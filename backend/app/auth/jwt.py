from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from app.core.config import get_settings
from app.core.exceptions import AuthenticationError
from app.models.schemas import Role
from app.auth.users import User

def create_access_token(user: User) -> str:
    s=get_settings(); exp=datetime.now(timezone.utc)+timedelta(minutes=s.jwt_expire_minutes)
    return jwt.encode({"sub":user.user_id,"email":user.email,"role":user.role.value,"exp":exp}, s.jwt_secret, algorithm="HS256")

def decode_access_token(token: str) -> dict:
    try: return jwt.decode(token, get_settings().jwt_secret, algorithms=["HS256"])
    except JWTError as e: raise AuthenticationError("Invalid or expired token") from e
