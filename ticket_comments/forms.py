# -*- coding: utf-8 -*-

from django import forms
from django.contrib.comments.forms import CommentForm
from ticket_comments.models import TicketComment

class TicketCommentForm(CommentForm):
    internal = forms.BooleanField(help_text = u"Commentaire interne (N'est pas diffusé au client final)", required=False)

    def __init__(self, *args, **kw):
        initial_kw = kw.get("initial", {})
        initial_kw.update({"internal": True})
        kw["initial"] = initial_kw
        super(CommentForm, self).__init__(*args, **kw)

    def get_comment_model(self):
        return TicketComment

    def get_comment_create_data(self):
        # Use the data of the superclass, and add in the title field
        data = super(TicketCommentForm, self).get_comment_create_data()
        data['internal'] = self.cleaned_data['internal']
        return data
