# -*- coding: utf8 -*-

from django import forms
from dojango import forms as df
from common.widgets import FilteringSelect
from common.models import ClaritickUser
from django.contrib.auth import SESSION_KEY


class ChuserForm(forms.Form):
    user = df.ModelChoiceField(widget=FilteringSelect(), queryset=ClaritickUser.objects.all())
    def __init__(self, *a, **kw):
        request = kw.pop('request', None)
        user = kw.pop('user', None)
        super(ChuserForm, self).__init__(*a, **kw)

        if request:
            self.request = request

    def save(self):
        user = self.cleaned_data['user']
        self.request.session[SESSION_KEY] = user.id
        self.request.user = user

