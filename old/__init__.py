# -*- coding: utf-8 -*-

from ticket.models import Ticket
from common.models import UserProfile, GoogleAccount, ClaritickUser
from django.contrib.auth.models import User
from django.db.models import signals

def handle_claritickuser_add_signal(sender, **kwargs):
    """
    Lorsqu'un ClaritickUser est ajouté.
    """
    if kwargs["created"]:
        kwargs["instance"].userprofile_set.create()

signals.post_save.connect(handle_claritickuser_add_signal, sender=ClaritickUser)
