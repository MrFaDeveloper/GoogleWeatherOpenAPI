"""Optional local REST proxy so you can use curl/Postman JSON against localhost.

Starts a tiny HTTP server (stdlib only) that maps REST paths to WeatherClient.

Endpoints::

    GET /health
    GET /v1/credentials
    GET /v1/location/timezone?lat=&lng=
    GET /v1/location/name?lat=&lng=
    GET /v1/weather?lat=&lng=&lang=&unit=
    GET /v1/air-quality?lat=&lng=&lang=
    GET /v1/pollen?lat=&lng=&lang=
    GET /v1/maps/air-quality?lat=&lng=&lang=
    GET /v1/maps/precipitation?lat=&lng=
    GET /v1/maps/tile-template?layer=
    GET /v1/preferences/locations

All JSON. No gRPC knowledge required on the client side.
"""

from __future__ import annotations

import json
import re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Callable, Dict, Optional, Tuple
from urllib.parse import parse_qs, urlparse

from .client import WeatherClient
from .credentials import DEFAULT_CREDENTIALS, Credentials


def _json_response(handler: BaseHTTPRequestHandler, code: int, obj: dict) -> None:
    body = json.dumps(obj, ensure_ascii=False, indent=2).encode("utf-8")
    handler.send_response(code)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.send_header("Access-Control-Allow-Origin", "*")
    handler.end_headers()
    handler.wfile.write(body)


def make_handler(client: WeatherClient) -> type:
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, fmt: str, *args) -> None:  # quieter
            print("[rest]", self.address_string(), fmt % args)

        def do_OPTIONS(self) -> None:  # noqa: N802
            self.send_response(204)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")
            self.end_headers()

        def do_GET(self) -> None:  # noqa: N802
            parsed = urlparse(self.path)
            path = parsed.path.rstrip("/") or "/"
            q = {k: v[0] for k, v in parse_qs(parsed.query).items()}

            try:
                if path in ("/", "/health"):
                    return _json_response(
                        self,
                        200,
                        {
                            "ok": True,
                            "service": "Google Weather Open API REST proxy",
                            "docs": "https://github.com/MrFaDeveloper/GoogleWeatherOpenAPI",
                            "endpoints": [
                                "GET /v1/credentials",
                                "GET /v1/location/timezone?lat=&lng=",
                                "GET /v1/location/name?lat=&lng=",
                                "GET /v1/weather?lat=&lng=&lang=&unit=",
                                "GET /v1/air-quality?lat=&lng=&lang=",
                                "GET /v1/pollen?lat=&lng=&lang=",
                                "GET /v1/maps/air-quality?lat=&lng=&lang=",
                                "GET /v1/maps/precipitation?lat=&lng=",
                                "GET /v1/maps/tile-template?layer=",
                                "GET /v1/preferences/locations",
                            ],
                        },
                    )

                if path == "/v1/credentials":
                    return _json_response(self, 200, {"credentials": client.credentials_info()})

                def need_lat_lng() -> Tuple[float, float]:
                    if "lat" not in q or "lng" not in q:
                        raise ValueError("query params lat and lng are required")
                    return float(q["lat"]), float(q["lng"])

                if path == "/v1/location/timezone":
                    lat, lng = need_lat_lng()
                    return _json_response(self, 200, client.get_timezone(lat, lng))

                if path == "/v1/location/name":
                    lat, lng = need_lat_lng()
                    return _json_response(self, 200, client.get_location_name(lat, lng))

                if path == "/v1/weather":
                    lat, lng = need_lat_lng()
                    lang = q.get("lang", "en-US")
                    unit = int(q.get("unit", "1"))
                    return _json_response(
                        self, 200, client.get_weather(lat, lng, lang=lang, unit=unit)
                    )

                if path == "/v1/air-quality":
                    lat, lng = need_lat_lng()
                    return _json_response(
                        self,
                        200,
                        client.get_air_quality(lat, lng, lang=q.get("lang", "en-US")),
                    )

                if path == "/v1/pollen":
                    lat, lng = need_lat_lng()
                    return _json_response(
                        self,
                        200,
                        client.get_pollen(lat, lng, lang=q.get("lang", "en-US")),
                    )

                if path == "/v1/maps/air-quality":
                    lat, lng = need_lat_lng()
                    return _json_response(
                        self,
                        200,
                        client.get_air_quality_map(lat, lng, lang=q.get("lang", "en-US")),
                    )

                if path == "/v1/maps/precipitation":
                    lat, lng = need_lat_lng()
                    return _json_response(self, 200, client.get_precipitation_map(lat, lng))

                if path == "/v1/maps/tile-template":
                    layer = int(q.get("layer", "1"))
                    return _json_response(self, 200, client.get_map_tile_template(layer))

                if path == "/v1/preferences/locations":
                    return _json_response(self, 200, client.list_preferred_locations())

                return _json_response(self, 404, {"ok": False, "error": f"unknown path {path}"})
            except ValueError as e:
                return _json_response(self, 400, {"ok": False, "error": str(e)})
            except Exception as e:  # noqa: BLE001
                return _json_response(self, 500, {"ok": False, "error": str(e)})

    return Handler


def serve(
    host: str = "127.0.0.1",
    port: int = 8787,
    credentials: Optional[Credentials] = None,
) -> None:
    client = WeatherClient(credentials or DEFAULT_CREDENTIALS)
    handler = make_handler(client)
    httpd = ThreadingHTTPServer((host, port), handler)
    print(f"Google Weather Open API REST proxy on http://{host}:{port}")
    print(f"  try: curl 'http://{host}:{port}/v1/location/timezone?lat=37.422&lng=-122.084'")
    print(f"  credentials: http://{host}:{port}/v1/credentials")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped")
