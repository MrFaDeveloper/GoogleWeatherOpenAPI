# LocationMetadataService

Service: `google.internal.android.pixel.weatherhub.v1.LocationMetadataService`  
Host: `pixelweatherhub-pa.googleapis.com`  
Auth: API key + Android package/cert (no OAuth)

## GetLocationTimeZone

```
POST /google.internal.android.pixel.weatherhub.v1.LocationMetadataService/GetLocationTimeZone
```

### Request

| Field | # | Type | Required |
|-------|---|------|----------|
| lat_lng | 1 | LatLng | yes |

### Response

| Field | # | Type |
|-------|---|------|
| timezone_id | 1 | string (IANA) |

### Proven example

Coords `37.422, -122.084` → `America/Los_Angeles`  
Sample: `samples/responses/GetLocationTimeZone.bin`

```bash
python3 scripts/grpc_client.py timezone --lat 37.422 --lng -122.084
```

## GetLocationName

```
POST /google.internal.android.pixel.weatherhub.v1.LocationMetadataService/GetLocationName
```

### Request

| Field | # | Type | Required |
|-------|---|------|----------|
| lat_lng | 1 | LatLng | yes |
| accuracy_m | 4 | float | no |
| wifi_access_points | 5 | repeated message | no |

### Response

Nested place structure including:

- Localized place name (e.g. `Mountain View`)
- Region codes
- Google place id (`ChIJ...`)

Sample: `samples/responses/GetLocationName.bin`

## GetGeoAttributes

Registered on the service stub; same host/auth class. Not exercised with a live sample in this reverse beyond inventory.
