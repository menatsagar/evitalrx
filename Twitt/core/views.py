from django.conf import settings
from django.contrib.auth import authenticate
from utils.validators import is_valid_uuid
from utils.exceptions.exceptions import (
    InvalidUUIDException,
    MissingFollowerIdException,
    MissingPostIdException,
    UserDoesNotExists,
    UserNotAuthenticated,
    PostDoesNotExists,
)
from utils.custom_response import APIResponse
from utils.custom_permissions import (
    CanDeleteComment,
    CanPerformRetrieveOrUpdateOrDelete,
)
from .models import Post, User, Like, Comment, Following
from .serializers import (
    FollowingSerializer,
    LoginSerializer,
    PostUpdateSerializer,
    ReplyCommentSerializer,
    SignUpSerializer,
    PostSerializer,
    LikeSerializer,
    CommentSerializer,
)
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.parsers import MultiPartParser, FormParser


class UserSignUpAPIView(APIView):
    """
    UserSignUpAPIView class handles the user sign-up functionality through APIView.

    Attributes:
        serializer_class: The serializer class used for user sign-up data validation and serialization.

    Methods:
        - post(request): Handles the POST request for user sign-up. Validates the input data using the serializer, creates a new user if valid, and returns a custom API response.

    Note:
        The class utilizes the SignUpSerializer for user sign-up data handling and validation.
        It catches specific exceptions for custom error responses and handles unknown errors with a generic message.
    """

    serializer_class = SignUpSerializer

    def post(self, request):
        try:

            serializer_obj = self.serializer_class(data=request.data)

            if serializer_obj.is_valid():
                serializer_obj.save()

                return APIResponse(
                    data=serializer_obj.data,
                    message="User created successfully",
                    status_code=status.HTTP_201_CREATED,
                )
            return APIResponse(
                errors=serializer_obj.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
                for_error=True,
                message="data validation error",
            )
        except settings.LAZY_EXCEPTIONS as ce:

            return APIResponse(
                status_code=ce.status_code,
                errors=ce.error_data(),
                message=ce.message,
                for_error=True,
            )

        except Exception as ce:

            return APIResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                for_error=True,
                message=f"Unknown error occurred in User signup: {ce}",
            )


class UserLoginAPIView(TokenObtainPairView):
    """
    This class represents an API view for user login functionality.

    Attributes:
        serializer_class (Serializer): A serializer class for validating login credentials.

    Methods:
        post(self, request, *args, **kwargs): Method to handle POST requests for user login.
            It validates the user credentials, authenticates the user, generates a token, and returns a response.

    Raises:
        UserDoesNotExists: If the user with the provided email does not exist.
        UserNotAuthenticated: If the provided email or password is incorrect.
        Exception: If an unknown error occurs during the user login process.
    """

    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        try:

            serializer_obj = self.serializer_class(data=request.data)
            if serializer_obj.is_valid():
                email = request.data["email"]
                password = request.data["password"]

                user = User.objects.filter(email=email).first()
                if not user:
                    raise UserDoesNotExists(
                        item="User not Exists",
                        message=f"User does not exists",
                    )

                user = authenticate(
                    request,
                    username=email,
                    password=password,
                )

                if user is None:
                    raise UserNotAuthenticated(
                        item="Authentication",
                        message="Email or password is incorrect.",
                    )
                if user:
                    token = RefreshToken.for_user(user)
                    token_data = {
                        "refresh": str(token),
                        "access": str(token.access_token),
                    }

                    return APIResponse(
                        data=token_data,
                        status_code=status.HTTP_200_OK,
                        message="User Successfully Logged In",
                    )

        except settings.LAZY_EXCEPTIONS as ce:

            return APIResponse(
                status_code=ce.status_code,
                errors=ce.error_data(),
                message=ce.message,
                for_error=True,
            )

        except Exception as ce:

            return APIResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                for_error=True,
                message=f"Unknown error occurred in User Login: {ce}",
            )


class UserLogoutAPIView(APIView):
    """
        Class representing an API view for user logout functionality.

    Attributes:
        authentication_classes (list): A list of authentication classes required for this view.
        permission_classes (list): A list of permission classes required for this view.

    Methods:
        post(self, request: Request, *args, **kwargs) -> Response: Method to handle POST requests for user logout.
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [
        IsAuthenticated,
    ]

    def post(self, request: Request, *args, **kwargs) -> Response:

        try:

            refresh_token = request.data.get("refresh")
            token = RefreshToken(refresh_token)
            token.blacklist()
            return APIResponse(
                status_code=status.HTTP_200_OK,
                message="User Successfully Logged out",
            )

        except settings.LAZY_EXCEPTIONS as ce:
            return APIResponse(
                status_code=ce.status_code,
                errors=ce.error_data(),
                message=ce.message,
                for_error=True,
            )

        except Exception as ce:
            return APIResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                for_error=True,
                message=str(ce),
            )


class PostCreateAPIView(APIView):
    """
    PostCreateAPIView class handles the creation of a new Post instance through a POST request.

    Attributes:
        authentication_classes (list): List of authentication classes required for the view (JWTAuthentication).
        permission_classes (list): List of permission classes required for the view (IsAuthenticated).
        serializer_class: The serializer class used for serializing and deserializing Post data (PostSerializer).
        parser_classes (tuple): Tuple of parser classes used for parsing the request data (MultiPartParser, FormParser).

    Methods:
        post(self, request, *args, **kwargs): Handles POST requests to create a new Post instance.
            - Validates the incoming data using the serializer_class.
            - If data is valid, saves the Post instance with the authenticated user.
            - Returns a success response with the serialized data if successful.
            - Returns an error response with validation errors if data is invalid.
            - Catches specific exceptions and returns appropriate error responses.

    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = PostSerializer
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        try:
            data = request.data
            user = request.user

            serializer_obj = self.serializer_class(data=data)

            if serializer_obj.is_valid():
                serializer_obj.save(user=user)
                return APIResponse(
                    data=serializer_obj.data,
                    message="Post created successfully",
                    status_code=status.HTTP_201_CREATED,
                )
            return APIResponse(
                errors=serializer_obj.errors,
                for_error=True,
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
            )
        except settings.LAZY_EXCEPTIONS as ce:
            return APIResponse(
                status_code=ce.status_code,
                errors=ce.error_data(),
                message=ce.message,
                for_error=True,
            )

        except Exception as ce:
            return APIResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                for_error=True,
                message=str(ce),
            )


class PostUpdateAPIView(APIView):
    """
        Class representing an API view for updating a post.

    Attributes:
        authentication_classes (list): List of authentication classes required for this view.
        permission_classes (list): List of permission classes required for this view.
        serializer_class (Serializer): Serializer class used for serializing and deserializing data.
        parser_classes (tuple): Tuple of parser classes used for parsing the request data.

    Methods:
        post(request, *args, **kwargs): Method to handle POST requests for updating a post.

    Raises:
        PostDoesNotExists: If the requested post does not exist.
        settings.LAZY_EXCEPTIONS: If a lazy exception is raised.
        Exception: If any other exception is raised during the request processing.
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = PostUpdateSerializer
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        try:
            data = request.data
            post_id = data.get("post_id")
            post = Post.objects.filter(id=post_id).first()
            if not post:
                raise PostDoesNotExists(item="Post", message="Post does not exists.")
            serializer_obj = self.serializer_class(data=data, instance=post)
            if serializer_obj.is_valid():
                serializer_obj.save()
                return APIResponse(
                    data=serializer_obj.data,
                    message="Post updated successfully",
                    status_code=status.HTTP_200_OK,
                )

            return APIResponse(
                errors=serializer_obj.errors,
                for_error=True,
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
            )
        except settings.LAZY_EXCEPTIONS as ce:
            return APIResponse(
                status_code=ce.status_code,
                errors=ce.error_data(),
                message=ce.message,
                for_error=True,
            )

        except Exception as ce:
            return APIResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                for_error=True,
                message=str(ce),
            )


class PostRetrieveAPIView(APIView):
    """
    PostRetrieveAPIView

    This class defines an API view for retrieving a specific post. It inherits from the APIView class of Django REST framework.
    It requires JWT authentication for access and permission from IsAuthenticated and CanPerformRetrieveOrUpdateOrDelete classes.
    The serializer used for serializing the Post model data is PostSerializer.

    Attributes:
        authentication_classes (list): A list containing JWTAuthentication class for authentication.
        permission_classes (list): A list containing IsAuthenticated and CanPerformRetrieveOrUpdateOrDelete classes for permission.
        serializer_class (class): The serializer class used for serializing Post model data.

    Methods:
        get(self, request, *args, **kwargs): Method to handle GET requests for retrieving a specific post.
            It retrieves the post_id from query parameters, fetches the post object from the database, and serializes the data.
            If the post does not exist, it raises a PostDoesNotExists exception.
            Returns an APIResponse with the serialized data and a success message if successful.
            If any exception is raised, it returns an appropriate APIResponse with error details.

    Exceptions:
        PostDoesNotExists: Raised when the requested post does not exist in the database.

    Raises:
        Any exception that occurs during the GET request handling process will be caught and appropriate error response will be returned.

    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, CanPerformRetrieveOrUpdateOrDelete]
    serializer_class = PostSerializer

    def get(self, request, *args, **kwargs):
        try:
            post_id = request.query_params.get("post_id")
            post = Post.objects.filter(id=post_id).first()
            if not post:
                raise PostDoesNotExists(item="Post", message="Post does not exists.")

            serializer = self.serializer_class(post)
            return APIResponse(
                data=serializer.data, message="success", status_code=status.HTTP_200_OK
            )

        except settings.LAZY_EXCEPTIONS as ce:
            return APIResponse(
                status_code=ce.status_code,
                errors=ce.error_data(),
                message=ce.message,
                for_error=True,
            )

        except Exception as ce:
            return APIResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                for_error=True,
                message=str(ce),
            )


class PostDeleteAPIView(APIView):
    """
    PostDeleteAPIView

    This class defines an API view for deleting a post. It requires JWT authentication for access and permission from the user to retrieve, update, or delete the post. The 'delete' method handles the deletion process by first checking the validity of the post ID and then deleting the post if it exists. It raises specific exceptions for missing post ID, invalid post ID, and non-existing post. It returns a custom API response indicating the success or failure of the deletion operation.

    Attributes:
        authentication_classes (list): A list of authentication classes, in this case, JWTAuthentication.
        permission_classes (list): A list of permission classes, including IsAuthenticated and CanPerformRetrieveOrUpdateOrDelete.

    Methods:
        delete(self, request): Handles the deletion of a post by verifying the post ID, checking its validity, and deleting the post if it exists. It returns a custom API response based on the success or failure of the deletion operation.

    Raises:
        MissingPostIdException: If the post ID is missing in the request.
        InvalidUUIDException: If the post ID is not a valid UUID.
        PostDoesNotExists: If the post with the given ID does not exist.

    Returns:
        APIResponse: A custom response indicating the success or failure of the post deletion operation.
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, CanPerformRetrieveOrUpdateOrDelete]

    def delete(self, request):
        try:
            post_id = request.query_params.get("post_id")
            if not post_id:
                raise MissingPostIdException(
                    item="Post Id", message="Please enter post id."
                )
            if not is_valid_uuid(post_id):
                raise InvalidUUIDException(
                    item="Invalid Post Id", message="Post Id is not a valid UUID"
                )
            post = Post.objects.filter(id=post_id).first()
            if not post:
                raise PostDoesNotExists(item="Post", message="Post does not exists.")
            post.delete()
            return APIResponse(
                message="Post Deleted Successfully",
                status_code=status.HTTP_200_OK,
            )

        except settings.LAZY_EXCEPTIONS as ce:
            return APIResponse(
                status_code=ce.status_code,
                errors=ce.error_data(),
                message=ce.message,
                for_error=True,
            )

        except Exception as ce:
            return APIResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                for_error=True,
                message=str(ce),
            )


class LikeAPIView(APIView):
    """
        Class representing an API view for handling like functionality.

    Attributes:
        authentication_classes (list): List of authentication classes required for this view.
        permission_classes (list): List of permission classes required for this view.
        serializer_class (class): Serializer class used for serializing Like model data.

    Methods:
        post(self, request): Method to handle POST requests for liking a post. It validates the post_id, checks if the post exists, and creates a Like instance if the user has not already liked the post. Returns appropriate APIResponse based on the outcome.

    Raises:
        MissingPostIdException: If the post_id is missing in the request data.
        InvalidUUIDException: If the post_id is not a valid UUID.
        PostDoesNotExists: If the post with the given post_id does not exist.
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = LikeSerializer

    def post(self, request):

        try:
            post_id = request.data.get("post_id")
            if not post_id:
                raise MissingPostIdException(
                    item="Post Id", message="Please enter post id."
                )
            if not is_valid_uuid(post_id):
                raise InvalidUUIDException(
                    item="Invalid Post Id", message="Post Id is not a valid UUID"
                )
            post = Post.objects.filter(id=post_id).first()

            if not post:
                raise PostDoesNotExists(item="Post", message="Post does not exists.")

            already_liked = Like.objects.filter(user=request.user, post=post).exists()
            if not already_liked:
                like = Like.objects.create(user=request.user, post=post)
                post.no_of_likes += 1
                post.save()
                serializer = self.serializer_class(like)
                return APIResponse(
                    data=serializer.data,
                    message="Liked Post Successfully",
                    status_code=status.HTTP_201_CREATED,
                )
            return APIResponse(
                message="Already Liked Post",
                status_code=status.HTTP_200_OK,
            )

        except settings.LAZY_EXCEPTIONS as ce:
            return APIResponse(
                status_code=ce.status_code,
                errors=ce.error_data(),
                message=ce.message,
                for_error=True,
            )

        except Exception as ce:
            return APIResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                for_error=True,
                message=str(ce),
            )


class DisLikeAPIView(APIView):
    """
        Class representing an API view for disliking a post.

    Attributes:
        authentication_classes (list): List of authentication classes required for this view.
        permission_classes (list): List of permission classes required for this view.

    Methods:
        post(self, request, *args, **kwargs): Method to handle POST requests for disliking a post. It checks for valid post_id, if the post exists, and if the user has already liked the post. It then removes the like and returns a success response. Handles exceptions and returns appropriate APIResponse.

    Raises:
        MissingPostIdException: If the post_id is missing in the request data.
        InvalidUUIDException: If the post_id is not a valid UUID.
        PostDoesNotExists: If the post with the given post_id does not exist.
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            post_id = request.data.get("post_id")
            if not post_id:
                raise MissingPostIdException(
                    item="Post Id", message="Please enter post id."
                )
            if not is_valid_uuid(post_id):
                raise InvalidUUIDException(
                    item="Invalid Post Id", message="Post Id is not a valid UUID"
                )
            post = Post.objects.filter(id=post_id).first()

            if not post:
                raise PostDoesNotExists(item="Post", message="Post does not exists.")

            like = Like.objects.filter(user=request.user, post=post).first()

            if not like:
                return APIResponse(
                    message="you have not liked post earlier or already disliked the post.",
                    status_code=status.HTTP_200_OK,
                )
            like.delete()
            return APIResponse(
                message="Disliked Post Successfully",
                status_code=status.HTTP_200_OK,
            )
        except settings.LAZY_EXCEPTIONS as ce:
            return APIResponse(
                status_code=ce.status_code,
                errors=ce.error_data(),
                message=ce.message,
                for_error=True,
            )

        except Exception as ce:
            return APIResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                for_error=True,
                message=str(ce),
            )


class CreateCommentAPIView(APIView):
    """
    APIView class for creating a new comment.

    Attributes:
        authentication_classes: List of authentication classes required for this view.
        permission_classes: List of permission classes required for this view.
        serializer_class: Serializer class used for serializing the input data.

    Methods:
        post: Method to handle POST requests for creating a new comment.

    Raises:
        LazyRelatedObjectDoesNotExist: If a lazy-related object does not exist.
        Exception: If an unexpected exception occurs during the request processing.
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = CommentSerializer

    def post(self, request):
        try:
            serializer_obj = self.serializer_class(
                data=request.data, context={"user": request.user}
            )

            if serializer_obj.is_valid():
                serializer_obj.save()
                return APIResponse(
                    data=serializer_obj.data,
                    status_code=status.HTTP_201_CREATED,
                    message="Comment created successfully",
                )
            return APIResponse(
                errors=serializer_obj.errors,
                for_error=True,
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
            )
        except settings.LAZY_EXCEPTIONS as ce:
            return APIResponse(
                status_code=ce.status_code,
                errors=ce.error_data(),
                message=ce.message,
                for_error=True,
            )

        except Exception as ce:
            return APIResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                for_error=True,
                message=str(ce),
            )


class DeleteCommentAPIView(APIView):
    """
    This class defines an API view for deleting a comment. It inherits from the APIView class provided by Django REST framework.
    The class has the following attributes:
        - authentication_classes: List containing JWTAuthentication for authenticating the user.
        - permission_classes: List containing IsAuthenticated and CanDeleteComment for permission control.

    The class has a delete method that handles the DELETE request to delete a comment. It performs the following actions:
        - Retrieves the comment_id from the request data.
        - Queries the Comment model to find the comment with the given comment_id.
        - If the comment exists, deletes the comment and returns a success response using the APIResponse class.
        - If the comment does not exist, returns an error response indicating that the comment was not found.
        - Handles exceptions by returning appropriate error responses.

    This class provides functionality to delete a comment based on the comment_id provided in the request data.
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, CanDeleteComment]

    def delete(self, request):
        try:
            comment_id = request.data.get("comment_id")
            comment = Comment.objects.filter(id=comment_id).first()
            if comment:
                comment.delete()
                return APIResponse(
                    message="Comment deleted successfully",
                    status_code=status.HTTP_200_OK,
                )
            return APIResponse(
                for_error=True,
                message="Comment not found.",
                status_code=status.HTTP_200_OK,
            )
        except settings.LAZY_EXCEPTIONS as ce:
            return APIResponse(
                status_code=ce.status_code,
                errors=ce.error_data(),
                message=ce.message,
                for_error=True,
            )

        except Exception as ce:
            return APIResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                for_error=True,
                message=str(ce),
            )


class CreateReplyCommentAPIView(APIView):
    """
    APIView for creating a reply to a comment.

    Attributes:
        authentication_classes (list): List of authentication classes required for this APIView.
        permission_classes (list): List of permission classes required for this APIView.
        serializer_class (ReplyCommentSerializer): Serializer class used for serializing the data.

    Methods:
        post(self, request): Method to handle POST requests for creating a reply comment.
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = ReplyCommentSerializer

    def post(self, request):
        try:
            serializer_obj = self.serializer_class(
                data=request.data, context={"user": request.user}
            )
            if serializer_obj.is_valid():
                serializer_obj.save()
                return APIResponse(
                    data=serializer_obj.data,
                    message="Reply comment created successfully",
                    status_code=status.HTTP_201_CREATED,
                )
            return APIResponse(
                errors=serializer_obj.errors,
                for_error=True,
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
            )
        except settings.LAZY_EXCEPTIONS as ce:
            return APIResponse(
                status_code=ce.status_code,
                errors=ce.error_data(),
                message=ce.message,
                for_error=True,
            )

        except Exception as ce:
            return APIResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                for_error=True,
                message=str(ce),
            )


class CreateFollowerAPIView(APIView):
    """
    CreateFollowerAPIView

    This class defines an API view for creating a follower relationship between users. It handles the POST method to create a new follower relationship. The user must be authenticated using JWT authentication to access this view.

    Attributes:
        authentication_classes (list): List of authentication classes, JWTAuthentication in this case.
        permission_classes (list): List of permission classes, IsAuthenticated in this case.
        serializer_class: The serializer class used for serializing the data, FollowingSerializer in this case.

    Methods:
        - post(self, request): Handles the POST request to create a follower relationship. It validates the input data, checks if the follower is already followed, creates a new follower relationship, and returns a custom API response.

    Exceptions:
        - MissingFollowerIdException: Raised when the follower_id is missing in the request data.
        - InvalidUUIDException: Raised when the follower_id is not a valid UUID.
        - settings.LAZY_EXCEPTIONS: Lazy exception handling for custom exceptions defined in settings.
        - Exception: Generic exception handling for internal server errors.

    Note:
        The class uses custom APIResponse for generating custom responses based on success or failure events. It follows RESTful conventions for creating a new resource.

    Inherits:
        APIView: A Django REST framework class for defining API views.

    Dependencies:
        - Django: Django framework for web development.
        - Django REST framework: Django REST framework for building APIs.
        - JWTAuthentication: Token-based authentication using JSON Web Tokens.
        - FollowingSerializer: Serializer class for the Following model.

    Usage:
        This class is used as a view to create a follower relationship between users in the API.

    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = FollowingSerializer

    def post(self, request):

        try:
            follower_id = request.data.get("follower_id")
            if not follower_id:
                raise MissingFollowerIdException(
                    item="Follower Id", message="Please enter follower id."
                )
            if not is_valid_uuid(follower_id):
                raise InvalidUUIDException(
                    item="Invalid follower Id",
                    message="follower Id is not a valid UUID",
                )
            already_followed = Following.objects.filter(
                target=request.user, follower__id=follower_id
            ).exists()

            if already_followed:
                return APIResponse(
                    message="Already followed", status_code=status.HTTP_200_OK
                )
            follower = User.objects.get(id=follower_id)

            following = Following.objects.create(target=request.user, follower=follower)
            serializer = self.serializer_class(following)
            return APIResponse(
                data=serializer.data,
                message=f"Successfully followed {follower.username}",
                status_code=status.HTTP_201_CREATED,
            )

        except settings.LAZY_EXCEPTIONS as ce:
            return APIResponse(
                status_code=ce.status_code,
                errors=ce.error_data(),
                message=ce.message,
                for_error=True,
            )

        except Exception as ce:
            return APIResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                for_error=True,
                message=str(ce),
            )


class RemoveFollowerAPIView(APIView):
    """
    A class-based view to handle the removal of a follower relationship between users.

    Attributes:
        authentication_classes (list): List of authentication classes required for this view.
        permission_classes (list): List of permission classes required for this view.
        serializer_class (Serializer): The serializer class used for serializing/deserializing data.

    Methods:
        post(self, request): Handles the POST request to remove a follower relationship between users.
            - Validates the input data for follower_id and following_id.
            - Checks if the provided IDs are valid UUIDs.
            - Retrieves the follower's username and deletes the follower relationship.
            - Returns a custom API response indicating the success or failure of the operation.

    Raises:
        MissingFollowerIdException: When both follower_id and following_id are missing in the request data.
        InvalidUUIDException: When the provided follower_id or following_id is not a valid UUID.
        Any other exception: Handles any other unexpected exceptions and returns a generic error response.

    Note:
        This view requires the user to be authenticated and provides a custom response format for success and failure events.
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = FollowingSerializer

    def post(self, request):

        try:
            follower_id = request.data.get("follower_id")
            following_id = request.data.get("following_id")
            if not (follower_id or following_id):
                raise MissingFollowerIdException(
                    item="Follower Id",
                    message="Please Provide follower id or Following id",
                )
            if follower_id and not is_valid_uuid(follower_id):
                raise InvalidUUIDException(
                    item="Invalid follower Id", message="Post Id is not a valid UUID"
                )

            if following_id and not is_valid_uuid(following_id):
                raise InvalidUUIDException(
                    item="Invalid following Id",
                    message="following Id is not a valid UUID",
                )
            follower_name = None
            serializer = None
            data = None
            if following_id:
                following = Following.objects.get(id=following_id)
                follower_name = following.follower.username
                serializer = self.serializer_class(following)
                following.delete()

            if follower_id:
                following = Following.objects.filter(
                    target=request.user, follower__id=follower_id
                ).first()
                if following:
                    follower_name = following.follower.username
                    serializer = self.serializer_class(following)
                    following.delete()
            if serializer is not None:
                data = serializer.data
                return APIResponse(
                    data=data,
                    message=f"Successfully unfollowed { follower_name }",
                    status_code=status.HTTP_200_OK,
                )
            return APIResponse(
                message="Already unfollowed.",
                status_code=status.HTTP_200_OK,
            )
        except settings.LAZY_EXCEPTIONS as ce:
            return APIResponse(
                status_code=ce.status_code,
                errors=ce.error_data(),
                message=ce.message,
                for_error=True,
            )

        except Exception as ce:
            return APIResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                for_error=True,
                message=str(ce),
            )
