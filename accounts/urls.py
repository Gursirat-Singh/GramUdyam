from django.urls import path
from accounts import views

app_name = "accounts"

urlpatterns = [
    path("register/", views.register_view, name="register"),
    path("login/", views.EntrepreneurLoginView.as_view(), name="login"),
    path("logout/", views.EntrepreneurLogoutView.as_view(), name="logout"),
    path("profile/", views.profile_view, name="profile"),
    path("password-reset/", views.EntrepreneurPasswordResetView.as_view(), name="password_reset"),
    path("password-reset/done/", views.EntrepreneurPasswordResetDoneView.as_view(), name="password_reset_done"),
]
