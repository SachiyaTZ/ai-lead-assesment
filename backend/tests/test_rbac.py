import pytest
from app.auth.users import User
from app.models.schemas import Role
from app.security.authorization import authorize
from app.core.exceptions import AuthorizationError

def test_viewer_blocked_analytics():
    with pytest.raises(AuthorizationError): authorize(User("1","v",Role.viewer,""),"analytics")
def test_analyst_allowed_analytics(): authorize(User("2","a",Role.analyst,""),"analytics")
