import sys
import traceback
from django.views.debug import technical_500_response
from django.http import HttpResponse


class UserBasedExceptionMiddleware(object):
    def process_exception(self, request, exception):
        if getattr(request, "is_text_exception", False):
            exc_info = traceback.format_exc()
            r = HttpResponse("Exception: %s\n================\n%s" % (
                    unicode(exception), exc_info),
                status=500)
            return r

        user = request.user
        if user.is_staff:
            return technical_500_response(request, *sys.exc_info())

        return None
