# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from common.exceptions import NoProfileException

def sort_queryset(queryset):
    """
        Tri un queryset par rapport au def __unicode__ de chaque objets.

        Retourne une liste python, pas un queryset.
    """
    objects = list(queryset)
    my_cmp = lambda x, y: cmp(str(x), str(y))
    objects.sort(my_cmp)
    return objects

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

def filter_form_for_user(forms, user):
    from common.models import UserProfile, Client, ClaritickUser

    if user.is_superuser:
        clients = sort_queryset(Client.objects.all())
        claritick_users = ClaritickUser.objects.all()
    else:
        try:
            clients = sort_queryset(user.get_profile().get_clients())
            claritick_users = ClaritickUser.objects.get(pk=user.pk).get_child_user()
        except UserProfile.DoesNotExist:
            raise NoProfileException(user)

    for f in forms:
        for key,qs in zip(("client", "assigned_to"), [clients, claritick_users]):
            if key in f.base_fields:
                f.base_fields[key].choices = [(x.pk, x) for x in qs]
        for key,qs in zip(("client", "assigned_to"), [clients, claritick_users]):
            if key in f.base_fields:
                f.base_fields[key].choices.insert(0, ("", ""))
