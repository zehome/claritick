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


def filter_form_for_user(form, user, keywords = ("client", "assigned_to")):
     if user:
        for key,qs in zip(keywords, [sort_queryset(user.clients), user.childs]):
            if key in form.base_fields:
                form.base_fields[key].choices = [(x.pk, x) for x in qs]
                form.base_fields[key].choices.insert(0, ("", ""))

def filter_ticket_for_user(form, user, current_assigned_to):
    if user:
        key = "client"
        qs = sort_queryset(user.clients)
        if key in form.base_fields:
            form.base_fields[key].choices = [(x.pk, x) for x in qs]
            form.base_fields[key].choices.insert(0, ("", ""))

        key = "assigned_to"
        qs = user.childs
        if key in form.base_fields:
            form.base_fields[key].choices = [(x.pk, x) for x in qs]
            form.base_fields[key].choices.insert(0, ("", ""))
            if current_assigned_to.pk not in form.base_fields[key].choices:
                # We want to insert this in first place
                form.base_fields[key].choices.insert(0, (current_assigned_to.pk, current_assigned_to))
