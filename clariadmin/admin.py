# -*- coding: utf-8 -*-

from django.contrib import admin
from clariadmin.models import OperatingSystem, HostType, Supplier, ParamAdditionnalField
from clariadmin.forms import ParamAdditionnalFieldAdminForm
# Procédure en cour d'implémentation inspirée de:
# http://www.hindsightlabs.com/blog/2010/02/11/adding-extra-fields-to-a-model-form-in-djangos-admin/

class ExtraFieldAdmin(admin.ModelAdmin):
    form=ParamAdditionnalFieldAdminForm
    class Media:
        js = ("js/clariadmin_extra_field_admin.js",)
    fieldsets = (
        (None,{
            'fields':('host_type','name','data_type','fast_search')}),
        ('Choix',{
            'classes': ('dj_admin_Choix',),
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
            'classes': ('dj_admin_Text',),
            'fields':('text_val',)}),
        ('Numérique',{
            'classes': ('dj_admin_Num',),
            'fields':('int_val',)}),
        ('Date',{
            'classes': ('dj_admin_Date',),
            'fields':('date_val',)}),
        ('Booleen',{
            'classes': ('dj_admin_Bool',),
            'fields':('bool_val',)}),)

class HostTypeAdmin(admin.ModelAdmin):
    fields=("gateway","text")

admin.site.register(ParamAdditionnalField,ExtraFieldAdmin)
admin.site.register(OperatingSystem)
admin.site.register(HostType, HostTypeAdmin)
admin.site.register(Supplier)
