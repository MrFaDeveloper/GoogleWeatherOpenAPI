# Postman — import and first successful request

## Public workspace

Workspace name: **Google Weather Open API**

| Language | Collection |
|----------|------------|
| English | Google Weather Open API (English) |
| Russian | Google Weather Open API (Русский) |

Both collections are the same API surface; only descriptions/docs language differs.

## Import from GitHub

1. Open [GoogleWeatherOpenAPI](https://github.com/MrFaDeveloper/GoogleWeatherOpenAPI).
2. Postman → **Import**:
   - `postman/Google Weather Open API English.postman_collection.json` (or Russian)
   - `postman/Google Weather Open API.postman_environment.json`
3. Select environment **Google Weather Open API** in the top-right dropdown.

## First successful request

1. Folder **Location** → **GetLocationTimeZone**
2. Click **Send**
3. Expect:
   - HTTP `200`
   - trailer `grpc-status: 0`
   - timezone string in the protobuf body (`America/Los_Angeles` for default MV coords)

Defaults: `lat=37.422`, `lng=-122.084` (Mountain View).

## Environment variables

| Variable | Purpose |
|----------|---------|
| `host` | `pixelweatherhub-pa.googleapis.com` |
| `api_key` | public client key from the APK |
| `android_package` | `com.google.android.apps.weather` |
| `android_cert` | app signing cert SHA-1 |
| `client_id` | `pixel-weather-mobile` |
| `lat` / `lng` | coordinates |
| `lang` | language tag |
| `oauth_token` | empty by default — Preferences folder only |

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `Android client application <empty> are blocked` | set package + cert |
| HTML 404 | must use `Content-Type: application/grpc` |
| `grpc-status: 16` on weather | wrong folder (Preferences needs OAuth) |
| Empty body | use Postman Desktop (HTTP/2) or CLI |

## CLI fallback

```bash
python3 scripts/grpc_client.py timezone --lat 37.422 --lng -122.084
python3 scripts/grpc_client.py weather --lat 37.422 --lng -122.084 --lang en-US
```
