# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from common.exceptions import NoProfileException
from common.models import UserProfile

def user_has_perms_on_client(user, client):
    """
        Verifie si client fait partis des clients de user.
    """
    try:
        if client and client not in user.get_profile().get_clients():
            return False
    except UserProfile.DoesNotExist:
        raise NoProfileException(user)

    return True
