from django.contrib.auth.backends import ModelBackend
from .models import AddTailors

class AddTailorsBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = AddTailors.objects.get(username=username)
        except AddTailors.DoesNotExist:
            return None

        if user.check_password(password):
            return user

        return None