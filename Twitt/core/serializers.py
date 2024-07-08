from rest_framework import serializers
from .models import Following, User, Post, Comment, Like
from utils.exceptions.exceptions import (
    CommentDoesNotExists,
    EmailAlreadyExistsException,
    MissingCommentException,
    MissingEmailException,
    MissingPasswordException,
    MissingPostIdException,
    PasswordMismatchException,
    PostDoesNotExists,
    UsernameAlreadyExistsException,
)
from rest_framework.exceptions import ValidationError


class SignUpSerializer(serializers.ModelSerializer):
    """
        Serializer for user sign up functionality.
        Handles validation and creation of new user accounts.

        Attributes:
            password (str): The password provided by the user.
            password2 (str): The confirmation password provided by the user.

        Meta:
            model (User): The User model to be used for serialization.
            fields (list): The fields to be included in the serialized data.

        Methods:
            validate(self, data): Validates the input data for sign up.
            create(self, data, *args, **kwargs): Creates a new
    class SignUpSerializer(serializers.ModelSerializer):ser account based on the validated data.
    """

    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "first_name",
            "last_name",
            "password",
            "password2",
        ]

    def validate(self, data):

        if User.objects.filter(email=data["email"]).exists():

            raise EmailAlreadyExistsException(
                item="Email", message="Email Already Exists!"
            )

        if User.objects.filter(username=data["username"]).exists():
            raise UsernameAlreadyExistsException(
                item="Username", message="Username Already Exists!"
            )

        if data["password"] != data["password2"]:
            raise PasswordMismatchException(
                item="confirm password",
                message="Password and confirm password didn't match",
            )

        return data

    def create(self, data, *args, **kwargs):
        password = data.pop("password2")
        user = User.objects.create(**data)
        user.set_password(password)
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    """
    Serializer for validating login credentials.

    Attributes:
        email (EmailField): Field for storing and validating email address.
        password (CharField): Field for storing and validating password.

    Methods:
        validate(self, data): Method to validate the email and password fields.
    """

    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")
        if not email:
            raise MissingEmailException(
                item="Email", message="Please provide valid Email address"
            )

        if not password:
            raise MissingPasswordException(
                item="Password", message="Please provide valid password"
            )
        return data


class PostSerializer(serializers.ModelSerializer):
    """
    Serializer class for serializing Post model data.

    Attributes:
        model: The model class to be serialized (Post).
        fields: The fields to be included in the serialized data (image, caption).
    """

    class Meta:
        model = Post
        fields = ["id", "image", "caption"]


class PostUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating a post.

    Attributes:
        image (ImageField): The image of the post.
        caption (CharField): The caption of the post.

    Methods:
        update(instance, validated_data): Updates the instance of the post with the validated data.
    """

    image = serializers.ImageField(required=False)
    caption = serializers.CharField(required=False)

    class Meta:
        model = Post
        fields = ["image", "caption"]

    def update(self, instance, validated_data):
        caption = validated_data.get("caption")
        image = validated_data.get("image")
        if caption:
            instance.caption = caption
        if image:
            instance.image = image
        instance.save()
        return instance


class LikeSerializer(serializers.ModelSerializer):
    """
    Serializer class for serializing Like model data.

    Attributes:
        model: The model class to be serialized (Like).
        fields: The fields to be included in the serialized data (id, user, post).
    """

    user = serializers.StringRelatedField()
    post = PostSerializer(read_only=True)

    class Meta:
        model = Like
        fields = ["id", "user", "post"]


class CommentSerializer(serializers.ModelSerializer):
    """
    Serializer class for serializing Comment model data.

    Attributes:
        user: StringRelatedField for serializing user data (read-only).
        post: PostSerializer for serializing post data (read-only).
        post_id: UUIDField for storing post id.

    Methods:
        validate: Method to validate the input data for creating a comment.
        create: Method to create a new comment instance.

    Raises:
        MissingPostIdException: If post_id is missing in the input data.
        MissingCommentException: If comment_text is missing in the input data.
        PostDoesNotExists: If the specified post does not exist in the database.
    """

    user = serializers.StringRelatedField(read_only=True)
    post = PostSerializer(read_only=True)
    post_id = serializers.UUIDField()

    class Meta:
        model = Comment
        fields = ["id", "post_id", "user", "post", "comment_text"]

    def validate(self, data):
        post_id = data.get("post_id")
        comment_text = data.get("comment_text")

        if not post_id:
            raise MissingPostIdException(
                item="Post Id", message="Please enter post id."
            )

        if not comment_text:
            raise MissingCommentException(item="comment", message="Please add comment.")

        return data

    def create(self, data):
        post_id = data.pop("post_id")
        post = Post.objects.filter(id=post_id).first()
        if not post:
            raise PostDoesNotExists(item="Post", message="Post does not exists")
        comment = Comment.objects.create(
            post=post, user=self.context.get("user"), **data
        )
        return comment


class ReplyCommentSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a reply to a comment.

    Attributes:
        parent_comment (ReadOnlyField): A read-only field to display the text of the parent comment being replied to.

    Meta:
        model (Comment): The model that the serializer is based on.
        fields (list): The fields to include in the serialized output.
        extra_kwargs (dict): Additional keyword arguments for the fields.

    Methods:
        create(self, data): Create a new reply comment based on the provided data.
    """

    parent_comment = serializers.ReadOnlyField(source="reply_to.comment_text")

    class Meta:
        model = Comment
        fields = ["id", "parent_comment", "comment_text", "reply_to"]
        extra_kwargs = {"reply_to": {"write_only": True}}

    def create(self, data):
        try:

            parent_comment = data.get("reply_to")
            post = parent_comment.post
            reply_comment = Comment.objects.create(
                reply_to=parent_comment,
                post=post,
                user=self.context.get("user"),
                comment_text=data.get("comment_text"),
            )
            return reply_comment
        except Comment.DoesNotExist as ce:
            raise CommentDoesNotExists(
                item="Comment", message="comment does not exists"
            )


class FollowingSerializer(serializers.ModelSerializer):
    """
    Serializer class for serializing Following objects.

    Attributes:
        target (ReadOnlyField): A read-only field representing the username of the user being followed.
        follower (ReadOnlyField): A read-only field representing the username of the user who is following.

    Meta:
        model (Following): The model class that the serializer is based on.
        fields (list): The fields to include in the serialized output.

    """

    target = serializers.ReadOnlyField(source="target.username")
    follower = serializers.ReadOnlyField(source="follower.username")

    class Meta:
        model = Following
        fields = ["target", "follower"]
