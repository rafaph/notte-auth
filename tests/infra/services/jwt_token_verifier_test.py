import asyncio

import pytest
from assertpy import assert_that
from faker import Faker

from auth.domain.entities import Payload
from auth.infra.services import JwtTokenVerifier
from tests.factories import make_jwt_config, make_token


@pytest.mark.asyncio
@pytest.mark.describe(JwtTokenVerifier.__name__)
class TestJwtTokenVerifier:
    @pytest.mark.it("should return a ok when token is valid")
    async def test_ok(self, faker: Faker) -> None:
        # given
        config = make_jwt_config()
        payload = Payload(user_id=faker.uuid4())
        token = make_token(config, payload)
        verifier = JwtTokenVerifier(config)

        # when
        result = await verifier.verify(token)

        # then
        assert_that(result.is_ok).is_true()
        assert_that(result.unwrap()).is_equal_to(payload)

    @pytest.mark.it("should return a err when token is invalid")
    async def test_err(self, faker: Faker) -> None:
        # given
        expiration_in_seconds = 0.2
        config = make_jwt_config(expiration_in_minutes=expiration_in_seconds / 60)
        payload = Payload(user_id=faker.uuid4())
        token = make_token(config, payload)
        verifier = JwtTokenVerifier(config)

        await asyncio.sleep(expiration_in_seconds)

        # when
        result = await verifier.verify(token)

        # then
        assert_that(result.is_err).is_true()
