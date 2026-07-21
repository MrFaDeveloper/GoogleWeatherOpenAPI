# Local REST proxy

Makes the API feel like a normal REST service. Under the hood it still calls Google weatherhub gRPC with the stock client headers.

## Start

```bash
python -m pip install -e .
python -m google_weather serve --bind 127.0.0.1 --port 8787
```

## Endpoints

| Method | Path | Query |
|--------|------|-------|
| GET | `/health` | — |
| GET | `/v1/credentials` | — |
| GET | `/v1/location/timezone` | `lat`, `lng` |
| GET | `/v1/location/name` | `lat`, `lng` |
| GET | `/v1/weather` | `lat`, `lng`, `lang?`, `unit?` |
| GET | `/v1/air-quality` | `lat`, `lng`, `lang?` |
| GET | `/v1/pollen` | `lat`, `lng`, `lang?` |
| GET | `/v1/maps/air-quality` | `lat`, `lng`, `lang?` |
| GET | `/v1/maps/precipitation` | `lat`, `lng` |
| GET | `/v1/maps/tile-template` | `layer?` |
| GET | `/v1/preferences/locations` | — (OAuth wall) |

## Examples

```bash
curl -s 'http://127.0.0.1:8787/v1/credentials' | jq .

curl -s 'http://127.0.0.1:8787/v1/location/timezone?lat=37.422&lng=-122.084' | jq .

curl -s 'http://127.0.0.1:8787/v1/weather?lat=37.422&lng=-122.084&lang=en-US' | jq '.data.conditions_mentioned'

curl -s 'http://127.0.0.1:8787/v1/air-quality?lat=37.422&lng=-122.084' | jq .

curl -s 'http://127.0.0.1:8787/v1/pollen?lat=55.75&lng=37.62&lang=ru-RU' | jq .
```

## Postman against localhost

Create a new Postman request:

- Method: GET  
- URL: `http://127.0.0.1:8787/v1/weather?lat={{lat}}&lng={{lng}}&lang={{lang}}`  
- No gRPC headers needed — the proxy adds them server-side.

This is the easiest path for teams who refuse binary gRPC in the GUI.

## CORS

The proxy sends `Access-Control-Allow-Origin: *` for simple browser demos. Do not expose it unauthenticated on a public network — it will burn Google quota with your shared client key.
