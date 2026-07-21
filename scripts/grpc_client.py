#!/usr/bin/env python3
"""Minimal gRPC-over-HTTP/2 client for Pixel Weather (pixelweatherhub-pa).

Reproduces stock client headers:
  X-Goog-Api-Key          — public client key shipped in the APK (phenotype 45460178)
  X-Android-Package      — com.google.android.apps.weather
  X-Android-Cert         — SHA-1 of the app signing cert (hex, lowercase)
  pixel-weather-client-id — pixel-weather-mobile

No Google account / OAuth is required for WeatherBrief, LocationMetadata,
Pollen, or MapService read RPCs proven in this reverse. UserPreferenceService
requires OAuth scope https://www.googleapis.com/auth/pixelweatherhub.

Usage:
  python3 scripts/grpc_client.py timezone --lat 37.422 --lng -122.084
  python3 scripts/grpc_client.py location-name --lat 37.422 --lng -122.084
  python3 scripts/grpc_client.py weather --lat 37.422 --lng -122.084 --lang en-US
  python3 scripts/grpc_client.py aqi --lat 37.422 --lng -122.084 --lang en-US
  python3 scripts/grpc_client.py pollen --lat 37.422 --lng -122.084 --lang en-US
  python3 scripts/grpc_client.py aqi-map --lat 37.422 --lng -122.084 --lang en-US
  python3 scripts/grpc_client.py precip-map --lat 37.422 --lng -122.084
  python3 scripts/grpc_client.py map-tile --layer 1
"""

from __future__ import annotations

import argparse
import struct
import subprocess
import sys
from pathlib import Path
from typing import Iterable, List, Optional, Tuple

HOST = "pixelweatherhub-pa.googleapis.com"
PKG = "com.google.android.apps.weather"
# Public client API key embedded in com.google.android.apps.weather (default for flag 45460178).
API_KEY = "AIzaSyCO1vbjEq1ZOZ1YKpksQY_MZuClk4acU_U"
# SHA-1 of the Play/system signing cert for this package (apksigner --print-certs).
ANDROID_CERT_SHA1 = "fe96f0c14f56c8c0ce26a654576fd8829224ed49"
CLIENT_ID = "pixel-weather-mobile"


def encode_varint(n: int) -> bytes:
    out = bytearray()
    while True:
        b = n & 0x7F
        n >>= 7
        out.append(b | (0x80 if n else 0))
        if not n:
            break
    return bytes(out)


def encode_key(field: int, wire: int) -> bytes:
    return encode_varint((field << 3) | wire)


def encode_len(field: int, data: bytes) -> bytes:
    return encode_key(field, 2) + encode_varint(len(data)) + data


def encode_float(field: int, val: float) -> bytes:
    return encode_key(field, 5) + struct.pack("<f", float(val))


def encode_string(field: int, s: str) -> bytes:
    return encode_len(field, s.encode("utf-8"))


def encode_enum(field: int, val: int) -> bytes:
    return encode_key(field, 0) + encode_varint(val)


def encode_latlng(lat: float, lng: float) -> bytes:
    """type LatLng { float latitude = 1; float longitude = 2; }"""
    return encode_float(1, lat) + encode_float(2, lng)


def encode_location_input(lat: float, lng: float) -> bytes:
    """Shared location input used by weather / pollen / map requests.

    Reconstructed field layout (decompiled message `bf`):
      1: LatLng lat_lng
      2..4: optional strings (timezone / place / labels — optional for basic calls)
      5: enum
      6: optional string
      7..8: nested messages
    Minimal working form: field 1 only.
    """
    return encode_len(1, encode_latlng(lat, lng))


def grpc_frame(payload: bytes) -> bytes:
    return b"\x00" + struct.pack(">I", len(payload)) + payload


def parse_grpc_response(data: bytes) -> Tuple[Optional[bytes], dict]:
    meta = {}
    if not data or len(data) < 5:
        return None, meta
    compressed = data[0]
    plen = struct.unpack(">I", data[1:5])[0]
    msg = data[5 : 5 + plen]
    meta["compressed"] = compressed
    meta["length"] = plen
    return msg, meta


def extract_strings(msg: bytes, min_len: int = 4) -> List[str]:
    out: List[str] = []
    cur: List[str] = []
    for b in msg:
        if 32 <= b < 127:
            cur.append(chr(b))
        else:
            if len(cur) >= min_len:
                out.append("".join(cur))
            cur = []
    if len(cur) >= min_len:
        out.append("".join(cur))
    return out


def decode_string_field1(msg: bytes) -> Optional[str]:
    """Decode a protobuf message that is only `string field1 = 1`."""
    if not msg:
        return None
    i = 0
    # field 1, wire 2
    if msg[i] != 0x0A:
        # fall back to first length-delimited string
        return None
    i += 1
    length = 0
    shift = 0
    while i < len(msg):
        b = msg[i]
        i += 1
        length |= (b & 0x7F) << shift
        if not (b & 0x80):
            break
        shift += 7
    return msg[i : i + length].decode("utf-8", errors="replace")


def call_rpc(
    method_path: str,
    body: bytes,
    *,
    api_key: str = API_KEY,
    cert: str = ANDROID_CERT_SHA1,
    package: str = PKG,
    raw_out: Optional[Path] = None,
    timeout: int = 60,
) -> Tuple[int, dict, Optional[bytes]]:
    """POST gRPC request via curl (HTTP/2). Returns (http_code-ish, trailers, msg)."""
    import tempfile

    with tempfile.NamedTemporaryFile(delete=False) as reqf, tempfile.NamedTemporaryFile(
        delete=False
    ) as respf, tempfile.NamedTemporaryFile(delete=False, mode="w+") as hdrf:
        req_path, resp_path, hdr_path = reqf.name, respf.name, hdrf.name
        reqf.write(grpc_frame(body))

    cmd = [
        "curl",
        "-sS",
        "--http2",
        "-D",
        hdr_path,
        "-o",
        resp_path,
        "-X",
        "POST",
        f"https://{HOST}{method_path}",
        "-H",
        "Content-Type: application/grpc",
        "-H",
        "te: trailers",
        "-H",
        f"X-Goog-Api-Key: {api_key}",
        "-H",
        f"X-Android-Package: {package}",
        "-H",
        f"X-Android-Cert: {cert}",
        "-H",
        f"pixel-weather-client-id: {CLIENT_ID}",
        "--data-binary",
        f"@{req_path}",
        "--max-time",
        str(timeout),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    headers = Path(hdr_path).read_text(errors="replace")
    raw = Path(resp_path).read_bytes()
    Path(req_path).unlink(missing_ok=True)
    Path(hdr_path).unlink(missing_ok=True)
    if raw_out:
        raw_out.write_bytes(raw)
    else:
        Path(resp_path).unlink(missing_ok=True)

    trailers = {}
    for line in headers.splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            trailers[k.strip().lower()] = v.strip()
        elif line.startswith("HTTP/"):
            trailers["http_status_line"] = line

    if proc.returncode != 0 and "http_status_line" not in trailers:
        raise RuntimeError(f"curl failed ({proc.returncode}): {proc.stderr}")

    msg, meta = parse_grpc_response(raw)
    trailers.update({f"body_{k}": str(v) for k, v in meta.items()})
    status = int(trailers.get("grpc-status", "-1") or "-1")
    return status, trailers, msg


# --- request builders -------------------------------------------------------

def req_get_location_timezone(lat: float, lng: float) -> bytes:
    # GetLocationTimeZoneRequest { LatLng lat_lng = 1; }
    return encode_len(1, encode_latlng(lat, lng))


def req_get_location_name(lat: float, lng: float) -> bytes:
    # GetLocationNameRequest { LatLng lat_lng = 1; float accuracy_m = 4; repeated WifiAccessPoint = 5; }
    return encode_len(1, encode_latlng(lat, lng))


def req_get_essentials_weather(lat: float, lng: float, lang: str = "en-US", unit: int = 1) -> bytes:
    # GetEssentialsWeatherRequest {
    #   LocationInput location = 1;  // bf
    #   TemperatureUnit unit = 2;    // enum (1 works; exact names R8-stripped)
    #   string language_code = 3;
    # }
    return encode_len(1, encode_location_input(lat, lng)) + encode_enum(2, unit) + encode_string(3, lang)


def req_get_air_quality(lat: float, lng: float, lang: str = "en-US") -> bytes:
    # GetAirQualityRequest { LatLng lat_lng = 1; string language_code = 5; }
    return encode_len(1, encode_latlng(lat, lng)) + encode_string(5, lang)


def req_get_pollen(lat: float, lng: float, lang: str = "en-US") -> bytes:
    # GetPollenRequest { LocationInput location = 1; string language_code = 6; }
    return encode_len(1, encode_location_input(lat, lng)) + encode_string(6, lang)


def req_get_aqi_map_layers(lat: float, lng: float, lang: str = "en-US") -> bytes:
    # GetAirQualityMapLayersRequest { LocationInput location = 1; string language_code = 2; }
    return encode_len(1, encode_location_input(lat, lng)) + encode_string(2, lang)


def req_get_precip_map_layers(lat: float, lng: float) -> bytes:
    # GetPrecipitationMapLayersRequest { LocationInput location = 1; }
    return encode_len(1, encode_location_input(lat, lng))


def req_get_map_tile_template(layer_enum: int = 1) -> bytes:
    # GetMapTileTemplateRequest { MapLayerType type = 1; ... }
    return encode_enum(1, layer_enum)


RPCS = {
    "timezone": (
        "/google.internal.android.pixel.weatherhub.v1.LocationMetadataService/GetLocationTimeZone",
        req_get_location_timezone,
    ),
    "location-name": (
        "/google.internal.android.pixel.weatherhub.v1.LocationMetadataService/GetLocationName",
        req_get_location_name,
    ),
    "weather": (
        "/google.internal.android.pixel.weatherhub.v1.WeatherBriefService/GetEssentialsWeather",
        req_get_essentials_weather,
    ),
    "aqi": (
        "/google.internal.android.pixel.weatherhub.v1.WeatherBriefService/GetAirQuality",
        req_get_air_quality,
    ),
    "pollen": (
        "/google.internal.android.pixel.weatherhub.v1.PollenService/GetPollen",
        req_get_pollen,
    ),
    "aqi-map": (
        "/google.internal.android.pixel.weatherhub.v1.MapService/GetAirQualityMapLayers",
        req_get_aqi_map_layers,
    ),
    "precip-map": (
        "/google.internal.android.pixel.weatherhub.v1.MapService/GetPrecipitationMapLayers",
        req_get_precip_map_layers,
    ),
    "map-tile": (
        "/google.internal.android.pixel.weatherhub.v1.MapService/GetMapTileTemplate",
        req_get_map_tile_template,
    ),
}


def main(argv: Optional[Iterable[str]] = None) -> int:
    p = argparse.ArgumentParser(description="Pixel Weather weatherhub gRPC client")
    p.add_argument("rpc", choices=sorted(RPCS.keys()))
    p.add_argument("--lat", type=float, default=37.422)
    p.add_argument("--lng", type=float, default=-122.084)
    p.add_argument("--lang", default="en-US")
    p.add_argument("--unit", type=int, default=1, help="temperature unit enum (1 proven)")
    p.add_argument("--layer", type=int, default=1, help="map tile layer enum (1-4 proven)")
    p.add_argument("--api-key", default=API_KEY)
    p.add_argument("--cert", default=ANDROID_CERT_SHA1)
    p.add_argument("--raw", type=Path, help="write raw gRPC response body")
    p.add_argument("--quiet-strings", action="store_true")
    args = p.parse_args(list(argv) if argv is not None else None)

    path, builder = RPCS[args.rpc]
    if args.rpc == "map-tile":
        body = builder(args.layer)
    elif args.rpc in ("weather", "aqi", "pollen", "aqi-map"):
        if args.rpc == "weather":
            body = builder(args.lat, args.lng, args.lang, args.unit)
        else:
            body = builder(args.lat, args.lng, args.lang)
    elif args.rpc == "precip-map":
        body = builder(args.lat, args.lng)
    else:
        body = builder(args.lat, args.lng)

    status, trailers, msg = call_rpc(
        path, body, api_key=args.api_key, cert=args.cert, raw_out=args.raw
    )
    print(f"rpc: {args.rpc}")
    print(f"path: {path}")
    print(f"http: {trailers.get('http_status_line', '?')}")
    print(f"grpc-status: {status}")
    if "grpc-message" in trailers:
        print(f"grpc-message: {trailers['grpc-message']}")
    if msg is None:
        print("message: <empty>")
        return 1 if status != 0 else 0

    print(f"message_bytes: {len(msg)}")
    if args.rpc == "timezone":
        tz = decode_string_field1(msg)
        print(f"timezone: {tz}")
    if not args.quiet_strings:
        strings = extract_strings(msg)
        # Print a short, useful sample of decoded strings
        interesting = [s for s in strings if any(c.isalpha() for c in s)][:30]
        if interesting:
            print("strings:")
            for s in interesting:
                print(f"  - {s}")
    return 0 if status == 0 else 2


if __name__ == "__main__":
    sys.exit(main())
