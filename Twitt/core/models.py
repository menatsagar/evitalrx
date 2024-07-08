import json
import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


class Activity(models.Model):
    """
    This module will contain activity records of each module.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    mark_as_deleted = models.BooleanField(default=False)

    class Meta:
        abstract = True


class UserManager(BaseUserManager):
    """
    This Following module is used to create a Custom user
    manager in order authentication with email instead of username
    """

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Enter an email address")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        user = self.create_user(email=email, password=password)
        user.is_superuser = True
        user.is_staff = True
        user.is_admin = True
        user.user_type = "Admin"
        user.save(using=self._db)
        return user


class User(AbstractUser, Activity):
    """
    This Following module is for User Creation.
    Inheritance from Abstract User
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField("email address", unique=True)
    is_admin = models.BooleanField(default=False)
    profile_pic = models.ImageField(upload_to="profiles/", blank=True, null=True)
    dob = models.DateField(blank=True, null=True)
    bio_data = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(
        "active",
        default=True,
        help_text=(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )

    objects = UserManager()
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return str(self.email)

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        db_table = "users"


def upload_to(instance, filename):
    return "posts/{filename}".format(filename=filename)


class Post(Activity):
    """
    A class to represent a Post object, inheriting from the Activity class.

    Attributes:
        user (User): The user who created the post.
        image (ImageField): The image associated with the post.
        caption (TextField): The caption or description of the post.
        no_of_likes (IntegerField): The number of likes the post has received.

    Methods:
        __str__: Returns the email of the user who created the post.
    """

    user = models.ForeignKey(
        User,
        verbose_name=_("Post User"),
        on_delete=models.CASCADE,
        related_name="posts",
    )
    image = models.ImageField(upload_to=upload_to)
    caption = models.TextField()
    no_of_likes = models.IntegerField(default=0)

    def __str__(self):
        return self.user.email


class Like(Activity):
    """
    A class to represent a Like object, inheriting from the Activity class.

    Attributes:
        user (User): The user who liked the post.
        post (Post): The post that was liked.

    Methods:
        __str__: Returns the email of the user who liked the post.
    """

    user = models.ForeignKey(
        User,
        verbose_name=_("who liked the post"),
        on_delete=models.CASCADE,
        related_name="all_posts_like",
    )
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="total_likes")

    def __str__(self):
        return self.user.email


class Comment(Activity):
    """
    A class to represent a Comment object, inheriting from the Activity class.

    Attributes:
        user (User): The user who posted the comment.
        post (Post): The post on which the comment is made.
        reply_to (Comment): The comment to which this comment is a reply to.
        comment_text (CharField): The text content of the comment.

    Methods:
        None
    """

    user = models.ForeignKey(
        User,
        verbose_name=_("who Commented on the post"),
        on_delete=models.CASCADE,
        related_name="all_posts_comment",
    )
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="total_Comments"
    )
    reply_to = models.ForeignKey(
        "self",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name="all_replies",
    )
    comment_text = models.CharField(max_length=255)


class Following(Activity):
    """
    A class to represent the relationship between users following each other.

    Attributes:
        target (User): The user being followed.
        follower (User): The user who is following.

    Inherits:
        Activity: A base class for storing activity records of each module.
    """

    target = models.ForeignKey(User, related_name="followers", on_delete=models.CASCADE)
    follower = models.ForeignKey(User, related_name="targets", on_delete=models.CASCADE)

    def __str__(self):
        return self.target.email


@receiver(post_save, sender=Like)
def send_like_notification(sender, instance, created, **kwargs):
    if created:
        user = instance.post.user
        channel_layer = get_channel_layer()
        notification = {
            "type": "send_notification",
            "notification": f"{instance.user.email} liked your post.",
        }
        async_to_sync(channel_layer.group_send)(f"user_{user.id}", notification)


@receiver(post_save, sender=Post)
def send_post_notification(sender, instance, created, **kwargs):
    if created:
        user = instance.user
        followers = Following.objects.filter(target=user)
        channel_layer = get_channel_layer()
        notification = {
            "type": "send_notification",
            "notification": f"{user.email} created a new post.",
        }
        for follower in followers:
            async_to_sync(channel_layer.group_send)(
                f"user_{follower.follower.id}", notification
            )
