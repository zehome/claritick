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
    if client and client not in user.clients:
        return False

    return True

def filter_form_for_user(form, user):
    if user:
        for key,qs in zip(("client", "assigned_to"), [sort_queryset(user.clients), user.childs]):
            if key in form.base_fields:
                form.base_fields[key].choices = [(x.pk, x) for x in qs]
                form.base_fields[key].choices.insert(0, ("", ""))
