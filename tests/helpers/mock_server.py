import asyncio
import multiprocessing
from typing import Any, Type

import httpx
import portpicker
from faker import Faker
from pydantic import BaseModel, root_validator
from sanic import HTTPResponse, Request, Sanic, json
from sanic.models.handler_types import RouteHandler

faker = Faker()


def serve(app: Sanic, host: str, port: int) -> None:
    app.run(
        host,
        port,
        access_log=False,
        single_process=True,
        motd=False,
        verbosity=2,
        noisy_exceptions=False,
    )


class MockResponse(BaseModel):
    status: int
    data: dict[str, Any] | None = None


class MockRoute(BaseModel):
    method: str
    path: str
    response: MockResponse | None = None
    handler: RouteHandler | None = None

    @root_validator(pre=True)
    def _check_response_and_handler(cls, values: dict[str, Any]) -> dict[str, Any]:
        if not ("response" in values or "handler" in values):
            raise ValueError('one of the fields "response" or "handler" are missing')
        return values


class MockServer:
    _client: httpx.AsyncClient
    _app: Sanic
    _process: multiprocessing.Process

    def __init__(self, routes: list[MockRoute] | None = None) -> None:
        self._app = Sanic(faker.pystr(), configure_logging=False)
        if routes:
            self._add_routes(routes)

    def _add_routes(self, routes: list[MockRoute]) -> None:
        def create_handler(mock_route: MockRoute) -> RouteHandler:
            assert mock_route.response
            response = mock_route.response

            async def handler(_request: Request) -> HTTPResponse:
                return json(body=response.data, status=response.status)

            return handler

        status_route: MockRoute = MockRoute.parse_obj(
            {
                "path": "/status",
                "method": "GET",
                "response": {"status": 200, "data": {"status": "ok"}},
            }
        )
        routes = [*routes, status_route]
        for route in routes:
            if not route.handler:
                route.handler = create_handler(route)
            self._app.add_route(route.handler, route.path, methods=[route.method])

    async def _is_ready(self) -> bool:
        try:
            response = await self._client.get("/status")
            is_ready = response.status_code == 200
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

    async def _wait_stop(self, times: int = 10, timeout: int = 200) -> None:
        count = 0
        while count < times and self.process.is_alive():
            await asyncio.sleep(timeout / 1000)
            count += 1
        if count == times:
            raise Exception("server is still running")

    async def __aenter__(self) -> httpx.AsyncClient:
        port = portpicker.pick_unused_port()
        host = "127.0.0.1"
        self.process = multiprocessing.Process(
            target=serve, args=(self._app, host, port), daemon=True
        )
        self.process.start()
        self._client = httpx.AsyncClient(base_url=f"http://{host}:{port}")
        await self._wait_start()
        return self._client

    async def __aexit__(
        self,
        exc_type: Type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: Any,
    ) -> None:
        self.process.terminate()
        await self._wait_stop()
        Sanic.unregister_app(self._app)
        await self._client.aclose()
