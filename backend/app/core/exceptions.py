class AppError(Exception):
    status_code = 500
    code = "internal_error"
    def __init__(self, message: str, *, details: dict | None = None):
        super().__init__(message); self.message=message; self.details=details or {}

class ValidationError(AppError): status_code=400; code="validation_error"
class AuthenticationError(AppError): status_code=401; code="authentication_error"
class AuthorizationError(AppError): status_code=403; code="authorization_error"
class RateLimitError(AppError): status_code=429; code="rate_limit_exceeded"
class RetrievalError(AppError): status_code=503; code="retrieval_error"
class ToolExecutionError(AppError): status_code=502; code="tool_error"
