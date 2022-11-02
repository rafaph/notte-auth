import pytest
from assertpy import assert_that
from faker import Faker

from auth.domain.clients import LoginRequest
from auth.infra.clients import HTTPUserClient
from tests.helpers import MockRoute, MockServer


@pytest.mark.asyncio
@pytest.mark.describe(HTTPUserClient.__name__)
class TestHttpUserClient:
    @pytest.mark.it("should return a valid login response")
    async def test_login_success(self, faker: Faker) -> None:
        login_route = MockRoute.parse_obj(
            {
                "path": "/login",
                "method": "POST",
                "response": {"status": 200, "data": {"user_id": faker.uuid4()}},
            }
        )
        async with MockServer([login_route]) as client:
            # given
            user_client = HTTPUserClient(client)
            request = LoginRequest(
                username=faker.user_name(), password=faker.password()
            )

            # when
            response = await user_client.login(request)

            # then
            assert_that(response.is_ok).is_true()

    @pytest.mark.it("should return an error response")
    async def test_login_fail(self, faker: Faker) -> None:
        login_route = MockRoute.parse_obj(
            {
                "path": "/login",
                "method": "POST",
                "response": {
                    "status": 500,
                },
            }
        )
        async with MockServer([login_route]) as client:
            # given
            user_client = HTTPUserClient(client)
            request = LoginRequest(
                username=faker.user_name(), password=faker.password()
            )

            # when
            response = await user_client.login(request)

            # then
            assert_that(response.is_err).is_true()
