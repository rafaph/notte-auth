from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    NoEncryption,
    PrivateFormat,
    PublicFormat,
)
from faker import Faker

from auth.config import JwtConfig

faker = Faker()


def _gen_keys() -> tuple[str, str]:
    private_key = Ed25519PrivateKey.generate()
    private_key_str = private_key.private_bytes(
        encoding=Encoding.PEM,
        format=PrivateFormat.PKCS8,
        encryption_algorithm=NoEncryption(),
    ).decode()
    public_key_str = (
        private_key.public_key()
        .public_bytes(encoding=Encoding.PEM, format=PublicFormat.SubjectPublicKeyInfo)
        .decode()
    )
    return private_key_str, public_key_str


def make_jwt_config(
    *,
    expiration_in_minutes: int | None = None,
    private_key: str | None = None,
    public_key: str | None = None
) -> JwtConfig:
    if private_key is None and public_key is None:
        private_key, public_key = _gen_keys()

    if private_key is None:
        private_key = faker.pystr()

    if public_key is None:
        public_key = faker.pystr()

    if expiration_in_minutes is None:
        expiration_in_minutes = faker.pyint()

    return JwtConfig(
        expiration_in_minutes=expiration_in_minutes,
        private_key=private_key,
        public_key=public_key,
    )
