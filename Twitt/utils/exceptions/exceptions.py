"""
Module containing custom exceptions related to company setup, Object does not exists, or duplicate objects and many more scenarios.

"""

from django.utils.translation import gettext_lazy as _

from utils.exceptions import base_exceptions


class MissingEmailException(base_exceptions.Status400Exception):
    pass


class MissingPasswordException(base_exceptions.Status400Exception):
    pass


class EmailAlreadyExistsException(base_exceptions.Status400Exception):
    pass


class UsernameAlreadyExistsException(base_exceptions.Status400Exception):
    pass


class PasswordMismatchException(base_exceptions.Status400Exception):
    pass


class UserDoesNotExists(base_exceptions.Status404Exception):
    pass


class PostDoesNotExists(base_exceptions.Status404Exception):
    pass


class CommentDoesNotExists(base_exceptions.Status404Exception):
    pass


class UserNotAuthenticated(base_exceptions.Status401Exception):
    pass


class MissingPostIdException(base_exceptions.Status400Exception):
    pass


class InvalidUUIDException(base_exceptions.Status400Exception):
    pass


class MissingLikeIdException(base_exceptions.Status400Exception):
    pass


class MissingCommentException(base_exceptions.Status400Exception):
    pass


class MissingFollowerIdException(base_exceptions.Status400Exception):
    pass
