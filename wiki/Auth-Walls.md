# Auth walls

## Level 0 — nothing

Does not work. Host requires the Android-restricted API key headers.

## Level 1 — public client headers (default)

Works for:

- LocationMetadataService (timezone, name, …)
- WeatherBriefService (essentials, AQI, …)
- PollenService
- MapService read methods
- (API-key-allowed) BlockConfig / Imagery methods when body is valid

Headers: see [Credentials](Credentials.md).

## Level 2 — Google OAuth

Required for UserPreferenceService:

```text
scope: https://www.googleapis.com/auth/pixelweatherhub
header: Authorization: Bearer <token>
```

How the stock app gets it: signed-in Google account via GMS / TikTok account module (`AuthContext` type `google`). Pseudonymous mode cannot sync preferred locations.

This reverse does **not** provide a third-party OAuth client id for that scope.

## Level 3 — Apex / LLM

Separate hosts (`apex-apis-pa`, `pixelapex-pa`) and key flag `45730423`. Not part of the least-auth weather contract.
