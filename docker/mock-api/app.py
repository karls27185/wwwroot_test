#!/usr/bin/env python3
"""Универсальная заглушка HTTP-сервисов WMS (central / printpack / crpt).

Поведение (эвристика, т.к. точные контракты внешних сервисов недоступны):
  * path содержит token/auth/login  -> {"token": "...", "uuidToken": "...", ...}
  * GET и path содержит list/sessions/assemblies/products/datamatrix/get -> []
  * /health, /, /ping               -> {"status": "ok", "service": "<name>"}
  * всё остальное                    -> {} со статусом 200

Настраивается через env:
  SERVICE_NAME — имя сервиса в логах/health (по умолчанию "mock")
  PORT         — порт прослушивания (по умолчанию 8015)
  LOG_BODY     — логировать ли тело запроса ("true"/"false", по умолчанию "true")
"""
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

PORT = int(os.getenv("PORT", "8015"))
SERVICE = os.getenv("SERVICE_NAME", "mock")
LOG_BODY = os.getenv("LOG_BODY", "true").lower() == "true"

TOKEN_HINTS = ("token", "auth", "login")
LIST_HINTS = ("list", "all", "sessions", "assemblies", "products", "datamatrix", "get")
HEALTH_PATHS = ("/", "/health", "/ping", "/api/ws")


class Handler(BaseHTTPRequestHandler):
    server_version = "WMSMock/1.0"

    def _payload(self, method, path):
        p = path.lower()
        if p in HEALTH_PATHS:
            return {"status": "ok", "service": SERVICE}
        if any(h in p for h in TOKEN_HINTS):
            return {
                "token": "mock-token",
                "uuidToken": "00000000-0000-0000-0000-000000000000",
                "expireDate": "2099-01-01T00:00:00",
            }
        if method == "GET" and any(h in p for h in LIST_HINTS):
            return []
        return {}

    def _json(self, payload, status=200):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_body(self):
        length = int(self.headers.get("Content-Length") or 0)
        if not length:
            return None
        raw = self.rfile.read(length)
        try:
            return json.loads(raw.decode("utf-8"))
        except Exception:
            return raw.decode("utf-8", "replace")

    def _route(self, method):
        path = urlparse(self.path).path.rstrip("/") or "/"
        body = self._read_body() if method in ("POST", "PUT", "PATCH") else None
        if LOG_BODY:
            print(f"[{SERVICE}] {method} {path} body={body}", flush=True)
        else:
            print(f"[{SERVICE}] {method} {path}", flush=True)
        self._json(self._payload(method, path))

    def do_GET(self):
        self._route("GET")

    def do_POST(self):
        self._route("POST")

    def do_PUT(self):
        self._route("PUT")

    def do_PATCH(self):
        self._route("PATCH")

    def do_DELETE(self):
        self._route("DELETE")

    def log_message(self, fmt, *args):
        pass  # логируем только через _route


if __name__ == "__main__":
    print(f"[{SERVICE}] listening on 0.0.0.0:{PORT}", flush=True)
    ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()