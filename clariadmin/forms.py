# -*- coding: utf-8 -*-

from dojango import forms as df
from clariadmin.models import (Host, OperatingSystem, HostType, AdditionnalField,
                               ParamAdditionnalField, CHOICES_FIELDS_AVAILABLE)
from common.models import Client
from common.forms import ModelFormTableMixin
from django.utils import simplejson as json

class HostForm(df.ModelForm):
    class Meta:
        model = Host

class ExtraFieldForm(df.Form):
    def _complete(self, field, index):
        if isinstance(field, AdditionnalField):
            content = field.value
            field = field.field
        else:
            content = field.default_values
        print "datatype:\t%s\ncontent:\t%s\n"%(field.data_type ,content)
        self.val = (df.CharField(label=field.name,initial=content,required=False) if field.data_type == '1'
            else df.BooleanField(label=field.name,initial=content,required=False) if field.data_type == '2'
            else df.IntegerField(label=field.name,initial=content,required=False) if field.data_type == '4'
            else df.DateField(label=field.name,initial=content,required=False) if field.data_type == '5'
            else df.ChoiceField(label=field.name,choices=enumerate(field.default_values)) if field.data_type == '3'
            else df.MultipleChoiceField(label=field.name,choices=enumerate(field.default_values)))
        self.fields['val%s'%(index,)]=self.val
        return self

    @staticmethod
    def get_forms(host_type=None, host=None):
        if host:
            host_type = host.host_type
            return [ ExtraFieldForm()._complete(f,i)
                   for i,f in enumerate(
                   host.additionnal_field_set)]
        else:
            return [ ExtraFieldForm()._complete(f,i)
                   for i,f in enumerate(
                   ParamAdditionnalField.objects.filter(host_type=host_type.id))]

    @staticmethod
    def set_forms(forms, host):
        pass


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
