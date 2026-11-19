from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher

_hasher = PasswordHash((Argon2Hasher(),))


def hashear_password(password_plana: str) -> str:
    return _hasher.hash(password_plana)


def verificar_password(password_plana: str, password_hash: str) -> bool:
    try:
        return _hasher.verify(password_plana, password_hash)
    except Exception:
        return False
