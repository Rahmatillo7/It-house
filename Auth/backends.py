from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()

class UsernameOrEmailOrPhoneBackend(ModelBackend):
    """
    Foydalanuvchini username, email yoki phone orqali autentifikatsiya qiladi.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None or password is None:
            return None

        try:
            user = User.objects.filter(username=username).first()

            if not user:
                user = User.objects.filter(email=username).first()

            if not user:
                user = User.objects.filter(phone=username).first()

            if user and user.check_password(password):
                return user

        except User.DoesNotExist:
            return None

        return None
