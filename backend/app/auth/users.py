from dataclasses import dataclass
import hashlib, hmac
from app.models.schemas import Role

@dataclass(frozen=True)
class User:
    user_id: str
    email: str
    role: Role
    password_hash: str


def _hash_password(password: str, salt: str) -> str:
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 120_000)
    return f"pbkdf2_sha256$120000${salt}${digest.hex()}"


def _verify(password: str, encoded: str) -> bool:
    _, rounds, salt, expected = encoded.split("$", 3)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), int(rounds)).hex()
    return hmac.compare_digest(digest, expected)

USERS = {
    "viewer@company.com": User("u-viewer", "viewer@company.com", Role.viewer, _hash_password("Viewer123!", "viewer-demo-salt")),
    "analyst@company.com": User("u-analyst", "analyst@company.com", Role.analyst, _hash_password("Analyst123!", "analyst-demo-salt")),
    "admin@company.com": User("u-admin", "admin@company.com", Role.administrator, _hash_password("Admin123!", "admin-demo-salt")),
}

def authenticate(email: str, password: str) -> User | None:
    user = USERS.get(email.lower())
    return user if user and _verify(password, user.password_hash) else None
