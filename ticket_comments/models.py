# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.comments.models import Comment

class TicketComment(Comment):
    class Meta:
        verbose_name = u"Reponse"
        verbose_name_plural = u"Reponses"

    internal = models.BooleanField(u"Interne")
