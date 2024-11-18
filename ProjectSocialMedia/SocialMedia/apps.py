from django.apps import AppConfig


class SocialmediaConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "SocialMedia"

    def ready(self):
        # Import the signals when the app is ready
        import SocialMedia.signals

