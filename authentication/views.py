from django.conf import settings
from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import DriverRegisterSerializer, UserSerializer

REFRESH_COOKIE_NAME = "refresh_token"

# Cookie only ever travels to the auth endpoints, never to the rest of the API.
REFRESH_COOKIE_KWARGS = {
    "httponly": True,
    "secure": not settings.DEBUG,              # True (HTTPS-only) in production
    "samesite": "None" if not settings.DEBUG else "Lax",
    "path": "/api/auth/",
}


def _issue_tokens(user):
    """Create a refresh + access token pair for a user."""
    refresh = RefreshToken.for_user(user)
    return str(refresh), str(refresh.access_token)


class DriverRegisterView(APIView):
    """
    POST /api/auth/register/
    { "username": "...", "email": "...", "password": "..." }

    Public endpoint. Creates a DRIVER account and logs them straight in.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = DriverRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        refresh_str, access_str = _issue_tokens(user)
        response = Response(
            {"user": UserSerializer(user).data, "access": access_str},
            status=status.HTTP_201_CREATED,
        )
        response.set_cookie(REFRESH_COOKIE_NAME, refresh_str, **REFRESH_COOKIE_KWARGS)
        return response


class LoginView(APIView):
    """
    POST /api/auth/login/
    { "username": "...", "password": "..." }

    One endpoint for every role — driver, gate operator, admin — since
    they all authenticate the same way; only their `role` differs.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(request, username=username, password=password)

        if user is None:
            return Response(
                {"detail": "Invalid credentials."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        refresh_str, access_str = _issue_tokens(user)
        response = Response(
            {"user": UserSerializer(user).data, "access": access_str},
            status=status.HTTP_200_OK,
        )
        response.set_cookie(REFRESH_COOKIE_NAME, refresh_str, **REFRESH_COOKIE_KWARGS)
        return response


class RefreshView(APIView):
    """
    POST /api/auth/refresh/   (no body — reads the httpOnly cookie)

    Frontend calls this silently whenever an API call returns 401,
    then retries the original request with the new access token.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        refresh_str = request.COOKIES.get(REFRESH_COOKIE_NAME)
        if not refresh_str:
            return Response(
                {"detail": "No refresh token."}, status=status.HTTP_401_UNAUTHORIZED
            )

        try:
            refresh = RefreshToken(refresh_str)
            access_str = str(refresh.access_token)
        except TokenError:
            return Response(
                {"detail": "Refresh token invalid or expired."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        return Response({"access": access_str}, status=status.HTTP_200_OK)


class LogoutView(APIView):
    """
    POST /api/auth/logout/

    Blacklists the refresh token (requires
    rest_framework_simplejwt.token_blacklist in INSTALLED_APPS) and
    clears the cookie so it can't be reused.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_str = request.COOKIES.get(REFRESH_COOKIE_NAME)
        if refresh_str:
            try:
                RefreshToken(refresh_str).blacklist()
            except TokenError:
                pass  # already invalid/expired — nothing left to blacklist

        response = Response(status=status.HTTP_204_NO_CONTENT)
        response.delete_cookie(REFRESH_COOKIE_NAME, path="/api/auth/")
        return response


class MeView(APIView):
    """GET /api/auth/me/ — the logged-in user's own profile."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)