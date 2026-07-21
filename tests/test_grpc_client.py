#!/usr/bin/env python3
"""Unit tests for shipped grpc_client builders + optional live smoke.

Default: pure offline tests of protobuf encoding and framing.
Set RUN_LIVE=1 to hit production weatherhub (network required).
"""

from __future__ import annotations

import os
import struct
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import grpc_client as gc  # noqa: E402


class TestEncoding(unittest.TestCase):
    def test_varint_small(self):
        self.assertEqual(gc.encode_varint(0), b"\x00")
        self.assertEqual(gc.encode_varint(1), b"\x01")
        self.assertEqual(gc.encode_varint(150), b"\x96\x01")

    def test_latlng_wire_shape(self):
        raw = gc.encode_latlng(37.422, -122.084)
        # field1 float + field2 float = 1+1+4 + 1+1+4 = 10 bytes keys+payload
        # key is 1 byte each for fields 1 and 2 wire 5
        self.assertEqual(raw[0], (1 << 3) | 5)
        self.assertEqual(raw[5], (2 << 3) | 5)
        lat = struct.unpack("<f", raw[1:5])[0]
        lng = struct.unpack("<f", raw[6:10])[0]
        self.assertAlmostEqual(lat, 37.422, places=3)
        self.assertAlmostEqual(lng, -122.084, places=3)

    def test_timezone_request_contains_latlng(self):
        body = gc.req_get_location_timezone(37.422, -122.084)
        # outer field 1 length-delimited
        self.assertEqual(body[0], (1 << 3) | 2)
        self.assertGreater(len(body), 10)

    def test_essentials_request_has_lang(self):
        body = gc.req_get_essentials_weather(37.422, -122.084, "en-US", 1)
        self.assertIn(b"en-US", body)

    def test_grpc_frame_header(self):
        payload = b"\x0a\x03abc"
        frame = gc.grpc_frame(payload)
        self.assertEqual(frame[0], 0)
        self.assertEqual(struct.unpack(">I", frame[1:5])[0], len(payload))
        self.assertEqual(frame[5:], payload)

    def test_decode_timezone_response_sample(self):
        sample = ROOT / "samples" / "responses" / "GetLocationTimeZone.bin"
        if not sample.is_file():
            self.skipTest("sample missing")
        raw = sample.read_bytes()
        msg, meta = gc.parse_grpc_response(raw)
        self.assertIsNotNone(msg)
        self.assertEqual(gc.decode_string_field1(msg), "America/Los_Angeles")

    def test_identity_hashes_match_artifacts(self):
        import hashlib
        import json

        meta = json.loads((ROOT / "artifacts" / "metadata" / "identity.json").read_text())
        for art in meta["artifacts"]:
            path = ROOT / art["file"]
            self.assertTrue(path.is_file(), art["file"])
            h = hashlib.sha256(path.read_bytes()).hexdigest()
            self.assertEqual(h, art["sha256"], art["file"])
            self.assertEqual(path.stat().st_size, art["bytes"])

    def test_openapi_and_postman_exist(self):
        import json

        oai = json.loads((ROOT / "openapi" / "openapi.json").read_text())
        self.assertEqual(oai["openapi"], "3.0.3")
        self.assertGreaterEqual(len(oai["paths"]), 10)
        # Must include proven RPCs
        paths = oai["paths"]
        self.assertIn(
            "/google.internal.android.pixel.weatherhub.v1.LocationMetadataService/GetLocationTimeZone",
            paths,
        )
        self.assertIn(
            "/google.internal.android.pixel.weatherhub.v1.WeatherBriefService/GetEssentialsWeather",
            paths,
        )
        coll = json.loads(
            (ROOT / "postman" / "Pixel_Weather_API.postman_collection.json").read_text()
        )
        self.assertIn("collection/v2.1.0", coll["info"]["schema"])
        self.assertGreaterEqual(len(coll["item"]), 5)
        env = json.loads(
            (ROOT / "postman" / "Pixel_Weather_API.postman_environment.json").read_text()
        )
        keys = {v["key"] for v in env["values"]}
        for k in ("host", "api_key", "android_package", "android_cert", "client_id"):
            self.assertIn(k, keys)


@unittest.skipUnless(os.environ.get("RUN_LIVE") == "1", "set RUN_LIVE=1 for live network tests")
class TestLive(unittest.TestCase):
    def test_timezone_live(self):
        status, trailers, msg = gc.call_rpc(
            "/google.internal.android.pixel.weatherhub.v1.LocationMetadataService/GetLocationTimeZone",
            gc.req_get_location_timezone(37.422, -122.084),
        )
        self.assertEqual(status, 0, trailers)
        self.assertEqual(gc.decode_string_field1(msg), "America/Los_Angeles")

    def test_weather_live_nonempty(self):
        status, trailers, msg = gc.call_rpc(
            "/google.internal.android.pixel.weatherhub.v1.WeatherBriefService/GetEssentialsWeather",
            gc.req_get_essentials_weather(37.422, -122.084, "en-US", 1),
        )
        self.assertEqual(status, 0, trailers)
        self.assertIsNotNone(msg)
        self.assertGreater(len(msg), 1000)
        strings = gc.extract_strings(msg)
        joined = " ".join(strings)
        self.assertTrue(
            any(x in joined for x in ("Sunny", "Clear", "cloud", "Partly", "Weather")),
            joined[:500],
        )


if __name__ == "__main__":
    unittest.main()
