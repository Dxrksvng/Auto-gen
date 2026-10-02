"""The renderer must not touch the network, even for loopback addresses."""

import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import pytest

from renderer import NETWORK_BLOCK_FLAGS, RendererUnavailableError, chrome_command, find_chrome, print_html_to_pdf


def test_every_chrome_command_carries_the_network_block_flags(tmp_path):
    command = chrome_command("chrome", tmp_path / "p.html", tmp_path / "o.pdf", tmp_path / "prof")
    for flag in NETWORK_BLOCK_FLAGS:
        assert flag in command


def test_remote_resources_are_not_requested_while_rendering(tmp_path):
    try:
        find_chrome()
    except RendererUnavailableError:
        pytest.skip("Chrome/Chromium not available")
    hits: list[str] = []

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):  # noqa: N802 - http.server API
            hits.append(self.path)
            self.send_response(200)
            self.end_headers()

        def log_message(self, *args):
            pass

    server = HTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        port = server.server_address[1]
        page = tmp_path / "probe.html"
        page.write_text(
            f'<html><body>probe<img src="http://127.0.0.1:{port}/tracker.png">'
            f'<link rel="stylesheet" href="http://localhost:{port}/remote.css"></body></html>',
            encoding="utf-8",
        )
        out = tmp_path / "probe.pdf"
        print_html_to_pdf(page, out, tmp_path / "profile")  # the page itself still prints
        assert out.exists()
    finally:
        server.shutdown()
    assert hits == []  # nothing reached the local server
