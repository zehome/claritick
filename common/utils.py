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

def filter_form_for_user(form, user):
    from common.models import UserProfile, Client, ClaritickUser
    if user.is_superuser:
        if "client" in form.base_fields:
            form.base_fields["client"].choices = [(x.pk, x) for x in sort_queryset(Client.objects.all())]
        if "assigned_to" in form.base_fields:
            form.base_fields["assigned_to"].choices = [(x.pk, x) for x in ClaritickUser.objects.all()]
    else:
        try:
            if "client" in form.base_fields:
                form.base_fields["client"].choices = [(x.pk, x) for x in sort_queryset(user.get_profile().get_clients())]
            if "assigned_to" in form.base_fields:
                form.base_fields["assigned_to"].choices = [(x.pk, x) for x in ClaritickUser.objects.get(pk=user.pk).get_child_users()]
        except UserProfile.DoesNotExist:
            raise NoProfileException(user)
    if "client" in form.base_fields:
        form.base_fields["client"].choices.insert(0, ("", ""))
    if "assigned_to" in form.base_fields:
        form.base_fields["assigned_to"].choices.insert(0, ("", ""))
