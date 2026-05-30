"""
Neuro Error Codes - Structured error handling
Provides consistent error codes across the system
"""
from enum import Enum


class NeuroErrorCode(Enum):
    """Standard error codes for Neuro system."""
    
    # Provider Errors (1000-1099)
    PROVIDER_UNAVAILABLE = 1001
    PROVIDER_RATE_LIMIT = 1002
    PROVIDER_AUTH_FAILED = 1003
    PROVIDER_TIMEOUT = 1004
    PROVIDER_INVALID_RESPONSE = 1005
    PROVIDER_CIRCUIT_OPEN = 1006
    
    # Model Errors (1100-1199)
    MODEL_NOT_FOUND = 1101
    MODEL_NOT_ENABLED = 1102
    MODEL_INVALID_CONFIG = 1103
    MODEL_UNSUPPORTED = 1104
    
    # Skill Errors (1200-1299)
    SKILL_NOT_FOUND = 1201
    SKILL_LOAD_FAILED = 1202
    SKILL_EXECUTION_ERROR = 1203
    SKILL_TIMEOUT = 1204
    SKILL_INVALID_PARAMS = 1205
    
    # File Operation Errors (1300-1399)
    FILE_NOT_FOUND = 1301
    FILE_PERMISSION_DENIED = 1302
    FILE_WRITE_ERROR = 1303
    FILE_READ_ERROR = 1304
    FILE_TOO_LARGE = 1305
    FILE_UNSAFE_PATH = 1306
    
    # Task Execution Errors (1400-1499)
    TASK_TIMEOUT = 1401
    TASK_INVALID_GOAL = 1402
    TASK_MAX_RETRIES = 1403
    TASK_CIRCULAR_REF = 1404
    TASK_INVALID_CONTEXT = 1405
    
    # Validation Errors (1500-1599)
    VALIDATION_FAILED = 1501
    VALIDATION_SYNTAX_ERROR = 1502
    VALIDATION_TYPE_ERROR = 1503
    
    # System Errors (9000-9999)
    SYSTEM_INIT_FAILED = 9001
    SYSTEM_CONFIG_ERROR = 9002
    SYSTEM_UNHANDLED = 9999


class NeuroError(Exception):
    """Base exception for Neuro system."""
    
    def __init__(self, code: NeuroErrorCode, message: str, details: dict = None):
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(f"[{code.name}] {message}")
    
    def to_dict(self) -> dict:
        return {
            "error": self.code.name,
            "code": self.code.value,
            "message": self.message,
            "details": self.details,
        }


class ProviderError(NeuroError):
    """Provider-related errors."""
    pass


class ModelError(NeuroError):
    """Model-related errors."""
    pass


class SkillError(NeuroError):
    """Skill-related errors."""
    pass


class FileOperationError(NeuroError):
    """File operation errors."""
    pass


class TaskError(NeuroError):
    """Task execution errors."""
    pass


def format_error(error: Exception) -> dict:
    """Format any exception into a structured error dict."""
    if isinstance(error, NeuroError):
        return error.to_dict()
    return {
        "error": "UNHANDLED_ERROR",
        "code": NeuroErrorCode.SYSTEM_UNHANDLED.value,
        "message": str(error),
        "details": {"type": type(error).__name__},
    }
