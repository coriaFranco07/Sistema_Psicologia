from django.contrib.auth.backends import ModelBackend

from .auth_utils import user_has_inactive_profile


class ActiveProfileModelBackend(ModelBackend):
    def user_can_authenticate(self, user):
        return super().user_can_authenticate(user) and not user_has_inactive_profile(user)
