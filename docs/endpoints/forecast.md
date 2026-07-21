# Forecast / WeatherBriefService

Service: `google.internal.android.pixel.weatherhub.v1.WeatherBriefService`  
Auth: API key + Android package/cert

## GetEssentialsWeather

Primary home-screen payload: current conditions plus multi-hour / multi-day forecast content in one unary response.

```
POST /google.internal.android.pixel.weatherhub.v1.WeatherBriefService/GetEssentialsWeather
```

### Request

| Field | # | Type | Required | Notes |
|-------|---|------|----------|-------|
| location | 1 | LocationInput | yes | field 1 = LatLng is enough |
| temperature_unit | 2 | enum | recommended | value `1` proven |
| language_code | 3 | string | yes | e.g. `en-US` |

### Response (high level)

Field numbers from decompiled `u` message:

| Field | # | Type | Role |
|-------|---|------|------|
| items | 2 | repeated message | attribution / block items (e.g. "Google Weather") |
| current | 3 | message | current condition cluster |
| forecast_a | 4 | message (list wrapper) | hourly-like series |
| forecast_b | 5 | message (list wrapper) | daily-like series |
| extra | 6 | oneof/message | alerts / aux |
| more | 7 | message | |
| timestamp | 8 | google.protobuf.Timestamp | |

Decoded strings from live MV traffic include condition phrases (`Partly sunny`, `Sunny`, `Clear`), timezone `America/Los_Angeles`, and insight text such as `Cooling expected over the next 2 days`.

Sample: `samples/responses/GetEssentialsWeather.bin` (~37 KB)

```bash
python3 scripts/grpc_client.py weather --lat 37.422 --lng -122.084 --lang en-US
```

## Other WeatherBrief methods (registered)

| Method | Purpose |
|--------|---------|
| GetEssentialsCurrentCondition | Current only |
| GetEssentialsForecast | Forecast only |
| GetWeatherAlert | Alerts |
| GetNowcastAndInsights | Short-term precip / insights (also embedded in essentials) |

These share the same service host and API-key auth class. Essentials is the practical single call for UI blocks.
