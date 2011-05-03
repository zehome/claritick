# -*- coding: utf-8 -*-
from django.contrib import admin
from django.http import HttpResponse
from clariadmin.models import OperatingSystem, HostType, Supplier, ParamAdditionnalField, HostStatus
from clariadmin.forms import ParamAdditionnalFieldAdminForm
from common.widgets import ColorPickerWidget
from common.models import ColorField
# Procédure en cour d'implémentation inspirée de:
# http://www.hindsightlabs.com/blog/2010/02/11/adding-extra-fields-to-a-model-form-in-djangos-admin/


class ExtraFieldAdmin(admin.ModelAdmin):
    form = ParamAdditionnalFieldAdminForm

    class Media:
        js = ("js/clariadmin_extra_field_admin.js",)
    fieldsets = (
        (None, {
            'fields': ('host_type', 'name', 'sorting_priority', 'api_key',
                      'data_type', 'fast_search', 'show')}),
        ('Choix (pas de recherche globale, supression de champs non supporté, favorisez un suffixe)', {
            'classes': ('dj_admin_Choix',),
            'fields': (
                'choice01_val', 'choice02_val',
                'choice03_val', 'choice04_val',
                'choice05_val', 'choice06_val',
                'choice07_val', 'choice08_val',
                'choice09_val', 'choice10_val',
                'choice11_val', 'choice12_val',
                'choice13_val', 'choice14_val',
                'choice15_val')}),
        ('Texte', {
            'classes': ('dj_admin_Text',),
            'fields': ('text_val',)}),
        ('Numérique', {
            'classes': ('dj_admin_Num',),
            'fields': ('int_val',)}),
        ('Date', {
            'classes': ('dj_admin_Date',),
            'fields': ('date_val',)}),
        ('Booleen (pas de recherche globale)', {
            'classes': ('dj_admin_Bool',),
            'fields': ('bool_val',)}),)

    def response_change(self, request, obj, *args, **kwargs):
        """
        Inspired from http://drl.posterous.com/django-admin-popup-to-change-add
        """
        if('_popup' in request.REQUEST):
            return HttpResponse("""<html><head></head><body>
                  <script type="text/javascript">
                  opener.dismissAddAnotherPopup(window);
                  </script></body></html>""")
        else:
            return super(ExtraFieldAdmin, self).response_change(request, obj, *args, **kwargs)


class ExtraFieldAdminInLine(admin.TabularInline):
    extra = 0
    model = ParamAdditionnalField
    readonly_fields = ('host_type', 'data_type', 'api_key', 'default_values')
    fields = ('name', 'sorting_priority', 'fast_search', 'host_type', 'api_key',
              'data_type', 'default_values')


class HostTypeAdmin(admin.ModelAdmin):
    class Media:
        css = {"all": ("admin_hosttype/admin_hosttype.css",)}
    formfield_overrides = {
        ColorField: {'widget': ColorPickerWidget},
    }
    inlines = [
        ExtraFieldAdminInLine,
    ]
    change_form_template = 'admin/clariadmin/hosttype/hosttype_change_form.html'

    def change_view(self, request, object_id, extra_context=None):
        return super(HostTypeAdmin, self).change_view(request, object_id, extra_context)


class OperatingSystemAdmin(admin.ModelAdmin):
    search_fields = ('name', 'version')
    list_display = ('name', 'version', 'depleted')
    list_editable = ['depleted']

admin.site.register(ParamAdditionnalField, ExtraFieldAdmin)
admin.site.register(OperatingSystem, OperatingSystemAdmin)
admin.site.register(HostType, HostTypeAdmin)
admin.site.register(HostStatus)
admin.site.register(Supplier)
