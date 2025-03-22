"""Forms for the application."""
from .auth import (
    LoginForm,
    RegistrationForm,
    ChangePasswordForm,
    ResetPasswordRequestForm,
    ResetPasswordForm
)

__all__ = [
    'LoginForm',
    'RegistrationForm',
    'ChangePasswordForm',
    'ResetPasswordRequestForm',
    'ResetPasswordForm'
]
