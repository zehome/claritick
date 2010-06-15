from django.contrib import admin
from claritick.developpements.models import Version, GroupeDev, Developpement, Client

admin.site.register(Version)
admin.site.register(GroupeDev)
admin.site.register(Developpement)
admin.site.register(Client)
