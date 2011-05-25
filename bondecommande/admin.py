# -*- coding: utf-8 -*-

from django.contrib import admin
from django.db import models
from django import forms
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe

from dojango import forms as df

from common.models import Client, OneLineTextField
from common.utils import sort_queryset
from common.widgets import FilteringSelect

from bondecommande.models import BonDeCommande, BonDeCommandeFile

class BonDeCommandeFileForm(forms.ModelForm):
    class Meta:
        model = BonDeCommandeFile

    file = forms.FileField(label='Fichier joint', required=False)

    def save(self, commit=False):
        file = self.cleaned_data["file"]
        if file:
            instance = super(BonDeCommandeFileForm, self).save(commit=False)
            instance.content_type = file.content_type
            if file.multiple_chunks():
                dataList = []
                for chunk in file.chunks():
                    dataList.append(chunk)
                data = "".join(dataList)
            else:
                data = file.read()
            instance.data = data
            instance.filename = file.name
            #LC: Never call this as it's inline
            #instance.save()
        else:
            instance = super(BonDeCommandeFileForm, self).save(commit=commit)
        return instance
    
class BonDeCommandeFileInline(admin.TabularInline):
    model = BonDeCommandeFile
    form = BonDeCommandeFileForm
    exclude = [ "data", "content_type", "filename" ]
    
    formfield_overrides = {
        OneLineTextField: {'widget': admin.widgets.AdminTextInputWidget},
    }

class BonDeCommandeAdminForm(forms.ModelForm):
    class Meta:
        model = BonDeCommande
    
    def clean_client(self):
        return Client.objects.get(pk=self.cleaned_data["client"])    

class BonDeCommandeAdmin(admin.ModelAdmin):
    form = BonDeCommandeAdminForm
    def get_form(self, request, obj=None, **kwargs):
        """ Override get_form to add "client" to project """
        form = super(BonDeCommandeAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields["client"] = df.ChoiceField(choices = [(x.pk, x) for x in sort_queryset(request.user.clients)],
            widget=FilteringSelect(), required=True)
        return form

    inlines = [BonDeCommandeFileInline, ]
    readonly_fields = ( "date_creation", "ticket" )
    search_fields = ( "client__label", "comment", "id" )
    list_display = ("__unicode__", "date_creation", "client", "comment", "is_closed")
    date_hierarchy = "date_creation"
    
admin.site.register(BonDeCommande, BonDeCommandeAdmin)
