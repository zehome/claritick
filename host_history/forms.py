# -*- coding: utf-8 -*-
import dojango.forms as df
from host_history.models import ACTIONS_LOG
from clariadmin.forms import attrs_filtering
from common.models import Client
from common.utils import sort_queryset
from common.forms import ModelFormTableMixin
from django.db.models import Q

class SearchLogForm(df.Form, ModelFormTableMixin):
    hostname = df.CharField(required=False, label=u'Nom de la machine')
    username = df.CharField(required=False, label=u"Nom d'utilisateur")
    site = df.ChoiceField(choices = (('',''),),
            widget=df.FilteringSelect(attrs=attrs_filtering),  required=False, label=u'Client')
    # these ModelChoiceFields are initialised twice. once forvalidation and once after filtering
    action = df.MultipleChoiceField(choices = ((i,s) for i,s,c in ACTIONS_LOG),
        required=False,
        label = u'Sauf les actions')
    message = df.CharField(required=False)
    ip = df.CharField(required=False)

    def __init__(self, user, *args, **kwargs):
        super(SearchLogForm, self).__init__(*args, **kwargs)
        ordered_clients = sort_queryset(Client.objects.filter(id__in=(c.id for c in user.clients)))
        self.fields['site'].choices=[('','')]+[(c.id, unicode(c)) for c in ordered_clients]
    def search(self, qs):
        cd = self.cleaned_data
        if cd['site']:
            qs = qs.filter( Q(host__site__id__exact = cd['site'])
                           |Q(host__site__parent__id__exact = cd['site'])
                           |Q(host__site__parent__parent__id__exact = cd['site']))
        if cd['hostname']:
            qs = qs.filter(host__hostname__icontains = cd['hostname'])
        if cd['username']:
            qs = qs.filter(username__icontains = cd['username'])
        if cd['action']:
            qs = qs.exclude(action__in = cd['action'])
        if cd['ip']:
            qs = qs.filter(ip__contains = cd['ip'])
        if cd['message']:
            qs = qs.filter(message__contains = cd['message'])
        return qs

# vim:set et sts=4 ts=4 tw=80:
