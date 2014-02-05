# -*- coding: utf-8 -*-

from django.contrib.auth.backends import ModelBackend
from loggingauth.signals import auth_username_failed, auth_password_failed
from django.contrib.auth.models import User


class LoggingAuthBackend(ModelBackend):
    """Extends django model auth backend with some database logging
    features.

    This backand will log "invalid user" tries, "wrong password" ones.

    Other cases (success login or logout are logged with django signals)

    Note:
    After AUTHENTIFICATION_BACKEND is changed, you need to reset all sessions:
    Session.objects.all().delete()
    """

    def authenticate(self, username=None, password=None):
        try:
            user = User.objects.get(username=username)
            if user.check_password(password):
                return user
            else:
                auth_password_failed.send(sender=None, user=user)
        except User.DoesNotExist:
            auth_username_failed(sender=None, username=username)
            return None
