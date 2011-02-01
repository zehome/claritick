# -*- coding: utf-8 -*-

from dojango import forms as df
from clariadmin.models import Host, OperatingSystem, HostType, ParamAdditionnalField, CHOICES_FIELDS_AVAILABLE
from common.models import Client
from common.forms import ModelFormTableMixin
from django.utils import simplejson as json

class HostForm(df.ModelForm):
    class Meta:
        model = Host

class NewExtraFieldForm(df.Form):
    data_type = df.CharField(label=u'Type de donnée',
        widget=df.Select(choices=CHOICES_FIELDS_AVAILABLE,
        attrs={u'onchange':u'showTypedField();',}))
    host_type = df.ModelChoiceField(label=u'Type de machine',
        queryset=HostType.objects.all(), empty_label=None)
    fast_search = df.BooleanField(label="")
    name = df.CharField()
    text_val = df.CharField(required=False)
    bool_val = df.BooleanField(required=False)
    int_val = df.IntegerField(required=False)
    date_val = df.DateField(required=False)
    choice01_val = df.CharField(label=u'Proposition:', required=False)
    choice02_val = df.CharField(label=u'Proposition:', required=False)
    choice03_val = df.CharField(label=u'Proposition:', required=False)
    choice04_val = df.CharField(label=u'Proposition:', required=False)
    choice05_val = df.CharField(label=u'Proposition:', required=False)
    choice06_val = df.CharField(label=u'Proposition:', required=False)
    choice07_val = df.CharField(label=u'Proposition:', required=False)
    choice08_val = df.CharField(label=u'Proposition:', required=False)
    choice09_val = df.CharField(label=u'Proposition:', required=False)
    choice10_val = df.CharField(label=u'Proposition:', required=False)
    choice11_val = df.CharField(label=u'Proposition:', required=False)
    choice12_val = df.CharField(label=u'Proposition:', required=False)
    choice13_val = df.CharField(label=u'Proposition:', required=False)
    choice14_val = df.CharField(label=u'Proposition:', required=False)
    choice15_val = df.CharField(label=u'Proposition:', required=False)

    def get_default_values(self):
        dv=""
        cd=self.cleaned_data
        if cd['data_type']=='1':
            dv = cd['text_val']
        elif cd['data_type']=='2':
            dv = cd['bool_val']
        elif cd['data_type']=='3' or cd['data_type']=='6':
            choices=["choice01_val", "choice02_val", "choice03_val", "choice04_val", "choice05_val",
                "choice06_val", "choice07_val", "choice08_val", "choice09_val", "choice10_val", "choice11_val",
                "choice12_val", "choice13_val", "choice14_val", "choice15_val"]
            dv = [cd[e] for e in choices if cd[e]]
        elif cd['data_type']=='4':
            dv = cd['int_val']
        elif cd['data_type']=='5':
            dv = cd['date_val']
        return json.dumps(dv)

class SearchHostForm(df.Form, ModelFormTableMixin):
    site = df.ModelChoiceField(queryset = Client.objects.all(),
        widget=df.FilteringSelect(), empty_label='', required=False)
    type = df.ModelChoiceField(queryset = HostType.objects.all(),
        widget=df.FilteringSelect(), empty_label='', required=False)
    os = df.ModelChoiceField(queryset = OperatingSystem.objects.all(),
        widget=df.FilteringSelect(), empty_label='', required=False)
    hostname = df.CharField(required=False)

    class Meta:
        fields = ('site', 'type', 'hostname', 'os', 'ip')
