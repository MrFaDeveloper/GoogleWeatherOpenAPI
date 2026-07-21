"""Public client credentials used by stock Pixel Weather.

These are **not user secrets**. They are Android-app-restricted API key
fields shipped inside ``com.google.android.apps.weather`` (phenotype flag
``45460178`` + signing cert SHA-1). Without package + cert headers Google
returns ``API_KEY_ANDROID_APP_BLOCKED``.

OAuth (Google account) is only required for UserPreferenceService
(saved places / block layout sync), not for forecast/location/AQI/pollen/maps.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Dict, Mapping, Optional


# ---------------------------------------------------------------------------
# Defaults reverse-engineered from Pixel Weather
# 1.1.20260413.940319463.release (versionCode 10009163)
# ---------------------------------------------------------------------------

DEFAULT_HOST = "pixelweatherhub-pa.googleapis.com"

# Phenotype / DI default for weatherhub (flag 45460178)
DEFAULT_API_KEY = "AIzaSyCO1vbjEq1ZOZ1YKpksQY_MZuClk4acU_U"

DEFAULT_ANDROID_PACKAGE = "com.google.android.apps.weather"

# apksigner verify --print-certs on base.apk (SHA-1, lowercase, no colons)
DEFAULT_ANDROID_CERT = "fe96f0c14f56c8c0ce26a654576fd8829224ed49"

# Hard-coded in app: api.server.b.B()
DEFAULT_CLIENT_ID = "pixel-weather-mobile"

# Only needed for UserPreferenceService
OAUTH_SCOPE = "https://www.googleapis.com/auth/pixelweatherhub"


@dataclass(frozen=True)
class Credentials:
    """HTTP headers / identity for weatherhub calls."""

    api_key: str = DEFAULT_API_KEY
    android_package: str = DEFAULT_ANDROID_PACKAGE
    android_cert: str = DEFAULT_ANDROID_CERT
    client_id: str = DEFAULT_CLIENT_ID
    host: str = DEFAULT_HOST
    oauth_token: Optional[str] = None  # Bearer token; UserPreference only

    def headers(self) -> Dict[str, str]:
        h = {
            "Content-Type": "application/grpc",
            "te": "trailers",
            "X-Goog-Api-Key": self.api_key,
            "X-Android-Package": self.android_package,
            "X-Android-Cert": self.android_cert,
            "pixel-weather-client-id": self.client_id,
            "User-Agent": "google-weather-open-api/python",
        }
        if self.oauth_token:
            h["Authorization"] = f"Bearer {self.oauth_token}"
        return h

    def as_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def public_info(self) -> Mapping[str, str]:
        """Human-readable table of what is sent (token redacted)."""
        return {
            "host": self.host,
            "X-Goog-Api-Key": self.api_key,
            "X-Android-Package": self.android_package,
            "X-Android-Cert": self.android_cert,
            "pixel-weather-client-id": self.client_id,
            "Authorization": (
                f"Bearer <set, {len(self.oauth_token)} chars>"
                if self.oauth_token
                else "(not set — not needed for weather/location/AQI/pollen/maps)"
            ),
            "oauth_scope_if_needed": OAUTH_SCOPE,
        }


DEFAULT_CREDENTIALS = Credentials()


def print_credentials(creds: Credentials = DEFAULT_CREDENTIALS) -> None:
    """Print ready-to-copy request identity for users / docs."""
    print("Google Weather Open API — default client identity")
    print("=" * 56)
    for k, v in creds.public_info().items():
        print(f"  {k}: {v}")
    print()
    print("Copy-paste HTTP headers:")
    for k, v in creds.headers().items():
        if k in ("Content-Type", "te", "User-Agent"):
            continue
        print(f"  {k}: {v}")
