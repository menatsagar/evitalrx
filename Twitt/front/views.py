"""
This is a view module to define list, create, update, delete views.
You can define different view properties here.
"""

import random
from typing import Any, Dict

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from itertools import chain
from core.models import Following, Post, User

# from .forms import (
#     UserAuthenticationForm,
#     UserCreationForm,
#     # UserSetPasswordForm,
# )
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated


class UserSignUpView(View):
    template_name = "front/signup.html"

    def get(self, request):
        return render(request, self.template_name)


class UserLoginView(View):
    template_name = "front/login.html"

    def get(self, request):
        return render(request, self.template_name)


class UserFeedView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    template_name = "front/index.html"

    def get(self, request):

        user_profile = request.user

        user_following_list = []
        feed = []

        my_followings = Following.objects.filter(follower=request.user)

        for following in my_followings:
            user_following_list.append(following.target)

        for user in user_following_list:
            feed_lists = Post.objects.filter(user=user)
            feed.append(feed_lists)

        feed_list = list(chain(*feed))

        # user suggestion starts
        all_users = User.objects.all()
        user_following_all = []

        for user in my_followings:
            user_following_all.append(user)

        new_suggestions_list = [
            x for x in list(all_users) if (x not in list(user_following_all))
        ]
        current_user = User.objects.filter(id=request.user.id)
        final_suggestions_list = [
            x for x in list(new_suggestions_list) if (x not in list(current_user))
        ]
        random.shuffle(final_suggestions_list)

        username_profile = []
        username_profile_list = []

        for users in final_suggestions_list:
            username_profile.append(users.id)

        for ids in username_profile:
            profile_lists = User.objects.filter(id=ids)
            username_profile_list.append(profile_lists)

        suggestions_username_profile_list = list(chain(*username_profile_list))
        # breakpoint()
        return render(
            request,
            "front/index.html",
            {
                "user_profile": user_profile,
                "posts": feed_list,
                "suggestions_username_profile_list": suggestions_username_profile_list[
                    :4
                ],
            },
        )
