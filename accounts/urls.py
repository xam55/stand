from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token

from .views import ConfirmEmailView, MeView, RegisterView, ResendConfirmationView

app_name = "accounts"

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("resend/", ResendConfirmationView.as_view(), name="resend"),
    path("confirm/<uuid:token>/", ConfirmEmailView.as_view(), name="confirm"),
    path("token/", obtain_auth_token, name="token"),
    path("me/", MeView.as_view(), name="me"),
]
