# -*- coding: utf-8 -*-

import  dojango.forms as df
from clariadmin.models import (Host, OperatingSystem, HostType, AdditionnalField,
                               ParamAdditionnalField, CHOICES_FIELDS_AVAILABLE,
                               Supplier)
from common.models import Client
from common.utils import sort_queryset
from common.forms import ModelFormTableMixin
from django.utils import simplejson as json
from itertools import repeat, chain

attrs_filtering={'queryExpr':'*${0}*','highlightMatch':'all','autoComplete':'False'}
def attrs_filtering_and(a):
    d=attrs_filtering.copy()
    d.update(a)
    return d

class HostForm(df.ModelForm):
    class Meta:
        model = Host
        widgets = {
            'os':df.FilteringSelect(attrs_filtering),
            'type':df.FilteringSelect(attrs=attrs_filtering_and({'onchange':'typeChanged(this);'})),
            'site':df.FilteringSelect(attrs=attrs_filtering),
            'supplier':df.FilteringSelect(attrs=attrs_filtering),
            'ip':df.IPAddressTextInput(),
        }
        fields=("site","hostname","ip","os","rootpw","supplier", "model", "type","location","serial","inventory","date_end_prod","status","commentaire")
    def __init__(self, user, *args, **kwargs):
        super(HostForm, self).__init__(*args, **kwargs)
        self.fields['site'].queryset=Client.objects.filter(id__in=(c.id for c in user.clients))


class ExtraFieldForm(df.Form):
    def _complete(self, host=None, blank=False):
        """ peuple fonction du contexte le formulaire. """
        # Rapide controle des arguments
        if isinstance(host,Host):
            host_type=host.type
            self.host=host
        else:
            host_type = host
            host=False
        if not host_type:
            return self
        # Récupère la liste des champs propre au type d'hote
        self.avail_fields=ParamAdditionnalField.objects.filter(host_type=host_type.id)[:]
        # Détermine la liste des champs et leurs valeurs courrante (défaut puis établi si existant)
        c_fields = dict(((v.id, v.default_values ) for v in (self.avail_fields)))
        if host:
            c_fields.update(dict((addf.field.id,addf.value)
                for addf in host.additionnalfield_set.all() if addf.field.id in c_fields.keys()))
        # Ajoute les champs dojango au formulaire
        if blank :
            args = lambda x,y:{'label':x.name,'initial':None,'required':False}
        else:
            args = lambda x,y:{'label':x.name,'initial':y[x.id],'required':False}
        self.fields.update(dict(
            (   'val_%s'%(field.id,),
                (df.CharField(**args(field,c_fields))
                    if field.data_type == '1' else
                 df.BooleanField(**args(field,c_fields))
                    if field.data_type == '2' else
                 df.IntegerField(**args(field,c_fields))
                    if field.data_type == '4' else
                 df.DateField(**args(field,c_fields))
                    if field.data_type == '5' else
                 df.ChoiceField(widget=df.FilteringSelect(attrs=attrs_filtering), choices=chain(((-1,''),),enumerate(field.default_values)), **args(field,c_fields))
                    if field.data_type == '3' else
                 df.MultipleChoiceField(choices=enumerate(field.default_values), **args(field,c_fields)))
            )for field in self.avail_fields))
        # renvoie son adresse
        return self

    def save(self):
        if not self.host.type:
            return False
        for f in self.avail_fields:
            cur=self.host.additionnalfield_set.filter(field=f.id)
            if not cur:
                cur = AdditionnalField(host=self.host,field=f)
            else:
                cur=cur[0]
            cur.value = self.cleaned_data['val_%s'%(f.id)]
            if cur.value == None:
                cur.value = "null"
            cur.save()

    def get_data(self):
        return dict((k, self.cleaned_data[k])
                for k, v in self.fields.iteritems()
                if not((isinstance(v,df.ChoiceField) and self.cleaned_data[k]=='-1')))

    @staticmethod
    def get_form(*args, **kwargs):
        h=kwargs.pop('host',False)
        b=kwargs.pop('blank',False)
        return ExtraFieldForm(*args,**kwargs)._complete(h,b)

class ExtraFieldAdminForm(df.ModelForm):
    text_val = df.CharField(label=u'Défaut', required=False)
    bool_val = df.BooleanField(label=u'Défaut', required=True)
    int_val  = df.IntegerField(label=u'Défaut', required=False)
    date_val = df.DateField(label=u'Défaut', required=False)
    choice01_val = df.CharField(label=u'Proposition', required=False)
    choice02_val = df.CharField(label=u'Proposition', required=False)
    choice03_val = df.CharField(label=u'Proposition', required=False)
    choice04_val = df.CharField(label=u'Proposition', required=False)
    choice05_val = df.CharField(label=u'Proposition', required=False)
    choice06_val = df.CharField(label=u'Proposition', required=False)
    choice07_val = df.CharField(label=u'Proposition', required=False)
    choice08_val = df.CharField(label=u'Proposition', required=False)
    choice09_val = df.CharField(label=u'Proposition', required=False)
    choice10_val = df.CharField(label=u'Proposition', required=False)
    choice11_val = df.CharField(label=u'Proposition', required=False)
    choice12_val = df.CharField(label=u'Proposition', required=False)
    choice13_val = df.CharField(label=u'Proposition', required=False)
    choice14_val = df.CharField(label=u'Proposition', required=False)
    choice15_val = df.CharField(label=u'Proposition', required=False)
    class Meta:
        model=ParamAdditionnalField
        widgets={
            'data_type':df.FilteringSelect(attrs=attrs_filtering_and({'onchange':'typeChanged(this);'}))
            }
    def __init__(self, *args, **kwargs):
        super(ExtraFieldAdminForm, self).__init__(*args, **kwargs)
        if kwargs.has_key('instance'):
            i= kwargs['instance']
            d=i.data_type
            ###
            ### To Be Continued
            ###
            self.initial['text_val']=i.default_values
            self.initial['bool_val']=i.default_values
    def save(self, commit=True):
        f = super(ExtraFieldAdminForm, self).save(commit=False)
        if commit:
            f.save()
        return f

# Depleted
class NewExtraFieldForm(df.Form):
    data_type = df.CharField(label=u'Type de donnée',
        widget=df.FilteringSelect(choices=CHOICES_FIELDS_AVAILABLE,
        attrs=attrs_filtering_and({u'onchange':u'showTypedField();'})))
    host_type = df.ModelChoiceField(label=u'Type de machine',
        queryset=HostType.objects.all(), empty_label=None)
    fast_search = df.BooleanField(label="Recherche rapide",required=False)
    name = df.CharField()
    text_val = df.CharField(label=u'Défaut:', required=False)
    bool_val = df.BooleanField(label=u'Défaut:', required=True)
    int_val = df.IntegerField(label=u'Défaut:', required=False)
    date_val = df.DateField(label=u'Défaut:', required=False)
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

    def __init__(self, *args, **kwargs):
        i=kwargs.pop('instance',False)
        if isinstance(i,ParamAdditionnalField):
            self.model=i
        super(NewExtraFieldForm, self).__init__(*args, **kwargs)


    def get_default_values(self):
        """ extrait du formulaire la valeur json des prop/defaults"""
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

    def save(self):
        cd = self.cleaned_data
        if self.model:
            self.model.name=cd["name"]
            self.model.host_type=cd["host_type"]
            self.model.data_type=cd["data_type"]
            self.model.fast_search=cd["fast_search"]
            self.model.default_values = self.get_default_values()
            return self.model.save()
        else:
            return ParamAdditionnalField(name=cd["name"], host_type=cd["host_type"],
                data_type=cd["data_type"], fast_search=cd["fast_search"],
                default_values=form.get_default_values()).save()

class SearchHostForm(df.Form, ModelFormTableMixin):
    global_search = df.CharField(label="Recherche globale",required=False)
    cheat_1 = df.CharField(max_length=1, label='', widget=df.TextInput(attrs={'class':'dijitHidden'}),required=False)
    cheat_2 = df.CharField(max_length=1, label='', widget=df.TextInput(attrs={'class':'dijitHidden'}),required=False)
    ip = df.CharField(required=False)
    hostname = df.CharField(required=False, label=u'Nom')
    site = df.ChoiceField(choices = (('',''),),
            widget=df.FilteringSelect(attrs=attrs_filtering),  required=False, label=u'Client')
    type = df.ModelChoiceField(queryset = HostType.objects.all(),
        widget=df.FilteringSelect(attrs=attrs_filtering_and({'onchange':'typeChanged(this);'})),
        empty_label='', required=False, label = u'Type')
    os = df.ModelChoiceField(queryset = OperatingSystem.objects.all(),
        widget=df.FilteringSelect(attrs=attrs_filtering), empty_label='', required=False, label=u'OS')
    supplier = df.ModelChoiceField(queryset = Supplier.objects.all(),
        widget=df.FilteringSelect(attrs=attrs_filtering), empty_label='', required=False, label=u'Fournisseur')
    status = df.CharField(required=False)
    inventory = df.CharField(required=False, label=u'Inventaire')
    commentaire = df.CharField(required=False)
    def __init__(self, user, *args, **kwargs):
        super(SearchHostForm, self).__init__(*args, **kwargs)
        self.fields['site'].choices=chain((('',''),),((c.id, str(c)) for c in sort_queryset(Client.objects.filter(id__in=(c.id for c in user.clients)))))

    class Meta:
        fields = ('ip', 'hostname', 'site', 'type', 'os', 'supplier', 'status', 'inventory', 'commentaire')
