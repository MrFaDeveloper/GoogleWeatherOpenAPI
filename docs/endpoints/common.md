# Common messages

## LatLng

| Field | # | Type | Description |
|-------|---|------|-------------|
| latitude | 1 | float | WGS84 latitude |
| longitude | 2 | float | WGS84 longitude |

Wire example (Mountain View): float bits for `37.422`, `-122.084`.

## LocationInput

Used by GetEssentialsWeather, GetPollen, map layer requests.

| Field | # | Type | Description |
|-------|---|------|-------------|
| lat_lng | 1 | LatLng | Required for minimal working requests |
| string fields | 2–4, 6 | string | Optional (timezone / place labels) |
| enum | 5 | enum | Optional |
| nested | 7–8 | message | Optional |

## Shared headers

See [../auth.md](../auth.md).

## gRPC status codes observed

| Code | Meaning in this API |
|------|---------------------|
| 0 | OK |
| 3 | INVALID_ARGUMENT (bad/incomplete body) |
| 7 | PERMISSION_DENIED (missing Android app restriction headers) |
| 13 | INTERNAL (e.g. unsupported map layer enum) |
| 16 | UNAUTHENTICATED (UserPreference without OAuth) |
