import pytest
from assertpy import assert_that
from faker import Faker

from auth.domain.entities import Payload
from auth.infra.services import JwtTokenGenerator
from tests.factories import make_jwt_config, make_payload_from_token


@pytest.mark.asyncio
@pytest.mark.describe(JwtTokenGenerator.__name__)
class TestJwtTokenGenerator:
    @pytest.mark.it("should return a ok when config is valid")
    async def test_ok(self, faker: Faker) -> None:
        # given
        config = make_jwt_config()
        generator = JwtTokenGenerator(config)
        expected_payload = Payload(user_id=faker.uuid4())

        # when
        result = await generator.generate(payload=expected_payload)

        # then
        assert_that(result.is_ok).is_true()
        payload = make_payload_from_token(config, result.unwrap())
        assert_that(payload).is_equal_to(expected_payload)

    @pytest.mark.it("should return an err when config is invalid")
    async def test_err(self, faker: Faker) -> None:
        # given
        config = make_jwt_config(private_key=faker.pystr())
        generator = JwtTokenGenerator(config)
        payload = Payload(user_id=faker.uuid4())

        # when
        result = await generator.generate(payload=payload)

        # then
        assert_that(result.is_err).is_true()
