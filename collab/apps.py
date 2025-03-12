from django.apps import AppConfig


class CollabConfig(AppConfig):
    name = "collab"

    def ready(self):
        # Avoid database queries here
        pass
