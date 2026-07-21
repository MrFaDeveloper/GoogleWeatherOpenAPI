#!/usr/bin/env bash
# Run the least-auth repro suite against live pixelweatherhub-pa.
# Requires: curl, python3, network.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PY="$ROOT/scripts/grpc_client.py"
LAT="${LAT:-37.422}"
LNG="${LNG:--122.084}"
LANG="${LANG:-en-US}"

echo "==> GetLocationTimeZone"
python3 "$PY" timezone --lat "$LAT" --lng "$LNG"
echo
echo "==> GetLocationName"
python3 "$PY" location-name --lat "$LAT" --lng "$LNG"
echo
echo "==> GetEssentialsWeather"
python3 "$PY" weather --lat "$LAT" --lng "$LNG" --lang "$LANG" --quiet-strings
echo
echo "==> GetAirQuality"
python3 "$PY" aqi --lat "$LAT" --lng "$LNG" --lang "$LANG"
echo
echo "==> GetPollen"
python3 "$PY" pollen --lat "$LAT" --lng "$LNG" --lang "$LANG" --quiet-strings
echo
echo "==> GetAirQualityMapLayers"
python3 "$PY" aqi-map --lat "$LAT" --lng "$LNG" --lang "$LANG" --quiet-strings
echo
echo "==> GetPrecipitationMapLayers"
python3 "$PY" precip-map --lat "$LAT" --lng "$LNG" --quiet-strings
echo
echo "==> GetMapTileTemplate"
python3 "$PY" map-tile --layer 1
echo
echo "OK: all least-auth RPCs exercised"
