#!/usr/bin/env python3
"""Minimal example — timezone + weather with default public client credentials."""

from google_weather import WeatherClient, print_credentials

def main() -> None:
    print_credentials()
    client = WeatherClient()

    lat, lng = 37.422, -122.084  # Mountain View
    tz = client.get_timezone(lat, lng)
    print("timezone:", tz.get("data", {}).get("timezone"), "ok=", tz.get("ok"))

    weather = client.get_weather(lat, lng, lang="en-US")
    print("weather ok=", weather.get("ok"), "bytes-ish strings=", len(weather.get("summary_strings") or []))
    for s in (weather.get("summary_strings") or [])[:12]:
        print(" ", s)

if __name__ == "__main__":
    main()
