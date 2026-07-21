# PollenService

```
POST /google.internal.android.pixel.weatherhub.v1.PollenService/GetPollen
```

Auth: API key + Android package/cert

### Request

| Field | # | Type |
|-------|---|------|
| location | 1 | LocationInput |
| (optional numeric) | 3 | fixed32/int |
| language_code | 6 | string |

### Response (live strings)

- Categories: `Weed`, `Tree`, `Grass`
- Risk labels: `None` (and higher levels when applicable)
- Species notes (e.g. Olive and Privet, Juniper, Cedar and Cypress)
- Seasonality and cross-allergy notes

Sample: `samples/responses/GetPollen.bin` (~9 KB)

```bash
python3 scripts/grpc_client.py pollen --lat 37.422 --lng -122.084 --lang en-US
```
