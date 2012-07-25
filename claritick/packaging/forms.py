# -*- coding: utf-8 -*-

from dojango import forms as df
from django.conf import settings

from common.forms import ModelFormTableMixin
from common.utils import filter_form_for_user, sort_queryset
from common.widgets import FilteringSelect
from packaging.models import PackageKind
from common.models import Client


class SearchPackageForm(df.Form, ModelFormTableMixin):
    client      = df.ChoiceField(choices=[(x.pk, x) for x in sort_queryset(Client.objects.all())],
                                 widget=FilteringSelect(),
                                 required=False)
    
    kind        = df.ModelChoiceField(queryset = PackageKind.objects.all(), 
                                      widget=FilteringSelect(), 
                                      empty_label='', 
                                      required=False)

    def __init__(self, *args, **kwargs):
        filter_form_for_user(self, kwargs.pop("user", None))
        super(SearchPackageForm, self).__init__(*args, **kwargs)