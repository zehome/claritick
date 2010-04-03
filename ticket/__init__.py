# -*- coding: utf-8 -*-

from django.db.models import signals
from claritick.common.models import ClaritickUser
import gcal

def handle_claritickuser_add_signal(sender, **kwargs):
    """
        Lorsqu'un ClaritickUser est ajouté.
    """
    if kwargs["created"]:
        kwargs["instance"].userprofile_set.create()

signals.post_save.connect(handle_claritickuser_add_signal, sender=ClaritickUser)
