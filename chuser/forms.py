# -*- coding: utf8 -*-

from django import forms
from dojango import forms as df
from common.widgets import FilteringSelect
from common.models import ClaritickUser


class ChuserForm(forms.Form):
    user = df.ModelChoiceField(widget=FilteringSelect(), queryset=ClaritickUser.objects.all())
