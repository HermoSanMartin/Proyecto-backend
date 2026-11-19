from pwdlib import PasswordHash
from pwdlib.exceptions import UnknownHashError
from pwdlib.hashers.argon2 import Argon2Hasher

_hasher = PasswordHash((Argon2Hasher(),))


def hashear_password(password_plana: str) -> str:
    return _hasher.hash(password_plana)


def verificar_password(password_plana: str, password_hash: str) -> bool:
    try:
        return _hasher.verify(password_plana, password_hash)
    except (UnknownHashError, ValueError, TypeError):
        return False
