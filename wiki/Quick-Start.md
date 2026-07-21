# Quick start

## 1) Clone & install

```bash
git clone https://github.com/MrFaDeveloper/GoogleWeatherOpenAPI.git
cd GoogleWeatherOpenAPI
python3 -m pip install -e .
```

Requires: Python 3.9+, `curl` with HTTP/2 support (macOS/Homebrew curl is fine).

## 2) Show credentials

```bash
python -m google_weather credentials
```

You should see the API key, package, cert, and client-id.

## 3) First RPC (timezone)

```bash
python -m google_weather timezone --lat 37.422 --lng -122.084 --json
```

Expected:

```json
{
  "ok": true,
  "grpc_status": 0,
  "data": { "timezone": "America/Los_Angeles" }
}
```

## 4) Weather brief

```bash
python -m google_weather weather --lat 37.422 --lng -122.084 --lang en-US --json
```

`summary_strings` will include condition phrases like `Sunny`, `Partly sunny`, etc.

## 5) Local REST (optional)

```bash
python -m google_weather serve --port 8787
# other terminal:
curl -s 'http://127.0.0.1:8787/v1/location/timezone?lat=37.422&lng=-122.084' | jq .
curl -s 'http://127.0.0.1:8787/v1/weather?lat=37.422&lng=-122.084&lang=en-US' | jq .
curl -s 'http://127.0.0.1:8787/v1/credentials' | jq .
```

## 6) Postman

Open the [public workspace](https://www.postman.com/altimetry-operator-52698115-s-team/workspace/google-weather-open-api/7f362113-7e78-4fce-88d2-6b76d9e15aeb), select environment **Google Weather Open API**, run **Location → GetLocationTimeZone**.

Or use the REST proxy + Postman against `http://127.0.0.1:8787` for pure JSON (easier than raw gRPC in the GUI).
