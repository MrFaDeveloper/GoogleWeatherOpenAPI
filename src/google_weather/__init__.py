"""Google Weather Open API — Python client for Pixel Weather weatherhub.

Hides gRPC framing. Call methods like a normal REST-style client and get
JSON-friendly dicts. Default credentials are the public Android-restricted
client fields reverse-engineered from com.google.android.apps.weather.

Quick start::

    from google_weather import WeatherClient, DEFAULT_CREDENTIALS

    client = WeatherClient()  # uses DEFAULT_CREDENTIALS
    print(client.get_timezone(37.422, -122.084))
    # {"timezone": "America/Los_Angeles", "grpc_status": 0, ...}

    weather = client.get_weather(37.422, -122.084, lang="en-US")
    print(weather["summary_strings"][:10])

See also: ``python -m google_weather --help`` and optional REST proxy
``python -m google_weather serve``.
"""

from .credentials import (
    DEFAULT_API_KEY,
    DEFAULT_ANDROID_CERT,
    DEFAULT_ANDROID_PACKAGE,
    DEFAULT_CLIENT_ID,
    DEFAULT_HOST,
    DEFAULT_CREDENTIALS,
    Credentials,
)
from .client import WeatherClient, WeatherError, WeatherResponse
from . import __version__ as _v

__version__ = _v.__version__

__all__ = [
    "WeatherClient",
    "WeatherError",
    "WeatherResponse",
    "Credentials",
    "DEFAULT_CREDENTIALS",
    "DEFAULT_API_KEY",
    "DEFAULT_ANDROID_CERT",
    "DEFAULT_ANDROID_PACKAGE",
    "DEFAULT_CLIENT_ID",
    "DEFAULT_HOST",
    "__version__",
]
