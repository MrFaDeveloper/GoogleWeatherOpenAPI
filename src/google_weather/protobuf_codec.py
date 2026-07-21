"""Minimal protobuf encode/decode helpers (no external protoc dependency)."""

from __future__ import annotations

import struct
from typing import Any, Dict, List, Optional, Tuple


def encode_varint(n: int) -> bytes:
    out = bytearray()
    n = int(n)
    if n < 0:
        # zig-zag not used for our enums; force unsigned treatment
        n &= (1 << 64) - 1
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
    """LatLng { float latitude = 1; float longitude = 2; }"""
    return encode_float(1, lat) + encode_float(2, lng)


def encode_location_input(lat: float, lng: float) -> bytes:
    """LocationInput minimal: field 1 = LatLng."""
    return encode_len(1, encode_latlng(lat, lng))


def grpc_frame(payload: bytes) -> bytes:
    return b"\x00" + struct.pack(">I", len(payload)) + payload


def parse_grpc_frame(data: bytes) -> Tuple[Optional[bytes], Dict[str, Any]]:
    meta: Dict[str, Any] = {"raw_len": len(data) if data else 0}
    if not data or len(data) < 5:
        return None, meta
    meta["compressed"] = data[0]
    plen = struct.unpack(">I", data[1:5])[0]
    meta["message_len"] = plen
    msg = data[5 : 5 + plen]
    return msg, meta


def decode_varint(buf: bytes, i: int) -> Tuple[int, int]:
    shift = 0
    result = 0
    while i < len(buf):
        b = buf[i]
        i += 1
        result |= (b & 0x7F) << shift
        if not (b & 0x80):
            return result, i
        shift += 7
        if shift > 63:
            raise ValueError("varint too long")
    raise ValueError("truncated varint")


def decode_fields(buf: bytes) -> List[Tuple[int, int, Any]]:
    """Return list of (field_number, wire_type, value).

    Values:
      wire 0: int
      wire 1: 8-byte raw
      wire 2: bytes
      wire 5: float (decoded)
    """
    out: List[Tuple[int, int, Any]] = []
    i = 0
    n = len(buf)
    while i < n:
        key, i = decode_varint(buf, i)
        field = key >> 3
        wire = key & 7
        if wire == 0:
            val, i = decode_varint(buf, i)
            out.append((field, wire, val))
        elif wire == 1:
            val = buf[i : i + 8]
            i += 8
            out.append((field, wire, val))
        elif wire == 2:
            length, i = decode_varint(buf, i)
            val = buf[i : i + length]
            i += length
            out.append((field, wire, val))
        elif wire == 5:
            val = struct.unpack("<f", buf[i : i + 4])[0]
            i += 4
            out.append((field, wire, val))
        else:
            # skip unknown wire
            break
    return out


def first_string_field(buf: bytes, field_no: int = 1) -> Optional[str]:
    for f, wire, val in decode_fields(buf):
        if f == field_no and wire == 2 and isinstance(val, (bytes, bytearray)):
            try:
                return val.decode("utf-8")
            except UnicodeDecodeError:
                return None
    return None


def extract_strings(buf: bytes, min_len: int = 4) -> List[str]:
    out: List[str] = []
    cur: List[str] = []
    for b in buf:
        if 32 <= b < 127:
            cur.append(chr(b))
        else:
            if len(cur) >= min_len:
                out.append("".join(cur))
            cur = []
    if len(cur) >= min_len:
        out.append("".join(cur))
    return out


# ---- request builders (match proven reverse) --------------------------------


def req_get_location_timezone(lat: float, lng: float) -> bytes:
    return encode_len(1, encode_latlng(lat, lng))


def req_get_location_name(lat: float, lng: float) -> bytes:
    return encode_len(1, encode_latlng(lat, lng))


def req_get_essentials_weather(
    lat: float, lng: float, lang: str = "en-US", unit: int = 1
) -> bytes:
    return (
        encode_len(1, encode_location_input(lat, lng))
        + encode_enum(2, unit)
        + encode_string(3, lang)
    )


def req_get_air_quality(lat: float, lng: float, lang: str = "en-US") -> bytes:
    return encode_len(1, encode_latlng(lat, lng)) + encode_string(5, lang)


def req_get_pollen(lat: float, lng: float, lang: str = "en-US") -> bytes:
    return encode_len(1, encode_location_input(lat, lng)) + encode_string(6, lang)


def req_get_aqi_map_layers(lat: float, lng: float, lang: str = "en-US") -> bytes:
    return encode_len(1, encode_location_input(lat, lng)) + encode_string(2, lang)


def req_get_precip_map_layers(lat: float, lng: float) -> bytes:
    return encode_len(1, encode_location_input(lat, lng))


def req_get_map_tile_template(layer: int = 1) -> bytes:
    return encode_enum(1, layer)


def req_empty() -> bytes:
    return b""
