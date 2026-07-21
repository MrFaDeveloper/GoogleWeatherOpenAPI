# UserPreferenceService

```
google.internal.android.pixel.weatherhub.v1.UserPreferenceService
```

## Methods

| Method | Purpose |
|--------|---------|
| CreatePreferredLocation | Save a place |
| DeletePreferredLocations | Remove places |
| ListPreferredLocations | List saved places |
| UpdatePreferredLocations | Reorder/update |
| CreateWeatherBlockConfigs | Block layout |
| ListWeatherBlockConfigsOrCreateDefault | Load layout |
| UpdateWeatherBlockConfigs | Update layout |
| DeleteWeatherBlockConfigs | Delete layout |
| OneOffOperation | Misc one-off ops |

## Auth wall (proven)

API key + Android headers alone:

```
grpc-status: 16
grpc-message: API keys are not supported by this API. Expected OAuth2 access token or other authentication credentials that assert a principal.
```

Required header:

```
Authorization: Bearer <token for scope https://www.googleapis.com/auth/pixelweatherhub>
```

How the stock app gets the token: signed-in Google account via GMS / TikTok auth (`AuthContext` type `google`). Pseudonymous/no-account mode cannot call these methods successfully.

See [../auth.md](../auth.md).
