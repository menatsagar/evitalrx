"""
Module: lazy_exceptions_module

This module contains the LazyExceptions class, which provides a mechanism to lazily load and retrieve all classes
from a specified module.
"""

import importlib
import inspect
from typing import Any

from django.utils.functional import SimpleLazyObject


class LazyExceptions:
    """
    LazyExceptions class

    This class provides a mechanism to lazily load and retrieve all classes from a specified module using
    SimpleLazyObject.
    """

    def get_all_classes(self, module_name):
        """
        Get all classes from the specified module.

        Args:
            module_name (str): The name of the module from which classes need to be retrieved.

        Returns:
            tuple: A tuple containing all the classes from the specified module.
        """
        module = importlib.import_module(module_name)
        classes = inspect.getmembers(module, inspect.isclass)
        return tuple(class_obj for name, class_obj in classes)

    @property
    def lazy_exceptions(self):
        """
        Get lazy-loaded exceptions.

        Returns:
            tuple: A tuple of SimpleLazyObject instances, each representing the lazily loaded classes
            from the "utils.exceptions.exceptions" module.
        """
        return tuple(
            SimpleLazyObject(
                lambda: self.get_all_classes("utils.exceptions.exceptions")
            )
        )
