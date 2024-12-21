from django.contrib.auth.backends import ModelBackend
from users.models import CustomUser

class PhoneNumberAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = CustomUser.objects.get(username=username)  # username is phone_number
            if user.check_password(password):
                return user
        except CustomUser.DoesNotExist:
            return None
