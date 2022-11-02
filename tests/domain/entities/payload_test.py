import pytest
from assertpy import assert_that
from faker import Faker

from auth.domain.entities import Payload


@pytest.mark.describe(Payload.__name__)
class TestSession:
    @pytest.mark.it("should return an error when user id is not an uuid")
    def test_validation_error(self, faker: Faker) -> None:
        result = Payload.create(user_id=faker.first_name())
        assert_that(result.is_err).is_true()

    @pytest.mark.it("should return  when user id is an uuid")
    def test_validation_ok(self, faker: Faker) -> None:
        result = Payload.create(user_id=faker.uuid4())
        assert_that(result.is_ok).is_true()
