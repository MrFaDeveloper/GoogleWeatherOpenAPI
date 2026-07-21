#!/usr/bin/env python3
import os
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from google_weather import WeatherClient, DEFAULT_API_KEY, DEFAULT_ANDROID_CERT
from google_weather.protobuf_codec import (
    req_get_location_timezone,
    parse_grpc_frame,
    first_string_field,
)


class Offline(unittest.TestCase):
    def test_credentials_present(self):
        self.assertTrue(DEFAULT_API_KEY.startswith("AIzaSy"))
        self.assertEqual(len(DEFAULT_ANDROID_CERT), 40)

    def test_sample_timezone_bin(self):
        raw = (ROOT / "samples/responses/GetLocationTimeZone.bin").read_bytes()
        msg, _ = parse_grpc_frame(raw)
        self.assertEqual(first_string_field(msg, 1), "America/Los_Angeles")

    def test_request_builder(self):
        self.assertGreater(len(req_get_location_timezone(1.0, 2.0)), 5)

    def test_llms_txt_format(self):
        text = (ROOT / "llms.txt").read_text(encoding="utf-8")
        self.assertTrue(text.startswith("# Google Weather Open API"))
        self.assertIn("> ", text)
        self.assertIn("## Docs", text)
        self.assertIn("AIzaSyCO1vbj", text)

    def test_wiki_home(self):
        self.assertTrue((ROOT / "wiki/Home.md").is_file())
        self.assertTrue((ROOT / "wiki/Credentials.md").is_file())


class Live(unittest.TestCase):
    """Hits pixelweatherhub-pa with stock client headers (least-auth path).

    Set SKIP_LIVE=1 to skip when offline. Prefer running with network so CI/agents
    prove the shipped WeatherClient entry points, not only offline builders.
    """

    @classmethod
    def setUpClass(cls):
        if os.environ.get("SKIP_LIVE") == "1":
            raise unittest.SkipTest("SKIP_LIVE=1")

    def test_timezone(self):
        r = WeatherClient().get_timezone(37.422, -122.084)
        self.assertTrue(r["ok"], r)
        self.assertEqual(r["data"]["timezone"], "America/Los_Angeles")

    def test_weather(self):
        r = WeatherClient().get_weather(37.422, -122.084)
        self.assertTrue(r["ok"], r)
        self.assertGreater(len(r.get("summary_strings") or []), 3)

    def test_air_quality(self):
        r = WeatherClient().get_air_quality(37.422, -122.084)
        self.assertTrue(r["ok"], r)
        self.assertTrue(r.get("data") or r.get("summary_strings"), r)


if __name__ == "__main__":
    unittest.main()
