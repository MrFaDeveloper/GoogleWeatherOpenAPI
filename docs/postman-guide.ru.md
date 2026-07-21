# Postman — как импортировать и сделать первый успешный запрос

## Публичный workspace

Workspace: **Google Weather Open API**  
Внутри две одинаковые по смыслу коллекции:

| Язык | Коллекция |
|------|-----------|
| English | Google Weather Open API (English) |
| Русский | Google Weather Open API (Русский) |

Ссылки на workspace публикуются в README репозитория после создания.

## Импорт из GitHub

1. Откройте [репозиторий](https://github.com/MrFaDeveloper/GoogleWeatherOpenAPI).
2. Postman → **Import** → файлы:
   - `postman/Google Weather Open API English.postman_collection.json` **или** Russian
   - `postman/Google Weather Open API.postman_environment.json`
3. Справа сверху выберите environment **Google Weather Open API**.

## Первый успешный запрос

1. Папка **Локация** → **GetLocationTimeZone**
2. **Send**
3. Ожидание:
   - HTTP `200`
   - trailer `grpc-status: 0`
   - в теле (protobuf) строка таймзоны, для дефолтных координат MV — `America/Los_Angeles`

Координаты по умолчанию: `lat=37.422`, `lng=-122.084` (Mountain View).

## Переменные environment

| Переменная | Зачем |
|------------|--------|
| `host` | `pixelweatherhub-pa.googleapis.com` |
| `api_key` | клиентский ключ из APK |
| `android_package` | `com.google.android.apps.weather` |
| `android_cert` | SHA-1 подписи приложения |
| `client_id` | `pixel-weather-mobile` |
| `lat` / `lng` | координаты |
| `lang` | язык (`en-US`, `ru-RU`, …) |
| `oauth_token` | **пусто** — только для OAuth-папки Preferences |

## Если не взлетело

| Симптом | Что сделать |
|---------|-------------|
| `Android client application <empty> are blocked` | проверьте `android_package` и `android_cert` |
| HTML 404 | нужен `Content-Type: application/grpc`, не JSON |
| `grpc-status: 16` на weather | вы в папке Preferences — это ожидаемо без OAuth |
| Пустое тело | используйте Postman Desktop (HTTP/2); или CLI `scripts/grpc_client.py` |

## CLI (если Postman режет binary gRPC)

```bash
python3 scripts/grpc_client.py timezone --lat 37.422 --lng -122.084
python3 scripts/grpc_client.py weather --lat 37.422 --lng -122.084 --lang ru-RU
```
