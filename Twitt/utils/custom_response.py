import inspect
from typing import Dict, Union
from django.conf import settings
from rest_framework import status
from rest_framework.response import Response


class APIResponse:
    """
    APIResponse class handles the creation of custom API responses for success and failure events.

    Attributes:
        message (Union[str, dict]): The message to be included in the response.
        errors (dict): Dictionary containing any errors that occurred.
        status_code (status): The HTTP status code for the response.
        data (dict): The data to be included in the response.
        for_error (bool): Flag indicating if the response is for an error event.
        general_error (bool): Flag indicating if the error is a general error.

    Methods:
        - response_builder_callback(): Determines whether to build a success or failure response.
        - struct_response(data: dict, success: bool, message: str, errors=None): Constructs the response structure.
        - success_message(): Generates a success message based on the caller function.
        - success(): Creates a custom response for a success event with status code 200.
        - fail(): Creates a custom response for a failure event with a custom status code.

    Note:
        The success method generates a response with status code 200 by default if no status code is provided.
        The fail method handles error messages and can include general error messages defined in settings.
    """

    def __new__(
        cls,
        errors={},
        status_code: status = None,
        data: dict = {},
        message: Union[str, Dict[str, str]] = "",
        for_error: bool = False,
        general_error: bool = False,
    ) -> "APIResponse":
        cls.__init__(
            cls,
            message=message,
            errors=errors,
            status_code=status_code,
            data=data,
            for_error=for_error,
            general_error=general_error,
        )
        instance = super().__new__(cls)
        instance.message = message
        instance.errors = errors
        instance.status_code = status_code
        instance.data = data
        instance.for_error = for_error
        instance.caller_function = inspect.stack()[1].function
        return instance.response_builder_callback()

    def __init__(
        self,
        message: Union[str, dict],
        errors={},
        status_code: status = None,
        data: dict = {},
        for_error: bool = False,
        general_error: bool = False,
    ) -> None:
        self.message = message
        self.errors = errors
        self.status_code = status_code
        self.data = data
        self.for_error = for_error
        self.caller_function = inspect.stack()[1].function
        self.general_error = general_error

    def response_builder_callback(self):
        if self.for_error:
            return self.fail()
        else:
            return self.success()

    def struct_response(
        self, data: dict, success: bool, message: str, errors=None
    ) -> dict:
        response = dict(success=success, message=message, data=data)
        if errors:
            response["errors"] = errors
        return response

    def success_message(self):
        return f'{self.caller_function.replace("_", "-").title()} Successful.'

    def success(self) -> Response:
        """This method will create custom response for success event with response status 200."""
        success_message = self.message if self.message else self.success_message()
        response_data = self.struct_response(
            data=self.data, success=True, message=success_message
        )
        success_status = self.status_code if self.status_code else status.HTTP_200_OK
        return Response(response_data, status=success_status)

    def fail(self) -> Response:
        """This method will create custom response for failure event with custom response status."""
        error_message = (
            self.message[next(iter(self.message))][0]
            if isinstance(self.message, dict)
            else self.message
        )
        if self.general_error:
            error_message = settings.GENERAL_ERROR_MESSAGE
        response_data = self.struct_response(
            data={}, success=False, message=error_message, errors=self.errors
        )
        return Response(response_data, status=self.status_code)
