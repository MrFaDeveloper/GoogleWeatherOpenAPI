# Authentication

## What you need for weather data (proven)

For LocationMetadata, WeatherBrief (essentials + AQI), Pollen, and MapService read RPCs, the stock client does **not** send a Google user OAuth token. It sends a **restricted Android API key** plus package identity headers.

| Header | Value | How to obtain |
|--------|-------|----------------|
| `X-Goog-Api-Key` | `AIzaSyCO1vbjEq1ZOZ1YKpksQY_MZuClk4acU_U` | Shipped in the APK as the default for phenotype flag `45460178` under package `com.google.android.apps.weather`. This is a public client field, not a user secret. |
| `X-Android-Package` | `com.google.android.apps.weather` | Fixed package name. |
| `X-Android-Cert` | `fe96f0c14f56c8c0ce26a654576fd8829224ed49` | SHA-1 fingerprint of the app signing certificate (lowercase hex, no colons). From this build: `apksigner verify --print-certs artifacts/apk/base.apk`. On a device: dump the package signature and SHA-1 digest of the cert DER. |
| `pixel-weather-client-id` | `pixel-weather-mobile` | Hard-coded in app (`api.server.b.B()`). |

### Recompute cert on a normal device

```bash
# From host, using the APK you pulled or installed
apksigner verify --print-certs path/to/base.apk
# Use "certificate SHA-1 digest" (lowercase, no separators)
```

Or with keytool after extracting the cert from the APK signature block.

### What fails without package/cert

```
grpc-status: 7
grpc-message: Requests from this Android client application <empty> are blocked.
```

Google Cloud error reason: `API_KEY_ANDROID_APP_BLOCKED` for service `pixelweatherhub-pa.googleapis.com`.

## What requires a Google session

### UserPreferenceService

Live call with the same API key headers:

```
grpc-status: 16
grpc-message: API keys are not supported by this API. Expected OAuth2 access token ...
```

Required:

```
Authorization: Bearer <oauth2_access_token>
```

- Scope: `https://www.googleapis.com/auth/pixelweatherhub`
- Source in app: GMS / TikTok account stack when the user has a Google account selected (not `pseudonymous`).
- How to take it from a normal device (for your own account only):
  1. Sign into Pixel Weather with a Google account.
  2. Capture traffic with a debug proxy that can decrypt the weather process (requires a debug/userdebug build or instrumented SSL unpin — **not** provided here).
  3. Or use official Google OAuth for a first-party app identity — **not available** to third parties as a public OAuth client for this scope.

This reverse does **not** invent or ship user tokens. OpenAPI marks preference endpoints as `oauth2` security; Postman leaves `oauth_token` empty.

### LlmService / Apex

Uses separate hosts and key flag `45730423` (`AIzaSyBL_...`) and may require additional session context. Not part of the proven least-auth weather contract.

## Pseudonymous / no-account mode

The app supports `pseudonymous` and `NoAccountEssentialsWeatherCache`. Forecast still hits weatherhub with the same API key strategy. Preferred-location sync is disabled without a Google account.

## Do not

- Paste third-party OAuth tokens into committed environments.
- Assume the API key works without Android package + cert headers.
- Treat the API key as a secret to hide from docs: it is already in every install of the app. Respect Google ToS and rate limits.
