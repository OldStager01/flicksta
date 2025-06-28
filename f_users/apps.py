from django.apps import AppConfig


class FUsersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "f_users"
    
    def ready(self):
        import f_users.signals