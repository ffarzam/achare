from django.urls import path

from . import views

app_name = "account"
urlpatterns = [
    path("login/", views.UserLogin.as_view(), name="login"),
    path("login/refresh/", views.RefreshToken.as_view(), name="token_refresh"),
    path("register/", views.UserRegister.as_view(), name="register"),
    path("update/", views.UserUpdate.as_view(), name="update"),
    path("check_phone/", views.CheckUserPhone.as_view(), name="check_phone"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("logout_all/", views.LogoutAll.as_view(), name="logout_all"),
    path("active_login/", views.CheckAllActiveLogin.as_view(), name="active_login"),
    path("selected_logout/", views.SelectedLogout.as_view(), name="selected_logout"),
]
