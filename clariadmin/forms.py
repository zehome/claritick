# -*- coding: utf-8 -*-

from dojango import forms as df
from clariadmin.models import (Host, OperatingSystem, HostType, AdditionnalField,
                               ParamAdditionnalField, CHOICES_FIELDS_AVAILABLE)
from common.models import Client
from common.forms import ModelFormTableMixin
from django.utils import simplejson as json
from itertools import repeat

class HostForm(df.ModelForm):
    class Meta:
        model = Host

class ExtraFieldForm(df.Form):
    def _complete(self, host=None):
        if isinstance(host,Host):
            host_type=host.type
            self.host=host
        else:
            host_type = host
            host=False
        self.avail_fields=ParamAdditionnalField.objects.filter(host_type=host_type.id)[:]
        c_fields = dict(((v.id, v.default_values ) for v in (self.avail_fields)))
        for addf in host.additionnalfield_set.all():
            c_fields[addf.field.id]=addf.value
        for field in self.avail_fields:
             self.fields['val_%s'%(field.id,)] = (
                df.CharField(label=field.name, initial=c_fields[field.id], required=False)
                    if field.data_type == '1' else
                df.BooleanField(label=field.name, initial=c_fields[field.id], required=False)
                    if field.data_type == '2' else
                df.IntegerField(label=field.name, initial=c_fields[field.id], required=False)
                    if field.data_type == '4' else
                df.DateField(label=field.name, initial=c_fields[field.id], required=False)
                    if field.data_type == '5' else
                df.ChoiceField(label=field.name, choices=enumerate(field.default_values))
                    if field.data_type == '3' else
                df.MultipleChoiceField(label=field.name, choices=enumerate(field.default_values)))
        return self
    def save(self):
        for f in self.avail_fields:
            cur=self.host.additionnalfield_set.filter(field=f.id)
            if not cur:
                cur = AdditionnalField(host=self.host,field=f)
            cur.value = self.cleaned_data['val_%s'%(f.id)]
            cur.save()
        #self.host.save()

    @staticmethod
    def get_form(*args, **kwargs):
        h=kwargs.pop('host')
        return ExtraFieldForm(*args,**kwargs)._complete(h)



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
            dv = [cd[e] for e in
                    ("choice%s_val"%(str(i).rjust(2,'0')) for i in range(1,16))
                    if cd[e]]
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
