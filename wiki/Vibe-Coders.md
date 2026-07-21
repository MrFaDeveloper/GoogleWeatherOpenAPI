# For vibe coders (Cursor, Claude, Copilot, Windsurf, …)

## Goal

Make an LLM **actually** write working weather code against this reverse, without inventing fake API keys or REST paths that do not exist.

## Feed the agent these files (in order)

1. **[`/llms.txt`](../llms.txt)** — curated map (start here every time)
2. **[`/llms-full.txt`](../llms-full.txt)** — expanded single-file context when the model has room
3. **[`wiki/Credentials.md`](Credentials.md)** — exact headers
4. **[`wiki/Python-Library.md`](Python-Library.md)** — how to call the client
5. **[`examples/quickstart.py`](../examples/quickstart.py)** — copy-paste

### Cursor / VS Code

- Add the repo root to the workspace.
- In chat: `@llms.txt @wiki/Credentials.md write a script that prints weather for Moscow`
- Or paste `llms-full.txt` into the system prompt for a one-shot agent.

### Claude Projects / Custom GPTs

Upload:

- `llms.txt`
- `llms-full.txt`
- `wiki/Credentials.md`
- `src/google_weather/client.py`

Instructions snippet:

```text
Use Google Weather Open API from this project only.
Default credentials are in Credentials.md — do not invent other API keys.
Prefer WeatherClient or the local REST proxy. Do not invent JSON REST on
pixelweatherhub-pa.googleapis.com; that host is gRPC-only.
```

### Copilot Chat

```text
#file:llms.txt #file:wiki/Python-Library.md
Implement get_weather for lat/lng using google_weather.WeatherClient
```

## What models get wrong (pre-bunk)

| Hallucination | Reality |
|---------------|---------|
| `https://pixelweatherhub-pa.googleapis.com/v1/weather` JSON | **No** public JSON REST on that host |
| Random `AIza…` key | Use **only** the documented CO1vbj key + package/cert |
| “Need Google login for forecast” | **False** for essentials/AQI/pollen/maps |
| “Just use OpenWeatherMap” | Different product; this repo is Pixel weatherhub |

## Minimal prompt that works

```text
Repo: https://github.com/MrFaDeveloper/GoogleWeatherOpenAPI
Read llms.txt and wiki/Credentials.md.
Write Python that installs the package from the repo and prints timezone +
weather summary_strings for lat=55.75 lng=37.62 lang=ru-RU using WeatherClient.
Do not invent credentials.
```

## llms.txt standard

This repo follows Jeremy Howard’s [/llms.txt](https://llmstxt.org/) proposal:

- H1 project name
- Blockquote summary
- H2 sections with link lists
- Optional section for secondary material

`llms-full.txt` is an expanded context file for agents (similar role to `llms-ctx-full.txt` in FastHTML docs).

## Directory listing

You may register the public GitHub raw URL of `llms.txt` in community directories such as llmstxt.site if you wish — not required.
