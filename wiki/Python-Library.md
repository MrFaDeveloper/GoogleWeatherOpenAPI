# Python library

Package name: **`google-weather-open-api`**  
Import name: **`google_weather`**

## Install

```bash
cd GoogleWeatherOpenAPI
python3 -m pip install -e .
```

Zero third-party runtime dependencies. Transport uses system `curl --http2`.

## WeatherClient (recommended)

```python
from google_weather import WeatherClient

client = WeatherClient()

# JSON-friendly dicts — no gRPC knowledge needed
tz = client.get_timezone(37.422, -122.084)
print(tz["data"]["timezone"])  # America/Los_Angeles

name = client.get_location_name(37.422, -122.084)
print(name["data"]["display_name"], name["data"].get("place_id"))

weather = client.get_weather(37.422, -122.084, lang="en-US")
print(weather["ok"], weather["data"]["conditions_mentioned"][:5])
print(weather["summary_strings"][:15])

aqi = client.get_air_quality(37.422, -122.084)
pollen = client.get_pollen(37.422, -122.084)
maps = client.get_air_quality_map(37.422, -122.084)
tile = client.get_map_tile_template(layer=1)

# Show what headers will be sent
print(client.credentials_info())
```

### Method ↔ REST analogy

| Client method | Logical REST |
|---------------|--------------|
| `get_timezone` | `GET /v1/location/timezone` |
| `get_location_name` | `GET /v1/location/name` |
| `get_weather` | `GET /v1/weather` |
| `get_air_quality` | `GET /v1/air-quality` |
| `get_pollen` | `GET /v1/pollen` |
| `get_air_quality_map` | `GET /v1/maps/air-quality` |
| `get_precipitation_map` | `GET /v1/maps/precipitation` |
| `get_map_tile_template` | `GET /v1/maps/tile-template` |
| `list_preferred_locations` | `GET /v1/preferences/locations` (OAuth) |

### Response envelope

Every method returns:

```json
{
  "ok": true,
  "grpc_status": 0,
  "grpc_message": "",
  "method": "get_weather",
  "path": "/google.internal.../GetEssentialsWeather",
  "data": { "...parsed fields..." },
  "summary_strings": ["Sunny", "America/Los_Angeles", "..."],
  "raw_message_b64": null,
  "http": "HTTP/2 200"
}
```

Protobuf wire format is decoded best-effort into `data` + human strings. Full binary available with `WeatherClient(include_raw=True)`.

### Custom credentials

```python
from google_weather import WeatherClient, Credentials

c = WeatherClient(Credentials(
    api_key="AIzaSyCO1vbjEq1ZOZ1YKpksQY_MZuClk4acU_U",
    android_package="com.google.android.apps.weather",
    android_cert="fe96f0c14f56c8c0ce26a654576fd8829224ed49",
    client_id="pixel-weather-mobile",
    oauth_token=None,  # set only for preferences
))
```

## CLI

```bash
python -m google_weather credentials
python -m google_weather timezone --lat 55.75 --lng 37.62 --json
python -m google_weather weather --lat 37.422 --lng -122.084 --lang ru-RU --json
python -m google_weather aqi --lat 37.422 --lng -122.084 --json
python -m google_weather pollen --lat 37.422 --lng -122.084 --json
python -m google_weather map-tile --layer 1 --json
python -m google_weather serve --port 8787
```

Entry point after install: `google-weather` (same args).

## Layout in repo

```text
src/google_weather/
  client.py           # WeatherClient
  credentials.py      # DEFAULT_* and Credentials
  protobuf_codec.py   # encode/decode without protoc
  transport.py        # curl HTTP/2 gRPC
  rest_server.py      # local JSON REST
  cli.py
```

## Why not grpcio?

Shipping a zero-dep client that works with stock macOS `curl` is simpler for reverse-docs consumers. You can still use raw gRPC if you prefer; OpenAPI documents the wire paths.
