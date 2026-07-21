"""gRPC-over-HTTP/2 transport via curl (no grpcio dependency)."""

from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path
from typing import Dict, Optional, Tuple

from .credentials import Credentials
from .protobuf_codec import grpc_frame, parse_grpc_frame


class TransportError(RuntimeError):
    pass


def call_rpc(
    method_path: str,
    body: bytes,
    creds: Credentials,
    *,
    timeout: int = 60,
) -> Tuple[int, Dict[str, str], Optional[bytes], bytes]:
    """POST unary gRPC method.

    Returns:
        (grpc_status, trailers_and_headers, message_bytes|None, raw_body)
    """
    if not method_path.startswith("/"):
        method_path = "/" + method_path

    with tempfile.NamedTemporaryFile(delete=False) as reqf, tempfile.NamedTemporaryFile(
        delete=False
    ) as respf, tempfile.NamedTemporaryFile(delete=False, mode="w+") as hdrf:
        req_path, resp_path, hdr_path = reqf.name, respf.name, hdrf.name
        reqf.write(grpc_frame(body))

    url = f"https://{creds.host}{method_path}"
    cmd = [
        "curl",
        "-sS",
        "--http2",
        "-D",
        hdr_path,
        "-o",
        resp_path,
        "-X",
        "POST",
        url,
        "--max-time",
        str(timeout),
        "--data-binary",
        f"@{req_path}",
    ]
    for k, v in creds.headers().items():
        cmd.extend(["-H", f"{k}: {v}"])

    try:
        proc = subprocess.run(cmd, capture_output=True, text=True)
    finally:
        Path(req_path).unlink(missing_ok=True)

    headers_text = Path(hdr_path).read_text(errors="replace")
    raw = Path(resp_path).read_bytes()
    Path(hdr_path).unlink(missing_ok=True)
    Path(resp_path).unlink(missing_ok=True)

    if proc.returncode != 0 and not headers_text:
        raise TransportError(f"curl failed ({proc.returncode}): {proc.stderr}")

    trailers: Dict[str, str] = {}
    for line in headers_text.splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            trailers[k.strip().lower()] = v.strip()
        elif line.startswith("HTTP/"):
            trailers["http_status_line"] = line

    msg, meta = parse_grpc_frame(raw)
    for k, v in meta.items():
        trailers[f"body_{k}"] = str(v)

    status_s = trailers.get("grpc-status", "-1")
    try:
        status = int(status_s)
    except ValueError:
        status = -1

    return status, trailers, msg, raw
