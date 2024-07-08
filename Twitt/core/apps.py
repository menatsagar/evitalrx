from django.apps import AppConfig


class CoreConfig(AppConfig):
    """
    Class representing the configuration for the 'core' Django app.

    Attributes:
        default_auto_field (str): The default auto field to use for models in the app.
        name (str): The name of the app.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "core"
