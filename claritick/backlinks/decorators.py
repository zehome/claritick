# -*- coding: utf-8 -*-

try:
    from functools import wraps
except ImportError:
    from django.utils.functional import wraps  # Python 2.3, 2.4 fallback.

from django.conf import settings
from backlinks.constants import BACKLINKS_KEY
from django.views.generic.simple import redirect_to


class InMemoryBacklink(object):
    _global_index = 0

    def __unicode__(self):
        return "<Backlink %s [%s] QUERY_STRING: %s>" % (
                self.index, self.path, self.QUERY_STRING)

    def __repr__(self):
        return unicode(self)

    @staticmethod
    def get_serial_inc():
        """ Should be thread protected. """
        InMemoryBacklink._global_index += 1

    def __init__(self, request, view, view_args, view_kw):
        self.QUERY_STRING = request.META.get("QUERY_STRING", "")
        self.path = request.path or ''
        self.index = self.get_serial_inc()

    def redirect(self, request, **args):
        """ Redirect to the last view """
        if self.QUERY_STRING:
            url = "%s?%s" % (self.path, self.QUERY_STRING)
        else:
            url = self.path

        return redirect_to(request, url, **args)


def backlink_setter(view_func):
    """
    This decorator will save requests in order to replay them when asked
    It should be placed on a view, say, like a list of items.
    So when you click the item, it will load a view which will
    not be a backlink_setter.
    Then, the middleware for each request will place a
    "backlink" in the request, so you can use it for redirects.
    This information will be available until removed from session,
    or overwritten by another call.
    """

    try:
        backlink_limit = settings.BACKLINK_LIMIT
    except AttributeError:
        backlink_limit = 10  # Maximum backlink "in memory" default to 10

    def _wrapped_view(request, *view_args, **view_kw):
        if not request.is_ajax():
            session = request.session
            backlinks = session.get(BACKLINKS_KEY, [])[-backlink_limit:]
            backlinks.append(InMemoryBacklink(request, view_func,
                             view_args, view_kw))
            session[BACKLINKS_KEY] = backlinks
        return view_func(request, *view_args, **view_kw)
    return wraps(view_func)(_wrapped_view)
