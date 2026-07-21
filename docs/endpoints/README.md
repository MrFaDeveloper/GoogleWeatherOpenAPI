# Endpoint index

All methods are gRPC unary RPCs on host `pixelweatherhub-pa.googleapis.com`.

Base path pattern:

```
POST /google.internal.android.pixel.weatherhub.v1.{Service}/{Method}
Content-Type: application/grpc
```

| Domain | Service | Methods | Auth |
|--------|---------|---------|------|
| [location](location.md) | LocationMetadataService | GetLocationTimeZone, GetLocationName, GetGeoAttributes | API key |
| [forecast](forecast.md) | WeatherBriefService | GetEssentialsWeather, GetEssentialsCurrentCondition, GetEssentialsForecast, GetWeatherAlert, GetNowcastAndInsights | API key |
| [air-quality](air-quality.md) | WeatherBriefService / MapService | GetAirQuality, GetAirQualityMapLayers | API key |
| [pollen](pollen.md) | PollenService | GetPollen | API key |
| [maps](maps.md) | MapService | GetMapTileTemplate, GetPrecipitationMapLayers, GetAirQualityMapLayers | API key |
| [blocks](blocks.md) | BlockConfigService, UserPreferenceService | QueryBlockConfigAvailability; List/Update weather block configs | API key / **OAuth** |
| [imagery](imagery.md) | ImageryService | ListImages, CreateImageRecords | API key |
| [preferences](preferences.md) | UserPreferenceService | Preferred locations CRUD | **OAuth only** |

Shared message: [common.md](common.md).
