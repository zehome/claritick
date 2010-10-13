from django.contrib import admin
from django.http import HttpResponse
from claritick.developpements.models import Version, GroupeDev, Developpement, Client, Project

admin.site.register(Version)
admin.site.register(Project)
admin.site.register(Client)

class DeveloppementAdmin(admin.ModelAdmin):
    list_display = ("project", "groupe", "nom")
    search_fields = ("nom", "description", "groupe__nom")
    exclude = ("ticket",)
    save_on_top = True

    fieldsets = (
        ('General', {
            'classes': ('wide',),
            'fields': (('project', 'groupe', 'version_requise'), 
                        'nom', 'description', 'temps_prevu'),
        }),
        ('Supplementaire', {
            'fields': ('lien', 
                       ('poids', 'poids_manuel'), 
                       'engagement', 'client_demandeur',
                       ('done', 'bug'),
                       'couleur',
                      ), 
        }),
    )

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Filter for easy add"""
        data = request.GET.copy()
        if data:
            if db_field.name == "project" and data.get("project", None):
                kwargs["queryset"] = Project.objects.filter(id=data["project"])
            if db_field.name == "groupe" and data.get("project", None):
                kwargs["queryset"] = GroupeDev.objects.filter(project=data["project"])
            if db_field.name == "version_requise" and data.get("project", None):
                kwargs["queryset"] = Version.objects.filter(project=data["project"])
        return super(DeveloppementAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def response_add(self, request, obj):
        if request.POST.has_key("_popup"):
            return HttpResponse('<script type="text/javascript">opener.onClosePopup(window);</script>' )
        return super(DeveloppementAdmin, self).response_add(self, request, obj)
    def response_change(self, request, obj):
        if request.POST.has_key("_popup"):
            return HttpResponse('<script type="text/javascript">opener.onClosePopup(window);</script>' )
        return super(DeveloppementAdmin, self).response_change(self, request, obj)

class GroupeDevAdmin(admin.ModelAdmin):
    def response_add(self, request, obj):
        if request.POST.has_key("_popup"):
            return HttpResponse('<script type="text/javascript">opener.onClosePopup(window);</script>' )
        return super(GroupeDevAdmin, self).response_add(self, request, obj)
    def response_change(self, request, obj):
        if request.POST.has_key("_popup"):
            return HttpResponse('<script type="text/javascript">opener.onClosePopup(window);</script>' )
        return super(GroupeDevAdmin, self).response_change(self, request, obj)

admin.site.register(GroupeDev, GroupeDevAdmin)
admin.site.register(Developpement, DeveloppementAdmin)


