from app.auth.users import User
from app.core.exceptions import AuthorizationError
from app.models.schemas import Role

PERMISSIONS={
    Role.viewer:{"chat","knowledge_search"},
    Role.analyst:{"chat","knowledge_search","analytics","mcp"},
    Role.administrator:{"chat","knowledge_search","analytics","mcp","admin_sensitive"},
}

def authorize(user: User, action: str) -> None:
    if action not in PERMISSIONS.get(user.role,set()):
        raise AuthorizationError(f"Role '{user.role.value}' is not permitted to perform '{action}'")
