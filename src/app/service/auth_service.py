from fastapi import status
from fastapi.requests import Request
from fastapi.responses import Response

from app.core.security import create_access_token, create_refresh_token, set_cookeies

class AuthService:
    