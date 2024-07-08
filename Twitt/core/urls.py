from django.urls import path
from .views import (
    CreateReplyCommentAPIView,
    PostRetrieveAPIView,
    RemoveFollowerAPIView,
    UserLoginAPIView,
    UserSignUpAPIView,
    UserLogoutAPIView,
    PostCreateAPIView,
    PostUpdateAPIView,
    PostDeleteAPIView,
    LikeAPIView,
    DisLikeAPIView,
    CreateCommentAPIView,
    DeleteCommentAPIView,
    CreateFollowerAPIView,
)
from django.conf import settings
from django.conf.urls.static import static

app_name = "core"

urlpatterns = [
    path("user/sign-up/", UserSignUpAPIView.as_view(), name="sign_up"),
    path("user/login/", UserLoginAPIView.as_view(), name="login"),
    path("user/logout/", UserLogoutAPIView.as_view(), name="logout"),
]

# Posts url

urlpatterns += [
    path("user/post/create/", PostCreateAPIView.as_view(), name="create_post"),
    path("user/post/update/", PostUpdateAPIView.as_view(), name="update_post"),
    path("user/post/get/", PostRetrieveAPIView.as_view(), name="retrieve_post"),
    path("user/post/delete/", PostDeleteAPIView.as_view(), name="delete_post"),
]


# Likes Url

urlpatterns += [
    path("user/post/like/", LikeAPIView.as_view(), name="like_post"),
    path("user/post/dislike/", DisLikeAPIView.as_view(), name="dislike_post"),
]


# Comments url

urlpatterns += [
    path(
        "user/post/comment/create/",
        CreateCommentAPIView.as_view(),
        name="create_comment",
    ),
    path(
        "user/post/comment/delete/",
        DeleteCommentAPIView.as_view(),
        name="delete_comment",
    ),
    path(
        "user/post/reply-comment/create/",
        CreateReplyCommentAPIView.as_view(),
        name="create_reply_comment",
    ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


urlpatterns += [
    path(
        "user/follower/add/",
        CreateFollowerAPIView.as_view(),
        name="create_follower",
    ),
    path(
        "user/follower/remove/",
        RemoveFollowerAPIView.as_view(),
        name="remove_follower",
    ),
]
