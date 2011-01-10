# -*- coding: utf-8 -*-

from dojango import forms as df
from clariadmin.models import Host, OperatingSystem, HostType
from common.models import Client
from common.forms import ModelFormTableMixin

class HostForm(df.ModelForm):
    class Meta:
        model = Host

class SearchHostForm(df.Form, ModelFormTableMixin):
    site = df.ModelChoiceField(queryset = Client.objects.all(),
        widget=df.FilteringSelect(), empty_label='', required=False)
    type = df.ModelChoiceField(queryset = HostType.objects.all(),
        widget=df.FilteringSelect(), empty_label='', required=False)
    os = df.ModelChoiceField(queryset = OperatingSystem.objects.all(),
        widget=df.FilteringSelect(), empty_label='', required=False)
    hostname = df.CharField(required=False)
    
    class Meta:
        fields = ('site', 'type', 'hostname', 'os', 'ip') # 'automate'
