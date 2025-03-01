from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

app_name = "accounts"

urlpatterns = [
    path("", views.default_view, name="default"),
    path("login/", views.login_view, name="login"),
    path("signup/", views.signup_view, name="signup"),
    path("logout/", views.logout_view, name="logout"),
    path("profile/", views.profile_view, name="profile"),
    path("profile/picture/", views.change_profile_picture_view, name="change_picture"),
    path(
        "profile/information/",
        views.change_profile_information_view,
        name="change_information",
    ),
    path(
        "profile/password/", views.change_profile_password_view, name="change_password"
    ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
