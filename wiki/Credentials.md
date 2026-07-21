# Credentials — what every request must send

These values are **public client fields** reverse-engineered from Pixel Weather  
version `1.1.20260413.940319463.release`. They are **not** personal user secrets.

Print them anytime:

```bash
python -m google_weather credentials
# or after pip install -e .
google-weather credentials
```

REST proxy:

```bash
curl http://127.0.0.1:8787/v1/credentials
```

---

## Ready-to-copy headers

```http
X-Goog-Api-Key: AIzaSyCO1vbjEq1ZOZ1YKpksQY_MZuClk4acU_U
X-Android-Package: com.google.android.apps.weather
X-Android-Cert: fe96f0c14f56c8c0ce26a654576fd8829224ed49
pixel-weather-client-id: pixel-weather-mobile
Content-Type: application/grpc
te: trailers
```

| Header | Value | Source in app |
|--------|--------|----------------|
| `X-Goog-Api-Key` | `AIzaSyCO1vbjEq1ZOZ1YKpksQY_MZuClk4acU_U` | Phenotype flag `45460178` / DI `ApiKeyStrategy` |
| `X-Android-Package` | `com.google.android.apps.weather` | `context.getPackageName()` |
| `X-Android-Cert` | `fe96f0c14f56c8c0ce26a654576fd8829224ed49` | SHA-1 of signing cert (hex lowercase) |
| `pixel-weather-client-id` | `pixel-weather-mobile` | Hard-coded interceptor |

### Host

```text
pixelweatherhub-pa.googleapis.com
```

---

## Why package + cert are mandatory

Without them Google returns:

```text
grpc-status: 7
grpc-message: Requests from this Android client application <empty> are blocked.
```

Error reason: `API_KEY_ANDROID_APP_BLOCKED` for service `pixelweatherhub-pa.googleapis.com`.

The key is **Android app restricted**. Desktop clients work only when they **impersonate** the stock app identity via these two headers.

### How cert was obtained

```bash
apksigner verify --print-certs artifacts/apk/base.apk
# certificate SHA-1 digest → remove colons, lowercase
```

---

## What is NOT required for weather data

| Credential | Needed for weather? |
|------------|---------------------|
| Google account password | No |
| OAuth access token | **No** for forecast/location/AQI/pollen/maps |
| Zwieback cookie | No (observed optional analytics) |
| Device attestation beyond cert headers | Not required in our live probes |

---

## OAuth (only preferences)

Scope:

```text
https://www.googleapis.com/auth/pixelweatherhub
```

Header:

```http
Authorization: Bearer <your_token>
```

Without it, `UserPreferenceService/*` returns `grpc-status: 16`.

This project **does not ship user tokens**. Put your own token only if you obtained it legally for your account.

---

## Other keys found in APK (not primary weatherhub)

| Key / flag | Role |
|------------|------|
| `AIzaSyBL_7VqwthaBp5TRtRMDgQDQ4kpH4wDkQQ` (45730423) | Apex / LLM related host |
| `AIzaSyDgmW4ZMvNblSXqMOgsbY8uRrTnfR3E7pY` | mapsmobilesdks default |
| `AIzaSyCO1vbj…` (45460178) | **weatherhub** (this project) |

Use **CO1vbj** for weatherhub unless you are exploring Apex separately.

---

## Postman environment

Environment name: **Google Weather Open API**

| Variable | Default |
|----------|---------|
| `api_key` | `AIzaSyCO1vbjEq1ZOZ1YKpksQY_MZuClk4acU_U` |
| `android_package` | `com.google.android.apps.weather` |
| `android_cert` | `fe96f0c14f56c8c0ce26a654576fd8829224ed49` |
| `client_id` | `pixel-weather-mobile` |
| `host` | `pixelweatherhub-pa.googleapis.com` |
| `lat` / `lng` | `37.422` / `-122.084` |
| `lang` | `en-US` |
| `oauth_token` | empty |

These are pre-filled in the public Postman workspace.
