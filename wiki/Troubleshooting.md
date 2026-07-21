# Troubleshooting

| Symptom | Cause | Fix |
|---------|--------|-----|
| `API_KEY_ANDROID_APP_BLOCKED` / app `<empty>` | Missing package or cert header | Set both `X-Android-Package` and `X-Android-Cert` |
| `grpc-status: 16` on weather | Wrong service or broken key | Check path; ensure API key header present |
| `grpc-status: 16` on preferences | Expected without OAuth | Add Bearer token or ignore preferences |
| `grpc-status: 3` | Bad protobuf body | Use library builders / REST proxy |
| `grpc-status: 13` on map-tile | Unsupported layer enum | Use layer 1–4 |
| HTML 404 from host | Used JSON REST path | Use gRPC path or REST **proxy** on localhost |
| curl HTTP/2 error | Old curl | Upgrade curl; macOS `/usr/bin/curl` usually OK |
| Empty Postman body | GUI binary limits | Use `python -m google_weather serve` + JSON requests |
| `pip install` ok but import fails | wrong cwd | `pip install -e .` from repo root; import `google_weather` |

## Debug

```bash
python -m google_weather credentials
python -m google_weather timezone --lat 37.422 --lng -122.084 --json
```

If timezone works, credentials are fine — debug the specific method next.
