# -*- coding: utf-8 -*-

from common.models import Client, ClaritickUser, UserProfile

class PopulateUserMiddleware(object):
    def process_request(self, request):
        if hasattr(request, 'user') and not request.user.is_anonymous():
            if request.user.is_superuser:
                request.user.clients = Client.objects.all()
                request.user.childs = ClaritickUser.objects.all()
            else:
                try:
                    request.user.clients = request.user.get_profile().get_clients()
                    request.user.childs = ClaritickUser.objects.get(pk=request.user.pk).get_child_users()
                except UserProfile.DoesNotExist:
                    raise NoProfileException(request.user)
        return None
