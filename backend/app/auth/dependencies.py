from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from app.auth.jwt import decode_access_token
from app.auth.users import User
from app.models.schemas import Role

bearer=HTTPBearer(auto_error=True)
async def current_user(creds: HTTPAuthorizationCredentials=Depends(bearer)) -> User:
    p=decode_access_token(creds.credentials)
    return User(p["sub"], p.get("email",""), Role(p["role"]), "")
