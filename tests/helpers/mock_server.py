import asyncio
import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, HTTPServer
from multiprocessing import Process
from typing import Any, Type
from urllib.parse import urlparse

import httpx
import portpicker
from pydantic import BaseModel


class MockResponse(BaseModel):
    status: int
    data: list[Any] | dict[str, Any] | None = None


class MockRoute(BaseModel):
    method: str
    path: str
    response: MockResponse


def create_server_handler(routes: list[MockRoute]) -> Type[BaseHTTPRequestHandler]:
    class handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            self._handle("GET")

        def do_POST(self) -> None:
            self._handle("POST")

        def do_PUT(self) -> None:
            self._handle("PUT")

        def do_PATCH(self) -> None:
            self._handle("PATCH")

        def do_DELETE(self) -> None:
            self._handle("DELETE")

        def do_OPTIONS(self) -> None:
            self._handle("OPTIONS")

        def log_message(self, _format: str, *args: Any) -> None:
            pass

        def _handle(self, method: str) -> None:
            path = urlparse(self.path).path
            for route in routes:
                if route.path == path and route.method == method:
                    self.send_response(route.response.status)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    data = (
                        json.dumps(route.response.data) if route.response.data else ""
                    )
                    self.wfile.write(data.encode("utf-8"))
                    return
            self.send_response(HTTPStatus.NOT_FOUND)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"message": "not found"}).encode("utf-8"))

    return handler


def start_server(host: str, port: int, handler: Type[BaseHTTPRequestHandler]) -> None:
    server = HTTPServer((host, port), handler)
    server.serve_forever()


class MockServer:
    def __init__(self, routes: list[MockRoute]) -> None:
        self._routes = [
            *routes,
            MockRoute.parse_obj(
                {
                    "path": "/healthz",
                    "method": "GET",
                    "response": {"status": HTTPStatus.OK, "data": {"message": "ok"}},
                }
            ),
        ]
        self._process: Process | None = None
        self._base_url: str | None = None
        self._client: httpx.AsyncClient | None = None

    async def _is_ready(self) -> bool:
        try:
            assert self._client
            response = await self._client.get("/healthz")
            is_ready = response.status_code == HTTPStatus.OK
        except Exception:
            is_ready = False

        return is_ready

    async def _wait_start(self, times: int = 10, timeout: int = 200) -> None:
        count = 0
        while count < times and not await self._is_ready():
            await asyncio.sleep(timeout / 1000)
            count += 1

        if count == times:
            raise Exception("server is not ready yet")

    async def up(self) -> None:
        port = portpicker.pick_unused_port()
        host = "127.0.0.1"
        self._base_url = f"http://{host}:{port}"
        self._process = Process(
            target=start_server,
            args=(host, port, create_server_handler(self._routes)),
            daemon=True,
        )
        self._process.start()
        self._client = httpx.AsyncClient(base_url=self._base_url)
        await self._wait_start()

    async def _wait_stop(self, times: int = 10, timeout: int = 200) -> None:
        count = 0
        assert self._process
        while count < times and self._process.is_alive():
            await asyncio.sleep(timeout / 1000)
            count += 1
        if count == times:
            raise Exception("server is still running")

    async def down(self) -> None:
        assert self._process
        self._process.terminate()
        await self._wait_stop()
        assert self._client
        await self._client.aclose()

    async def __aenter__(self) -> httpx.AsyncClient:
        await self.up()
        assert self._client
        return self._client

    async def __aexit__(
        self,
        exc_type: Type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: Any,
    ) -> None:
        await self.down()
