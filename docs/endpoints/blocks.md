# Weather blocks / config

## BlockConfigService.QueryBlockConfigAvailability

```
POST /google.internal.android.pixel.weatherhub.v1.BlockConfigService/QueryBlockConfigAvailability
```

- Auth class: API key allowed
- Minimal LocationInput-only probe returned `grpc-status: 3 INVALID_ARGUMENT`
- Full request schema needs additional fields (not fully reconstructed to a working sample)

## UserPreferenceService block config methods

| Method | Auth |
|--------|------|
| ListWeatherBlockConfigsOrCreateDefault | **OAuth** |
| CreateWeatherBlockConfigs | **OAuth** |
| UpdateWeatherBlockConfigs | **OAuth** |
| DeleteWeatherBlockConfigs | **OAuth** |

These sync the user's reordered weather home blocks to Google account storage. Local defaults work offline / no-account without these RPCs.

See [preferences.md](preferences.md) and [../auth.md](../auth.md).
