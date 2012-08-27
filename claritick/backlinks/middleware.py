# -*- coding: utf-8 -*-

from backlinks.constants import BACKLINKS_KEY


class BacklinksMiddleware(object):
    def process_request(self, request):
        assert(hasattr(request, 'session'),
            "The Backlinks middleware requires session middleware "
            "to be installed. Edit your MIDDLEWARE_CLASSES setting "
            "to insert 'django.contrib.sessions.middleware.SessionMiddleware'")
        request.backlinks = request.session.get(BACKLINKS_KEY, [])
        return None
