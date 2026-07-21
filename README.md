# Google Weather Open API

Open documentation, **Python library**, and working clients for the **Google Pixel Weather** backend  
(`com.google.android.apps.weather` → **pixelweatherhub-pa.googleapis.com**).

This is **not** an official Google product. It is a reverse of the stock Pixel Weather client so anyone can call the same weather surface using only **public client fields** from the APK. The Python API is **REST-style** (JSON dicts / optional local HTTP proxy). Under the hood Google still speaks **gRPC**.

| | |
|--|--|
| **GitHub** | https://github.com/MrFaDeveloper/GoogleWeatherOpenAPI |
| **Wiki** | [`wiki/`](wiki/Home.md) (also published to GitHub Wiki) |
| **llms.txt** | [`llms.txt`](llms.txt) · full context [`llms-full.txt`](llms-full.txt) |
| **Postman workspace** | [Google Weather Open API](https://www.postman.com/altimetry-operator-52698115-s-team/workspace/google-weather-open-api/7f362113-7e78-4fce-88d2-6b76d9e15aeb) |
| **Postman EN** | [English collection](https://www.postman.com/altimetry-operator-52698115-s-team/workspace/google-weather-open-api/collection/036eb99c-d4aa-4f7a-8cb8-09bc13f7c52a) |
| **Postman RU** | [Русский collection](https://www.postman.com/altimetry-operator-52698115-s-team/workspace/google-weather-open-api/collection/b10cf0db-ebb5-4d46-9faa-1f1ea395d6a6) |
| **App reverse** | `1.1.20260413.940319463.release` (versionCode `10009163`) |

---

## Default credentials (copy-paste)

These are **shipped in the stock app** (Android-restricted API key). Not a user password.

```http
X-Goog-Api-Key: AIzaSyCO1vbjEq1ZOZ1YKpksQY_MZuClk4acU_U
X-Android-Package: com.google.android.apps.weather
X-Android-Cert: fe96f0c14f56c8c0ce26a654576fd8829224ed49
pixel-weather-client-id: pixel-weather-mobile
```

Host: `pixelweatherhub-pa.googleapis.com`

```bash
python -m google_weather credentials
```

Full explanation: [wiki/Credentials.md](wiki/Credentials.md) · [docs/auth.md](docs/auth.md)

---

## Install Python library

```bash
git clone https://github.com/MrFaDeveloper/GoogleWeatherOpenAPI.git
cd GoogleWeatherOpenAPI
python3 -m pip install -e .
```

### Code (no gRPC knowledge)

```python
from google_weather import WeatherClient

client = WeatherClient()  # uses default public headers
print(client.get_timezone(37.422, -122.084)["data"]["timezone"])
# America/Los_Angeles

w = client.get_weather(37.422, -122.084, lang="en-US")
print(w["ok"], w["data"].get("conditions_mentioned", [])[:5])
print(w["summary_strings"][:10])
```

### CLI

```bash
python -m google_weather timezone --lat 37.422 --lng -122.084 --json
python -m google_weather weather --lat 37.422 --lng -122.084 --lang en-US --json
python -m google_weather aqi --lat 37.422 --lng -122.084 --json
python -m google_weather pollen --lat 37.422 --lng -122.084 --json
```

### Local REST proxy (JSON for Postman/curl)

```bash
python -m google_weather serve --port 8787
curl -s 'http://127.0.0.1:8787/v1/credentials'
curl -s 'http://127.0.0.1:8787/v1/location/timezone?lat=37.422&lng=-122.084'
curl -s 'http://127.0.0.1:8787/v1/weather?lat=37.422&lng=-122.084&lang=en-US'
```

| REST path | What it does |
|-----------|----------------|
| `GET /v1/location/timezone` | IANA timezone |
| `GET /v1/location/name` | Place name + place id |
| `GET /v1/weather` | Essentials forecast brief |
| `GET /v1/air-quality` | AQI |
| `GET /v1/pollen` | Pollen |
| `GET /v1/maps/*` | Map layers / tile template |
| `GET /v1/credentials` | Shows headers in use |

Docs: [wiki/Python-Library.md](wiki/Python-Library.md) · [wiki/REST-Proxy.md](wiki/REST-Proxy.md)

---

## What works without a Google account

| Domain | RPC / method | Proven |
|--------|----------------|--------|
| Location | GetLocationTimeZone / `get_timezone` | Yes |
| Location | GetLocationName / `get_location_name` | Yes |
| Forecast | GetEssentialsWeather / `get_weather` | Yes (~37 KB) |
| Air quality | GetAirQuality / `get_air_quality` | Yes |
| Pollen | GetPollen / `get_pollen` | Yes |
| Maps | AQI + precip layers, tile template | Yes |
| Preferences | ListPreferredLocations | **OAuth only** (`grpc-status 16`) |

---

## Wiki

Full human docs in [`wiki/`](wiki/Home.md):

- [Home](wiki/Home.md)
- [Credentials](wiki/Credentials.md)
- [Quick Start](wiki/Quick-Start.md)
- [Python Library](wiki/Python-Library.md)
- [REST Proxy](wiki/REST-Proxy.md)
- [Endpoints](wiki/Endpoints.md)
- [Auth Walls](wiki/Auth-Walls.md)
- [Architecture](wiki/Architecture.md)
- [Postman](wiki/Postman.md)
- [Vibe Coders / LLMs](wiki/Vibe-Coders.md)
- [Troubleshooting](wiki/Troubleshooting.md)

---

## For AI agents (vibe coding)

```text
https://github.com/MrFaDeveloper/GoogleWeatherOpenAPI/blob/main/llms.txt
https://github.com/MrFaDeveloper/GoogleWeatherOpenAPI/blob/main/llms-full.txt
```

Follows the [llms.txt](https://llmstxt.org/) standard. See [wiki/Vibe-Coders.md](wiki/Vibe-Coders.md).

---

## OpenAPI / raw gRPC

- [openapi/openapi.yaml](openapi/openapi.yaml)
- [openapi/openapi.json](openapi/openapi.json)

OpenAPI models each unary RPC as `POST /package.Service/Method` with `application/grpc`. Prefer the Python client or REST proxy unless you need wire-level control.

---

## Postman

Environment **Google Weather Open API** already contains the real default API key + package + cert.

1. Open the public workspace link above.
2. Select the environment.
3. Run **Location → GetLocationTimeZone**.

Easier alternative: start `python -m google_weather serve` and call localhost JSON URLs from Postman.

Guides: [docs/postman-guide.md](docs/postman-guide.md) · [docs/postman-guide.ru.md](docs/postman-guide.ru.md)

---

## Repository layout

```text
src/google_weather/     Python package (WeatherClient, REST proxy, CLI)
wiki/                   Detailed wiki pages
llms.txt / llms-full.txt  LLM agent entrypoints
docs/                   Endpoint + auth guides
openapi/                OpenAPI 3
postman/                EN + RU collections + environment
examples/               quickstart.py
artifacts/              APK identity + hashes
samples/responses/      live binary captures
tests/
```

---

## How it was reversed

1. Pulled base + splits from a developer-owned rooted Android device.
2. Deep jadx decompile of weatherhub stubs.
3. Rebuilt protobuf requests from R8 field schemas.
4. Live-probed production with stock Android-restricted API key.

Notes: [wiki/Architecture.md](wiki/Architecture.md).

---

## Limits

- Not affiliated with Google. Respect [ToS](https://policies.google.com/terms).
- Message type names are R8-stripped; docs use reconstructed names + field numbers.
- Prefer rate-limiting your own tooling; shared client keys can be restricted by Google.

## License

MIT for code in this repository. APK artifacts come from a developer-owned device install.
