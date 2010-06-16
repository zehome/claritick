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

        # django.contrib.comment ne permet pas de spécifier un prefix
        savekw = [(k, kw.pop(k)) for k in ("auto_id", "prefix") if k in kw]
        super(CommentForm, self).__init__(*args, **kw)
        for k,v in savekw:
            setattr(self, k, v)

    def get_comment_model(self):
        return TicketComment

    def get_comment_create_data(self):
        # Use the data of the superclass, and add in the title field
        data = super(TicketCommentForm, self).get_comment_create_data()
        data['internal'] = self.cleaned_data['internal']
        return data

    def get_comment_html_id(self):
        if self.prefix:
            return u"%s-comment" % (self.prefix)
        else:
            return u"id_comment"
