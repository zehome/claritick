# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.comments.models import Comment
from django.contrib.comments.managers import CommentManager

class TicketCommentManager(CommentManager):
    def get_query_set(self):
        qs = super(TicketCommentManager, self).get_query_set().\
                select_related("user")
        return qs

class TicketComment(Comment):
    class Meta:
        verbose_name = u"Reponse"
        verbose_name_plural = u"Reponses"

    internal = models.BooleanField(u"Interne")
    objects = TicketCommentManager()
