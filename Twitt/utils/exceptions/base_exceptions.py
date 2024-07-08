"""
Module containing a base exception class with data attributes for item and message.
This class is intended for use in situations where additional context 
is needed when handling exceptions.

Classes:
- APIBaseException: A frozen data class inheriting from the built-in Exception class.
"""

from dataclasses import dataclass

from rest_framework import status


@dataclass(frozen=True)
class APIBaseException(Exception):
    """
    A frozen data class inheriting from the built-in Exception class with data attributes for item, message, and status_code.

    Attributes:
    - item (str): The item related to the exception.
    - message (str): The message describing the exception.
    - status_code (int): The HTTP status code associated with the exception.

    Methods:
    - error_data(): Returns a dictionary containing the item and message of the exception.
    - __str__(): Returns a string representation of the exception in the format "item: message".
    """

    item: str
    message: str
    status_code: int = status.HTTP_400_BAD_REQUEST

    def error_data(self) -> dict:
        error_data = {"item": self.item, "message": self.message}
        return error_data

    def __str__(self):
        return "{}: {}".format(self.item, self.message)


class Status400Exception(APIBaseException):
    def __init__(self, item, message):
        super().__init__(item, message, status_code=status.HTTP_400_BAD_REQUEST)


class Status403Exception(APIBaseException):
    def __init__(self, item, message):
        super().__init__(item, message, status_code=status.HTTP_403_FORBIDDEN)


class Status404Exception(APIBaseException):
    def __init__(self, item, message):
        super().__init__(item, message, status_code=status.HTTP_404_NOT_FOUND)


class Status500Exception(APIBaseException):
    def __init__(self, item, message):
        super().__init__(
            item, message, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class Status401Exception(APIBaseException):
    def __init__(self, item, message):
        super().__init__(item, message, status_code=status.HTTP_401_UNAUTHORIZED)
