from django.contrib import admin
from claritick.developpements.models import Version, GroupeDev, Developpement, Client

admin.site.register(Version)
admin.site.register(GroupeDev)
admin.site.register(Client)

class DeveloppementAdmin(admin.ModelAdmin):
    list_display = ("nom", "groupe")
    search_fields = ("nom", "description", "groupe__nom")

admin.site.register(Developpement, DeveloppementAdmin)


