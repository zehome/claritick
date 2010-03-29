# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from common.exceptions import NoProfileException
from common.models import UserProfile, Client

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

def filter_form_for_user(form, user):

    if user.is_superuser:
        form.base_fields["client"].choices = [(x.pk, x) for x in Client.objects.all()]
    else:
        try:
            form.base_fields["client"].choices = [(x.pk, x) for x in user.get_profile().get_clients()]
        except UserProfile.DoesNotExist:
            raise NoProfileException(user)
    form.base_fields["client"].choices.insert(0, ("", ""))
