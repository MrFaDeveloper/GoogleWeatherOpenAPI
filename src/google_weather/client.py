"""High-level WeatherClient — REST-like methods, JSON-friendly dicts."""

from __future__ import annotations

import base64
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from . import protobuf_codec as pb
from .credentials import Credentials, DEFAULT_CREDENTIALS
from .transport import TransportError, call_rpc

# Fully-qualified gRPC paths
P = {
    "timezone": "/google.internal.android.pixel.weatherhub.v1.LocationMetadataService/GetLocationTimeZone",
    "location_name": "/google.internal.android.pixel.weatherhub.v1.LocationMetadataService/GetLocationName",
    "weather": "/google.internal.android.pixel.weatherhub.v1.WeatherBriefService/GetEssentialsWeather",
    "aqi": "/google.internal.android.pixel.weatherhub.v1.WeatherBriefService/GetAirQuality",
    "pollen": "/google.internal.android.pixel.weatherhub.v1.PollenService/GetPollen",
    "aqi_map": "/google.internal.android.pixel.weatherhub.v1.MapService/GetAirQualityMapLayers",
    "precip_map": "/google.internal.android.pixel.weatherhub.v1.MapService/GetPrecipitationMapLayers",
    "map_tile": "/google.internal.android.pixel.weatherhub.v1.MapService/GetMapTileTemplate",
    "list_preferred": "/google.internal.android.pixel.weatherhub.v1.UserPreferenceService/ListPreferredLocations",
}


class WeatherError(RuntimeError):
    """Raised when grpc-status != 0 (optional; methods return dict by default)."""

    def __init__(self, status: int, message: str, detail: Optional[dict] = None):
        super().__init__(f"grpc-status={status}: {message}")
        self.status = status
        self.grpc_message = message
        self.detail = detail or {}


@dataclass
class WeatherResponse:
    """Normalized response envelope (dict-serializable)."""

    ok: bool
    grpc_status: int
    grpc_message: str = ""
    method: str = ""
    path: str = ""
    data: Dict[str, Any] = field(default_factory=dict)
    summary_strings: List[str] = field(default_factory=list)
    raw_message_b64: Optional[str] = None
    headers: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ok": self.ok,
            "grpc_status": self.grpc_status,
            "grpc_message": self.grpc_message,
            "method": self.method,
            "path": self.path,
            "data": self.data,
            "summary_strings": self.summary_strings,
            "raw_message_b64": self.raw_message_b64,
            "http": self.headers.get("http_status_line"),
        }


class WeatherClient:
    """Friendly client. You do not need to know gRPC.

    Example::

        c = WeatherClient()
        print(c.get_timezone(55.75, 37.62))   # Moscow
        w = c.get_weather(37.422, -122.084)
        print(w["summary_strings"][:15])
    """

    def __init__(
        self,
        credentials: Optional[Credentials] = None,
        *,
        include_raw: bool = False,
        raise_on_error: bool = False,
        timeout: int = 60,
    ):
        self.credentials = credentials or DEFAULT_CREDENTIALS
        self.include_raw = include_raw
        self.raise_on_error = raise_on_error
        self.timeout = timeout

    # ---- internal ---------------------------------------------------------

    def _call(
        self,
        method: str,
        path: str,
        body: bytes,
        parser,
    ) -> Dict[str, Any]:
        try:
            status, trailers, msg, raw = call_rpc(
                path, body, self.credentials, timeout=self.timeout
            )
        except TransportError as e:
            if self.raise_on_error:
                raise
            return {
                "ok": False,
                "grpc_status": -1,
                "grpc_message": str(e),
                "method": method,
                "path": path,
                "data": {},
                "summary_strings": [],
            }

        grpc_msg = trailers.get("grpc-message", "")
        data: Dict[str, Any] = {}
        strings: List[str] = []
        if msg:
            strings = pb.extract_strings(msg)
            try:
                data = parser(msg) if parser else {}
            except Exception as ex:  # noqa: BLE001
                data = {"parse_error": str(ex)}

        env = WeatherResponse(
            ok=status == 0,
            grpc_status=status,
            grpc_message=grpc_msg,
            method=method,
            path=path,
            data=data,
            summary_strings=strings[:80],
            raw_message_b64=base64.b64encode(msg).decode() if (self.include_raw and msg) else None,
            headers={k: v for k, v in trailers.items() if not k.startswith("body_")},
        )
        if self.raise_on_error and status != 0:
            raise WeatherError(status, grpc_msg or "RPC failed", env.to_dict())
        return env.to_dict()

    # ---- public REST-like API ---------------------------------------------

    def get_timezone(self, lat: float, lng: float) -> Dict[str, Any]:
        """IANA timezone for coordinates.

        REST analogy: ``GET /v1/location/timezone?lat=&lng=``
        """

        def parse(msg: bytes) -> Dict[str, Any]:
            tz = pb.first_string_field(msg, 1)
            return {"timezone": tz}

        return self._call(
            "get_timezone",
            P["timezone"],
            pb.req_get_location_timezone(lat, lng),
            parse,
        )

    def get_location_name(self, lat: float, lng: float) -> Dict[str, Any]:
        """Place name / place id for coordinates.

        REST analogy: ``GET /v1/location/name?lat=&lng=``
        """

        def parse(msg: bytes) -> Dict[str, Any]:
            strings = pb.extract_strings(msg, min_len=2)
            place_id = next((s for s in strings if s.startswith("ChIJ")), None)
            # first non-trivial alpha name often city
            names = [s for s in strings if s.isalpha() or " " in s]
            return {
                "place_id": place_id,
                "labels": names[:20],
                "display_name": names[0] if names else None,
            }

        return self._call(
            "get_location_name",
            P["location_name"],
            pb.req_get_location_name(lat, lng),
            parse,
        )

    def get_weather(
        self,
        lat: float,
        lng: float,
        *,
        lang: str = "en-US",
        unit: int = 1,
    ) -> Dict[str, Any]:
        """Full essentials weather brief (current + series).

        REST analogy: ``GET /v1/weather?lat=&lng=&lang=&unit=``
        """

        def parse(msg: bytes) -> Dict[str, Any]:
            strings = pb.extract_strings(msg)
            conditions = [
                s
                for s in strings
                if any(
                    w in s
                    for w in (
                        "Sunny",
                        "Clear",
                        "Cloud",
                        "Rain",
                        "Snow",
                        "Fog",
                        "Partly",
                        "Mostly",
                        "Overcast",
                        "Showers",
                        "Thunder",
                    )
                )
            ]
            return {
                "message_bytes": len(msg),
                "conditions_mentioned": conditions[:40],
                "timezone_guess": next(
                    (s for s in strings if "/" in s and s[0].isalpha() and " " not in s and len(s) < 40),
                    None,
                ),
                "attribution": next((s for s in strings if "Weather" in s), None),
            }

        return self._call(
            "get_weather",
            P["weather"],
            pb.req_get_essentials_weather(lat, lng, lang, unit),
            parse,
        )

    def get_air_quality(
        self, lat: float, lng: float, *, lang: str = "en-US"
    ) -> Dict[str, Any]:
        """Air quality index payload.

        REST analogy: ``GET /v1/air-quality?lat=&lng=&lang=``
        """

        def parse(msg: bytes) -> Dict[str, Any]:
            strings = pb.extract_strings(msg)
            cats = [
                s
                for s in strings
                if s
                in (
                    "Good",
                    "Moderate",
                    "Unhealthy",
                    "Hazardous",
                    "Unhealthy for sensitive groups",
                    "Very unhealthy",
                )
                or "air quality" in s.lower()
                or s == "AQI"
                or "Air Quality" in s
            ]
            return {"categories_and_labels": cats[:30], "message_bytes": len(msg)}

        return self._call(
            "get_air_quality",
            P["aqi"],
            pb.req_get_air_quality(lat, lng, lang),
            parse,
        )

    def get_pollen(
        self, lat: float, lng: float, *, lang: str = "en-US"
    ) -> Dict[str, Any]:
        """Pollen categories and notes.

        REST analogy: ``GET /v1/pollen?lat=&lng=&lang=``
        """

        def parse(msg: bytes) -> Dict[str, Any]:
            strings = pb.extract_strings(msg)
            types = [s for s in strings if s in ("Weed", "Tree", "Grass")]
            return {
                "types_seen": types,
                "notes": [s for s in strings if len(s) > 20][:25],
                "message_bytes": len(msg),
            }

        return self._call(
            "get_pollen",
            P["pollen"],
            pb.req_get_pollen(lat, lng, lang),
            parse,
        )

    def get_air_quality_map(
        self, lat: float, lng: float, *, lang: str = "en-US"
    ) -> Dict[str, Any]:
        """AQI heatmap layer metadata.

        REST analogy: ``GET /v1/maps/air-quality?lat=&lng=``
        """

        def parse(msg: bytes) -> Dict[str, Any]:
            strings = pb.extract_strings(msg)
            return {
                "layer_id": next(
                    (s for s in strings if "heatmap" in s or "air-quality" in s), None
                ),
                "labels": strings[:40],
                "message_bytes": len(msg),
            }

        return self._call(
            "get_air_quality_map",
            P["aqi_map"],
            pb.req_get_aqi_map_layers(lat, lng, lang),
            parse,
        )

    def get_precipitation_map(self, lat: float, lng: float) -> Dict[str, Any]:
        """Precipitation map layer keys.

        REST analogy: ``GET /v1/maps/precipitation?lat=&lng=``
        """

        def parse(msg: bytes) -> Dict[str, Any]:
            strings = pb.extract_strings(msg)
            return {
                "tile_paths": [s for s in strings if s.startswith("/") or "tile" in s.lower()][
                    :20
                ],
                "message_bytes": len(msg),
            }

        return self._call(
            "get_precipitation_map",
            P["precip_map"],
            pb.req_get_precip_map_layers(lat, lng),
            parse,
        )

    def get_map_tile_template(self, layer: int = 1) -> Dict[str, Any]:
        """Map tile URL template.

        REST analogy: ``GET /v1/maps/tile-template?layer=``
        """

        def parse(msg: bytes) -> Dict[str, Any]:
            strings = pb.extract_strings(msg)
            url = next((s for s in strings if s.startswith("http")), None)
            return {"template_url": url, "strings": strings[:10]}

        return self._call(
            "get_map_tile_template",
            P["map_tile"],
            pb.req_get_map_tile_template(layer),
            parse,
        )

    def list_preferred_locations(self) -> Dict[str, Any]:
        """Requires OAuth. Documents the auth wall when only API key is set.

        REST analogy: ``GET /v1/preferences/locations`` (401/UNAUTHENTICATED without token)
        """
        return self._call(
            "list_preferred_locations",
            P["list_preferred"],
            pb.req_empty(),
            lambda msg: {"raw_strings": pb.extract_strings(msg)},
        )

    def credentials_info(self) -> Dict[str, Any]:
        """Return the headers/identity this client will send (for docs/UI)."""
        return dict(self.credentials.public_info())
