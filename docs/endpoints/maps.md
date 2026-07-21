# MapService

Host: `pixelweatherhub-pa.googleapis.com`  
Auth: API key + Android package/cert

## GetMapTileTemplate

```
POST /google.internal.android.pixel.weatherhub.v1.MapService/GetMapTileTemplate
```

### Request

| Field | # | Type | Notes |
|-------|---|------|-------|
| layer_type | 1 | enum | Values **1–4** return OK; 0 and 5+ fail |

### Response

- Template URL: `https://mt0.google.com/vt?bpb=`
- Additional binary tile parameters

Sample: `samples/responses/GetMapTileTemplate.bin`

## GetPrecipitationMapLayers

```
POST /google.internal.android.pixel.weatherhub.v1.MapService/GetPrecipitationMapLayers
```

### Request

| Field | # | Type |
|-------|---|------|
| location | 1 | LocationInput |

### Response

Large payload (~20 KB) including internal tile key paths and signed `ml:xs:c:` tokens for map tiles.

Sample: `samples/responses/GetPrecipitationMapLayers.bin`

## GetAirQualityMapLayers

See [air-quality.md](air-quality.md).

## Icons (static)

Base URLs from app:

- `https://www.gstatic.com/pixel-weather/icons/v1`
- `https://www.gstatic.com/pixel-weather/icons/v3_1` (when flag enabled)

Exact file names are not a stable open directory listing; icons are resolved from weather condition enums in the app resources / response data.
