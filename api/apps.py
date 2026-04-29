from django.apps import AppConfig


class ApiConfig(AppConfig):
    """
    Django application configuration for the API module.

        Args:
            default_auto_field (str): The default auto field type for models.
            name (str): The name of the application.

        Returns:
            None: This method does not return a value.

    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "api"

    def ready(self):
        # Import tasks to ensure Celery registers them
        """
        Ensures that Celery tasks are registered by importing them.

            Args:
                self: The instance of the class.

            Returns:
                None: This method does not return a value.

        """
