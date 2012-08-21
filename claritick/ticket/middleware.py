# -*- coding: utf-8 -*-

from common.models import Client, ClaritickUser, UserProfile
from common.exceptions import NoProfileException

class PopulateUserMiddleware(object):
    def process_request(self, request):
        if hasattr(request, 'user') and not request.user.is_anonymous():
            try:
                profile = request.user.my_userprofile
                if request.user.is_superuser:
                    request.user.clients = Client.objects.all()
                    request.user.childs = ClaritickUser.objects.all()
                else:
                    request.user.clients = profile.get_clients()
                    request.user.childs = ClaritickUser.objects.get(pk=request.user.pk).get_child_users()
                request.user.security_level = profile.get_security_level()
            except UserProfile.DoesNotExist:
                raise NoProfileException(request.user)
        return None
