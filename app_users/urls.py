from django.urls import path
from .views import *


app_name = "users"
urlpatterns = [
    path("list/users/", UserListView.as_view(), name="list_user"),
    path("delete/user/<int:pk>/", UserDeleteView.as_view(), name="delete_user"),
    path("register/user/", RegisterUserView.as_view(), name="register_user"),
    path("login/user/", LoginUserView.as_view(), name="login_client"),
    path("confirm-email/<str:token>/", ConfirmEmailView.as_view(), name="confirm_email"),
]