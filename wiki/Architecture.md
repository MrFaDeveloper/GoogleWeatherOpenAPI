# Architecture

## Stock app call path

```text
HomeActivity / WeatherBlocksFragment
  → EssentialsWeatherCacheAccessor
  → builds GetEssentialsWeatherRequest (LatLng + language)
  → WeatherBriefService gRPC stub
  → Google frameworks client + Cronet HTTP/2
  → pixelweatherhub-pa.googleapis.com
  → SqliteKeyValueCache (account or NoAccount*)
```

## This library

```text
Your code / curl / Postman
  → WeatherClient  or  REST proxy :8787
  → protobuf_codec (build request)
  → transport (curl --http2 application/grpc)
  → Google weatherhub
  → parse protobuf → JSON dict
```

## Why gRPC is hidden

Most consumers want:

```python
client.get_weather(lat, lng)
```

or

```http
GET /v1/weather?lat=...&lng=...
```

not length-prefixed protobuf frames. The library performs framing/unframing internally.

## Hosts

| Host | Role |
|------|------|
| `pixelweatherhub-pa.googleapis.com` | Production weatherhub |
| `pixelweatherhub-pa.mtls.googleapis.com` | mTLS variant |
| `staging-pixelweatherhub-pa.sandbox.googleapis.com` | Staging |
| `www.gstatic.com/pixel-weather/icons/*` | Icons CDN |
| `mt0.google.com` | Map tiles from template |

See also endpoint docs and Credentials wiki.
