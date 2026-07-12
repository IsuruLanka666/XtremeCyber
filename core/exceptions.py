"""
Custom exception classes for XtremeCyber.
"""


class XtremeCyberError(Exception):
    """Base exception for all application-specific errors."""


class ConfigurationError(XtremeCyberError):
    """Raised when application configuration is invalid."""


class DatabaseError(XtremeCyberError):
    """Raised when a database operation fails."""


class DatabaseInitializationError(DatabaseError):
    """Raised when the database cannot be initialized."""


class RepositoryError(DatabaseError):
    """Raised when a repository operation fails."""


class ValidationError(XtremeCyberError):
    """Raised when supplied input is invalid."""


class InvalidTargetError(ValidationError):
    """Raised when a scan target is invalid."""


class InvalidPortRangeError(ValidationError):
    """Raised when a port range is invalid."""


class AuthenticationError(XtremeCyberError):
    """Raised when user authentication fails."""


class ReportGenerationError(XtremeCyberError):
    """Raised when a report cannot be generated."""


class EmailConfigurationError(XtremeCyberError):
    """Raised when email configuration is missing or invalid."""