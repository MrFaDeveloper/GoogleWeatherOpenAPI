# Postman

## Public workspace

**[Google Weather Open API](https://www.postman.com/altimetry-operator-52698115-s-team/workspace/google-weather-open-api/7f362113-7e78-4fce-88d2-6b76d9e15aeb)**

| Collection | Link |
|------------|------|
| English | https://www.postman.com/altimetry-operator-52698115-s-team/workspace/google-weather-open-api/collection/036eb99c-d4aa-4f7a-8cb8-09bc13f7c52a |
| Русский | https://www.postman.com/altimetry-operator-52698115-s-team/workspace/google-weather-open-api/collection/b10cf0db-ebb5-4d46-9faa-1f1ea395d6a6 |

Environment **Google Weather Open API** ships with the real default headers filled in:

- `api_key` = `AIzaSyCO1vbjEq1ZOZ1YKpksQY_MZuClk4acU_U`
- `android_package` = `com.google.android.apps.weather`
- `android_cert` = `fe96f0c14f56c8c0ce26a654576fd8829224ed49`
- `client_id` = `pixel-weather-mobile`

## Recommended flows

### A) Raw gRPC collection (public workspace)

1. Select environment.
2. Run **Location → GetLocationTimeZone** (pre-request builds protobuf).
3. Expect `grpc-status: 0`.

Binary bodies are finicky in some Postman builds. Prefer Desktop + HTTP/2.

### B) Local REST proxy (easiest for teams)

```bash
python -m google_weather serve --port 8787
```

Then Postman GET:

```text
http://127.0.0.1:8787/v1/weather?lat=37.422&lng=-122.084&lang=en-US
```

No special headers — JSON in, JSON out.

## Offline import

Files under `postman/` in the GitHub repo.

Guides: [docs/postman-guide.md](../docs/postman-guide.md), [docs/postman-guide.ru.md](../docs/postman-guide.ru.md).
