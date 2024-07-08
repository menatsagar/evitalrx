from django.urls import path
from .views import UserSignUpView, UserLoginView, UserFeedView

app_name = "front"

urlpatterns = [
    path("sign-up/", UserSignUpView.as_view(), name="sign_up"),
    path("login/", UserLoginView.as_view(), name="login"),
    path("feed/", UserFeedView.as_view(), name="feed"),
    # path("logout/", UserLogOutView.as_view(), name="logout"),
]
