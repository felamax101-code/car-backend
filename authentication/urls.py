from django.urls import path

from .views import DriverRegisterView, LoginView, LogoutView, MeView, RefreshView

urlpatterns = [
    path("register/", DriverRegisterView.as_view(), name="auth-register"),
    path("login/", LoginView.as_view(), name="auth-login"),
    path("refresh/", RefreshView.as_view(), name="auth-refresh"),
    path("logout/", LogoutView.as_view(), name="auth-logout"),
    path("me/", MeView.as_view(), name="auth-me"),
]