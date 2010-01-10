# -*- coding: utf-8 -*-

from dojango import forms as df
from claritick.clariadmin.models import Host
from claritick.common.models import Client
from claritick.common.forms import ModelFormTableMixin

class HostForm(df.ModelForm):
    class Meta:
        model = Host

class SearchHostForm(df.ModelForm, ModelFormTableMixin):
    site = df.ModelChoiceField(queryset = Client.objects.all(),
        widget=df.FilteringSelect(attrs={'queryExpr': '*${0}*'}), empty_label='', required=False)

    hostname = df.CharField(required=False)    
    class Meta:
        fields = ('site', 'type', 'hostname', 'os', 'automate', 'ip')
        model = Host
    
