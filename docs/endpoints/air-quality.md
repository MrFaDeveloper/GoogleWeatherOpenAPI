# Air quality

## GetAirQuality (WeatherBriefService)

```
POST /google.internal.android.pixel.weatherhub.v1.WeatherBriefService/GetAirQuality
```

### Request

| Field | # | Type |
|-------|---|------|
| lat_lng | 1 | LatLng |
| language_code | 5 | string |

### Response (content proven live)

- Index name: `U.S. Air Quality Index` / `AQI`
- Categories: Good, Moderate, Unhealthy for sensitive groups, Unhealthy, Very unhealthy, Hazardous
- Educational copy for the AQI scale
- Hybrid NowCast / U.S. AQI notes for PM2.5, PM10, O3, CO, SO2, NO2

Sample: `samples/responses/GetAirQuality.bin`

## GetAirQualityMapLayers (MapService)

```
POST /google.internal.android.pixel.weatherhub.v1.MapService/GetAirQualityMapLayers
```

### Request

| Field | # | Type |
|-------|---|------|
| location | 1 | LocationInput |
| language_code | 2 | string |

### Response

- Layer id string: `air-quality-heatmap`
- Legend / category payloads similar to GetAirQuality

Sample: `samples/responses/GetAirQualityMapLayers.bin`
