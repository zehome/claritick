# -*- coding: utf-8 -*-

import dojango.forms as df
from clariadmin.models import Host, OperatingSystem, HostType
from clariadmin.models import AdditionnalField, ParamAdditionnalField, Supplier
from clariadmin.models import CHOICES_FIELDS_AVAILABLE
from common.models import Client
from common.utils import sort_queryset
from common.forms import ModelFormTableMixin
from django.utils import simplejson as json
from django.utils.datastructures import SortedDict
from django.conf import settings
from itertools import chain
import datetime

attrs_filtering={'queryExpr':'*${0}*','highlightMatch':'all','autoComplete':'False'}
def attrs_filtering_and(a):
    d=attrs_filtering.copy()
    d.update(a)
    return d

class FormSecurityChecker(object):
    """
    This mixin permits to check security aspects regarding to a form.

    Will remove items user when user has a security level higher
    than the configured security level.
    """

    # This flags is set to False if a required field
    # is removed by the mixin.
    _security_can_save = True
    # This flag is True if at least 1 field is visible.
    _security_can_view = False
    # Store deleted fields if needed by the programmer.
    _security_deleted_fields = []
    # Loaded in the init from django.conf.settings.
    _security_settings = {}
    # Default security level of fields.
    _security_default_level = 99
    # Cache the user_profile security_level in the instance of the form.
    _security_userlevel = None

    def _security_filter(self, user, formName, security = {}):
        """
        Will delete fields from the form if user has no access to them.
        deleted fields are placed in _security_deleted_fields.

        If required fields are removed, the _security_can_save flag is
        switched to False.
        """
        self._security_userlevel = user.get_profile().get_security_level()
        if not security:
            self._security_settings = settings.SECURITY.get(formName, {})
        else:
            self._security_settings = security
        self._security_default_level = self._security_settings.get("__default__", settings.SECURITY["DEFAULT_LEVEL"])
        for fname in self.fields.keys():
            required_level = self._security_settings.get(fname, self._security_default_level)
            # LC: TODO: Debug: remove this
            print "User level %d required %s for %s" % (self._security_userlevel, required_level, fname)
            if required_level < self._security_userlevel:
                field = self.fields[fname]
                if field.required:
                    self._security_can_save = False
                self._security_deleted_fields.append(field)
                del(self.fields[fname])
        self._security_can_view = bool(self.fields)

    @classmethod
    def filter_querydict(cls, user, querydict):
        """
        This method will filter querydict, not letting user pass invalid data to the view.
        """
        userlevel = user.get_profile().get_security_level()
        security_settings = settings.SECURITY.get(cls.__name__, {})
        security_default_level = security_settings.get("__default__", settings.SECURITY["DEFAULT_LEVEL"])
        filtred_querydict = querydict.copy()
        #filtred_querydict._mutable=True
        for key in filtred_querydict.keys():
            required_level = security_settings.get(key, security_default_level)
            if required_level < userlevel:
                # LC: TODO: Debug: remove this
                print "Deleted querydict key %s" % (key,)
                del(filtred_querydict[key])
        return filtred_querydict

    @classmethod
    def filter_list(cls, user, fields):
        """
        user -- request.user: reference security level for this filtering.
        fileds -- list or iterable of keys to filter.
        returns the `list` with only authorized filed names.
        """
        userlevel = user.get_profile().get_security_level()
        security_settings = settings.SECURITY.get(cls.__name__, {})
        security_default_level = security_settings.get("__default__", settings.SECURITY["DEFAULT_LEVEL"])
        return [e for e in fields
            if userlevel < security_settings.get(e, security_default_level)]


    # Proxy accessor
    def security_can_view(self):
        return self._security_can_view

    # Proxy accessor
    def security_can_save(self):
        return self._security_can_view and self._security_can_save

    def has_deleted_fields(self):
        return bool(self._security_deleted_fields)

class HostForm(df.ModelForm, FormSecurityChecker):
    date_start_prod=df.DateField(initial=datetime.date.today)
    class Meta:
        model = Host
        widgets = {
            'os':df.FilteringSelect(attrs_filtering),
            'type':df.FilteringSelect(attrs_filtering_and({'onchange':'typeChanged(this);'})),
            'site':df.FilteringSelect(attrs_filtering),
            'supplier':df.FilteringSelect(attrs_filtering),
            'ip':df.IPAddressTextInput(),
            'commentaire':df.Textarea({"class":'comment_field'})
        }
        fields = ("site","hostname","ip","os","rootpw","supplier", "model",
            "type","location","serial","inventory", "date_start_prod","date_end_prod",
            "status","commentaire")
    def __init__(self, user, *args, **kwargs):
        super(HostForm, self).__init__(*args, **kwargs)
        self.fields['site'].queryset = Client.objects.filter(id__in=(c.id for c in user.clients))

        self._security_filter(user = user, formName = 'Host')

    def save(self, force_insert=False, force_update=False, commit=True):
        assert(self.security_can_save())
        return super(HostForm, self).save(commit)

    def is_valid(self):
        if not self.security_can_save():
            print "return False!"
            return False
        return super(HostForm, self).is_valid()

class AdditionnalFieldForm(df.Form):
    def _complete(self, host=None, host_type=None, blank=False):
        """Adapt and fill the form. Called by `AdditionnalFieldForm.get_form`"""
        # Rapide controle des arguments
        if host:
            host_type=host.type
            self.host=host
        if not host_type:
            return self
        # Récupère la liste des champs propre au type d'hote
        self.avail_fields=ParamAdditionnalField.objects.filter(host_type=host_type.id)[:]
        # Détermine la liste des champs et leurs valeurs courrante (défaut puis établi si existant)
        c_fields = dict((v.id, v.default_values ) for v in (self.avail_fields))
        if host:
            c_fields.update(dict((addf.field.id,addf.value)
                for addf in host.additionnalfield_set.all() if addf.field.id in c_fields.keys()))
        # Ajoute les champs dojango au formulaire
        if blank :
            args = lambda x,y:{'label':x.name,'initial':None,'required':False}
        else:
            args = lambda x,y:{'label':x.name,'initial':y[x.id],'required':False}
        self.fields.update(SortedDict(
            (   'val_%s'%(field.id,),
                (df.CharField(**args(field,c_fields))
                    if field.data_type == '1' else
                 df.BooleanField(**args(field,c_fields))
                    if field.data_type == '2' else
                 df.IntegerField(**args(field,c_fields))
                    if field.data_type == '4' else
                 df.DateField(**args(field,c_fields))
                    if field.data_type == '5' else
                 df.ChoiceField(widget=df.FilteringSelect(attrs=attrs_filtering),
                    choices=[(-1,'')]+list(enumerate(field.default_values)), **args(field,c_fields))
                    if field.data_type == '3' else
                 df.MultipleChoiceField(choices=enumerate(field.default_values), **args(field,c_fields)))
            )for field in self.avail_fields))
        # renvoie son adresse
        return self

    def save(self, force_insert=False, force_update=False, commit=True):
        """To use used like the ModelFrom save method"""
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
            cur.save(commit)

    def get_data(self):
        """returns a `self.cleaned_data` copy without empty ChoiceFields"""
        return dict((k, self.cleaned_data[k])
                for k, v in self.fields.iteritems()
                if not((isinstance(v,df.ChoiceField) and self.cleaned_data[k]=='-1')))

    @staticmethod
    def get_form(*args, **kwargs):
        """
        Used to wrap `Form.__init__` method and returns a new instance.
        It uses normal `Form.__init__` args and these named args:
            host: host's host type as host_type and form with host's values.
            host_type: host_type specific fields and default values.
            blank: provide a form with no values
        """
        h=kwargs.pop('host',False)
        ht=kwargs.pop('host_type',False)
        b=kwargs.pop('blank',False)
        return AdditionnalFieldForm(*args,**kwargs)._complete(h,ht,b)

class ParamAdditionnalFieldAdminForm(df.ModelForm):
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
        super(ParamAdditionnalFieldAdminForm, self).__init__(*args, **kwargs)
        if kwargs.has_key('instance'):
            inst= kwargs['instance']
            if inst.data_type in ('1','2','4','5'):
                for key in ('text_val','bool_val','date_val','int_val'):
                    self.initial[key] = inst.default_values
            else:
                for i,e in ((i,"choice%s_val"%(str(i+1).rjust(2,'0'))) for i in range(16)):
                    try:
                        if inst.default_values[i]:
                            self.initial[e]=inst.default_values[i]
                    except IndexError:
                        pass
    def save(self, commit=True):
        inst = super(ParamAdditionnalFieldAdminForm, self).save(commit=False)
        cd=self.cleaned_data
        normal_fields={'1':'text_val', '2':'bool_val', '4':'int_val', '5':'date_val'}
        if normal_fields.get(cd['data_type'],False):
            dv = cd[normal_fields[cd['data_type']]]
        else:
            dv = [cd[e] for e in
                    ("choice%s_val"%(str(i).rjust(2,'0')) for i in range(1,16))
                    if cd[e]]
        inst.default_values = json.dumps(dv)
        if commit:
            inst.save()
        return inst

class SearchHostForm(df.Form, ModelFormTableMixin, FormSecurityChecker):
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
        ordered_clients = sort_queryset(Client.objects.filter(id__in=(c.id for c in user.clients)))
        self.fields['site'].choices=[('','')]+[(c.id, unicode(c)) for c in ordered_clients]
        self._security_filter(user = user, formName = 'SearchHost')

    def update(self, hosts):
        """Restrict `ModelChoiceFields` to values existing in hosts queryset"""
        if self.fields.has_key('os'):
            self.fields['os'].queryset = OperatingSystem.objects.filter(host__in=hosts).distinct()
        if self.fields.has_key('supplier'):
            self.fields['supplier'].queryset = Supplier.objects.filter(host__in=hosts).distinct()
        if self.fields.has_key('type'):
            self.fields['type'].queryset = HostType.objects.filter(host__in=hosts).distinct()
        if self.fields.has_key('site'):
            self.fields['site'].choices = chain((('',''),),((c.id, str(c))
                for c in sort_queryset(Client.objects.filter(host__in=hosts).distinct())))

    class Meta:
        fields = ('ip', 'hostname', 'site', 'type', 'os', 'supplier', 'status', 'inventory', 'commentaire')
