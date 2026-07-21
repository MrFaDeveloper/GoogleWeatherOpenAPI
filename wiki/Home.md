# Google Weather Open API — Wiki

**Unofficial open client** for the network backend used by **Google Pixel Weather**.

| Item | Value |
|------|--------|
| GitHub | https://github.com/MrFaDeveloper/GoogleWeatherOpenAPI |
| Package | `google-weather-open-api` (Python) |
| Backend host | `pixelweatherhub-pa.googleapis.com` |
| App reverse | `com.google.android.apps.weather` **1.1.20260413.940319463.release** (vc **10009163**) |
| Official? | **No.** Community reverse for interoperability / research. |

---

## Start here

1. **[Credentials](Credentials.md)** — API key, Android package, cert, client-id (copy-paste)
2. **[Quick start](Quick-Start.md)** — first successful call in 30 seconds
3. **[Python library](Python-Library.md)** — `WeatherClient`, CLI, install
4. **[REST proxy](REST-Proxy.md)** — local `GET /v1/weather?...` JSON API
5. **[Endpoints](Endpoints.md)** — every RPC explained
6. **[Auth walls](Auth-Walls.md)** — what needs Google OAuth
7. **[Postman](Postman.md)** — public EN + RU collections
8. **[Architecture](Architecture.md)** — gRPC stack, call graph
9. **[Vibe coders](Vibe-Coders.md)** — Cursor / Claude / Copilot + `llms.txt`
10. **[Troubleshooting](Troubleshooting.md)**

---

## What “open API” means here

Google does **not** publish a public REST product for Pixel Weather. The stock app speaks **gRPC** to an internal package:

```text
google.internal.android.pixel.weatherhub.v1.*
```

This project:

1. Documents that surface honestly.
2. Ships **default public client headers** the APK already contains.
3. Gives you a **Python API that looks like REST** (methods return JSON dicts).
4. Optionally runs a **local REST HTTP server** so Postman/curl use JSON, not raw gRPC.

You still hit Google’s production host. You do not get an unrestricted free-for-all key without the Android app restriction headers.

---

## Capability matrix

| Feature | Works with default headers? | Notes |
|---------|----------------------------|--------|
| Timezone | Yes | Proven |
| Location name | Yes | Proven |
| Essentials weather | Yes | ~37 KB response |
| Air quality | Yes | Proven |
| Pollen | Yes | Proven |
| AQI / precip map layers | Yes | Proven |
| Map tile template | Yes | layer enum 1–4 |
| Saved locations / block sync | **No** | OAuth required (`grpc-status 16`) |

---

## Languages

| Resource | Language |
|----------|----------|
| README, wiki, OpenAPI | English (primary) |
| Postman RU collection | Russian descriptions |
| Postman EN collection | English descriptions |
| Chat process notes | may be RU; committed docs EN |

---

## License / ToS

Use at your own risk. Do not abuse Google services. Do not claim affiliation with Google.
