# -*- coding: utf-8 -*-

from django.contrib import admin
from django.core.urlresolvers import reverse
from loggingauth.models import UserLoginTrace

class UserLoginTraceAdmin(admin.ModelAdmin):
    actions = None
    
    date_hierarchy = "date"
    list_display = ("action", "granted", "get_user_link", "username", "date", "reason", "ip")
    readonly_fields = list_display
    search_fields = ["user__login", "user__email", "username", "user__first_name", "user__last_name", "ip"]
    
    def get_user_link(self, log):
        user = log.user
        if user:
            url = reverse('admin:%s_%s_change' % ("common", "claritickuser"), args=[user.id] )
            return u'<a href="%s">%s</a>' % (url, user.get_full_name())
    get_user_link.allow_tags = True
    get_user_link.admin_order_field = 'user'
    get_user_link.short_description = "User"
    
    def save_model(self, *args, **kwargs):
        return
    
    def delete_model(self, *args, **kwargs):
        return

admin.site.register(UserLoginTrace, UserLoginTraceAdmin)
