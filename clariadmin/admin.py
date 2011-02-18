# -*- coding: utf-8 -*-

from django.contrib import admin
import dojango.forms as df
from clariadmin.models import OperatingSystem, HostType, Supplier, ParamAdditionnalField
from clariadmin.forms import ExtraFieldAdminForm
# Procédure en cour d'implémentation inspirée de:
# http://www.hindsightlabs.com/blog/2010/02/11/adding-extra-fields-to-a-model-form-in-djangos-admin/

class ExtraFieldAdmin(admin.ModelAdmin):
    form=ExtraFieldAdminForm
    class Media:
        js = ("js/clariadmin_extra_field_admin.js",)
        #css = (""),
    fieldsets = (
            (None,{
                'fields':('host_type','name','data_type','fast_search')}),
            ('Choix',{
                'classes': ('dijitHidden',),
                'fields':(
                    'choice01_val', 'choice02_val',
                    'choice03_val', 'choice04_val',
                    'choice05_val', 'choice06_val',
                    'choice07_val', 'choice08_val',
                    'choice09_val', 'choice10_val',
                    'choice11_val', 'choice12_val',
                    'choice13_val', 'choice14_val',
                    'choice15_val')}),
            ('Texte',{
                'classes': ('dijitHidden',),
                'fields':('text_val',)}),
            ('Numérique',{
                'classes': ('dijitHidden',),
                'fields':('int_val',)}),
            ('Date',{
                'classes': ('dijitHidden',),
                'fields':('date_val',)}),
            ('Booleen',{
                'classes': ('dijitHidden',),
                'fields':('bool_val',)}),
        )
    def save_model(self, request, obj, form, change):
        o = super(ExtraFieldAdmin, self).save_model(request, obj, form, change)
        data = request.POST
        obj.save()

admin.site.register(ParamAdditionnalField,ExtraFieldAdmin)
admin.site.register(OperatingSystem)
admin.site.register(HostType)
admin.site.register(Supplier)
