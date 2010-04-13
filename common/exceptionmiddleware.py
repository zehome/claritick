import sys
from django.views.debug import technical_500_response

class UserBasedExceptionMiddleware(object):
    def process_exception(self, request, exception):
        user = request.user
        if user.is_staff:
            return technical_500_response(request, *sys.exc_info())
        return None
