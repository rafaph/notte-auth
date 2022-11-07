import jwt
import pytest
from assertpy import assert_that
from faker import Faker

from auth.domain.entities import Payload
from auth.infra.services import JwtTokenGenerator
from tests.factories import make_jwt_config


@pytest.mark.asyncio
@pytest.mark.describe(JwtTokenGenerator.__name__)
class TestJwtTokenGenerator:
    @pytest.mark.it("should return a ok when config is valid")
    async def test_ok(self, faker: Faker) -> None:
        config = make_jwt_config()
        generator = JwtTokenGenerator(config)
        payload = Payload(user_id=faker.uuid4())
        result = await generator.generate(payload)
        assert_that(result.is_ok).is_true()
        token = result.unwrap()
        user_id = jwt.decode(token, config.public_key, algorithms=["EdDSA"]).get(
            "user_id"
        )
        assert_that(user_id).is_equal_to(payload.user_id)

    @pytest.mark.it("should return an err when config is invalid")
    async def test_err(self, faker: Faker) -> None:
        config = make_jwt_config(private_key=faker.pystr())
        generator = JwtTokenGenerator(config)
        payload = Payload(user_id=faker.uuid4())
        result = await generator.generate(payload)
        assert_that(result.is_err).is_true()
