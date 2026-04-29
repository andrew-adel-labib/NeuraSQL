class ForecastingError(Exception):
    def __init__(self, message, *, error_code="APP_ERROR", context=None, cause=None, user_message=None):
        self.error_code = error_code
        self.context = context or {}
        self.cause = cause
        self.user_message = user_message or "Internal error"
        super().__init__(message)

    def to_dict(self):
        return {
            "error_code": self.error_code,
            "message": self.user_message,
            "context": self.context,
        }

class SecurityViolation(ForecastingError):
    def __init__(self, message, **kw):
        super().__init__(message, error_code="SECURITY_VIOLATION", user_message="Security violation", **kw)

class DatabaseError(ForecastingError):
    def __init__(self, message, **kw):
        super().__init__(message, error_code="DATABASE_ERROR", user_message="Database error", **kw)

class PlanningError(ForecastingError):
    def __init__(self, message, **kw):
        super().__init__(message, error_code="PLANNING_ERROR", user_message="Planning failed", **kw)