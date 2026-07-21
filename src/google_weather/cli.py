"""CLI: google-weather / python -m google_weather"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any, Optional

from . import __version__
from .client import WeatherClient
from .credentials import (
    Credentials,
    DEFAULT_API_KEY,
    DEFAULT_ANDROID_CERT,
    DEFAULT_ANDROID_PACKAGE,
    DEFAULT_CLIENT_ID,
    DEFAULT_HOST,
    print_credentials,
)


def _client(args: argparse.Namespace) -> WeatherClient:
    creds = Credentials(
        api_key=args.api_key,
        android_package=args.android_package,
        android_cert=args.android_cert,
        client_id=args.client_id,
        host=args.host,
        oauth_token=args.oauth_token or None,
    )
    return WeatherClient(creds, include_raw=getattr(args, "raw", False), raise_on_error=False)


def _print(obj: Any, as_json: bool) -> None:
    if as_json:
        print(json.dumps(obj, ensure_ascii=False, indent=2))
        return
    if not isinstance(obj, dict):
        print(obj)
        return
    print(f"ok={obj.get('ok')}  grpc_status={obj.get('grpc_status')}")
    if obj.get("grpc_message"):
        print(f"grpc_message={obj['grpc_message']}")
    data = obj.get("data") or {}
    for k, v in data.items():
        print(f"  {k}: {v}")
    strings = obj.get("summary_strings") or []
    if strings:
        print("strings:")
        for s in strings[:25]:
            print(f"  - {s}")


def _add_common(sp: argparse.ArgumentParser) -> None:
    sp.add_argument("--host", default=DEFAULT_HOST)
    sp.add_argument("--api-key", default=DEFAULT_API_KEY, help="X-Goog-Api-Key (public client key)")
    sp.add_argument("--android-package", default=DEFAULT_ANDROID_PACKAGE)
    sp.add_argument("--android-cert", default=DEFAULT_ANDROID_CERT, help="SHA-1 hex of app cert")
    sp.add_argument("--client-id", default=DEFAULT_CLIENT_ID)
    sp.add_argument("--oauth-token", default="", help="Bearer token for preferences only")
    sp.add_argument("--json", action="store_true", help="print full JSON")
    sp.add_argument("--raw", action="store_true", help="include base64 raw protobuf in JSON")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="google-weather",
        description="Google Weather Open API — REST-style CLI over Pixel Weather weatherhub gRPC",
    )
    p.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("credentials", help="print default request identity / headers")
    _add_common(sp)

    def add_ll(name: str, help_: str) -> argparse.ArgumentParser:
        sp_ = sub.add_parser(name, help=help_)
        _add_common(sp_)
        sp_.add_argument("--lat", type=float, required=True)
        sp_.add_argument("--lng", type=float, required=True)
        return sp_

    add_ll("timezone", "GetLocationTimeZone")
    add_ll("location-name", "GetLocationName")
    sp = add_ll("weather", "GetEssentialsWeather")
    sp.add_argument("--lang", default="en-US")
    sp.add_argument("--unit", type=int, default=1)
    sp = add_ll("aqi", "GetAirQuality")
    sp.add_argument("--lang", default="en-US")
    sp = add_ll("pollen", "GetPollen")
    sp.add_argument("--lang", default="en-US")
    sp = add_ll("aqi-map", "GetAirQualityMapLayers")
    sp.add_argument("--lang", default="en-US")
    add_ll("precip-map", "GetPrecipitationMapLayers")

    sp = sub.add_parser("map-tile", help="GetMapTileTemplate")
    _add_common(sp)
    sp.add_argument("--layer", type=int, default=1)

    sp = sub.add_parser("preferences", help="ListPreferredLocations (needs OAuth)")
    _add_common(sp)

    sp = sub.add_parser("serve", help="run local JSON REST proxy")
    _add_common(sp)
    sp.add_argument("--bind", default="127.0.0.1")
    sp.add_argument("--port", type=int, default=8787)

    return p


def main(argv: Optional[list] = None) -> int:
    args = build_parser().parse_args(argv)
    if args.cmd == "credentials":
        print_credentials(
            Credentials(
                api_key=args.api_key,
                android_package=args.android_package,
                android_cert=args.android_cert,
                client_id=args.client_id,
                host=args.host,
                oauth_token=args.oauth_token or None,
            )
        )
        return 0

    if args.cmd == "serve":
        from .rest_server import serve

        serve(
            host=args.bind,
            port=args.port,
            credentials=Credentials(
                api_key=args.api_key,
                android_package=args.android_package,
                android_cert=args.android_cert,
                client_id=args.client_id,
                host=args.host,
                oauth_token=args.oauth_token or None,
            ),
        )
        return 0

    c = _client(args)
    j = bool(getattr(args, "json", False))
    if args.cmd == "timezone":
        _print(c.get_timezone(args.lat, args.lng), j)
    elif args.cmd == "location-name":
        _print(c.get_location_name(args.lat, args.lng), j)
    elif args.cmd == "weather":
        _print(c.get_weather(args.lat, args.lng, lang=args.lang, unit=args.unit), j)
    elif args.cmd == "aqi":
        _print(c.get_air_quality(args.lat, args.lng, lang=args.lang), j)
    elif args.cmd == "pollen":
        _print(c.get_pollen(args.lat, args.lng, lang=args.lang), j)
    elif args.cmd == "aqi-map":
        _print(c.get_air_quality_map(args.lat, args.lng, lang=args.lang), j)
    elif args.cmd == "precip-map":
        _print(c.get_precipitation_map(args.lat, args.lng), j)
    elif args.cmd == "map-tile":
        _print(c.get_map_tile_template(args.layer), j)
    elif args.cmd == "preferences":
        _print(c.list_preferred_locations(), j)
    else:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
