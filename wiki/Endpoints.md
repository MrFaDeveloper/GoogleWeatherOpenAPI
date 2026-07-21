# Endpoints reference

Host: **`pixelweatherhub-pa.googleapis.com`**  
Wire: gRPC unary, `Content-Type: application/grpc`  
Library: use `WeatherClient` / REST proxy instead of hand-rolling frames.

Package prefix:

```text
google.internal.android.pixel.weatherhub.v1
```

---

## LocationMetadataService

### GetLocationTimeZone

- Path: `/...LocationMetadataService/GetLocationTimeZone`
- Auth: API key headers
- Request: `LatLng` field 1
- Response: string timezone field 1
- Python: `client.get_timezone(lat, lng)`
- REST: `GET /v1/location/timezone?lat=&lng=`
- Sample: Mountain View → `America/Los_Angeles`

### GetLocationName

- Request: `LatLng` field 1 (+ optional accuracy / Wi-Fi)
- Response: nested place names + place id (`ChIJ…`)
- Python: `client.get_location_name(lat, lng)`
- REST: `GET /v1/location/name?lat=&lng=`

### GetGeoAttributes

Registered on service; same auth class. See decompiled stubs for full fields.

---

## WeatherBriefService

### GetEssentialsWeather ⭐ primary

- Request: LocationInput (1), temperature unit enum (2), language (3)
- Response: large message — current + forecast series + insights
- Python: `client.get_weather(lat, lng, lang="en-US", unit=1)`
- REST: `GET /v1/weather?lat=&lng=&lang=&unit=`

Also registered: `GetEssentialsCurrentCondition`, `GetEssentialsForecast`, `GetWeatherAlert`, `GetNowcastAndInsights` — essentials covers UI home path.

### GetAirQuality

- Request: LatLng (1), language (5)
- Python: `client.get_air_quality`
- REST: `GET /v1/air-quality`

---

## PollenService

### GetPollen

- Request: LocationInput (1), language (6)
- Python: `client.get_pollen`
- REST: `GET /v1/pollen`

---

## MapService

### GetAirQualityMapLayers

- LocationInput + language
- Layer id often `air-quality-heatmap`

### GetPrecipitationMapLayers

- LocationInput
- Large tile key payload

### GetMapTileTemplate

- Enum layer type field 1 (values **1–4** OK)
- Returns `https://mt0.google.com/vt?bpb=`

---

## BlockConfigService / ImageryService / LlmService

Inventoried in OpenAPI and analysis notes. Prefer live samples in `samples/responses/` where present.

---

## UserPreferenceService (OAuth)

Create/List/Update/Delete preferred locations and weather block configs.

Without `Authorization: Bearer …`:

```text
grpc-status: 16
API keys are not supported by this API.
```

---

## OpenAPI

Machine-readable list of all operations:

- [`openapi/openapi.yaml`](../openapi/openapi.yaml)
- [`openapi/openapi.json`](../openapi/openapi.json)
