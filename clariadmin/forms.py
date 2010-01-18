# -*- coding: utf-8 -*-

from dojango import forms as df
from claritick.clariadmin.models import Host, OperatingSystem, HostType
from claritick.common.models import Client
from claritick.common.forms import ModelFormTableMixin

class HostForm(df.ModelForm):
    class Meta:
        model = Host

class SearchHostForm(df.ModelForm, ModelFormTableMixin):
    site = df.ModelChoiceField(queryset = Client.objects.all(),
        widget=df.FilteringSelect(), empty_label='', required=False)
    type = df.ModelChoiceField(queryset = HostType.objects.all(),
        widget=df.FilteringSelect(), empty_label='', required=False)
    os = df.ModelChoiceField(queryset = OperatingSystem.objects.all(),
        widget=df.FilteringSelect(), empty_label='', required=False)
    hostname = df.CharField(required=False)
    
    class Meta:
        fields = ('site', 'type', 'hostname', 'os', 'automate', 'ip')
        model = Host
    
