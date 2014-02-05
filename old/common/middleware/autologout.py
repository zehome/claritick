# -*- coding: utf-8 -*-

from django.conf import settings
from django.utils.http import urlquote
from django.http import HttpResponseRedirect
from django.contrib import auth
from datetime import datetime, timedelta


class AutoLogout(object):
    login_url = settings.LOGIN_URL
    redirect_field_name = auth.REDIRECT_FIELD_NAME

    def process_request(self, request):
        if not request.user.is_authenticated():
            return
        # Permission no autologout => Pas de logout automatique
        if request.user.has_perm("auth.no_autologout"):
            request.autologout_enabled = False
        else:
            request.autologout_enabled = True

            try:
                last_touch = request.session['last_touch']
            except KeyError:
                pass
            else:
                request.session['last_touch'] = datetime.now()
                if datetime.now() - last_touch > timedelta( 0, getattr(settings, 'AUTO_LOGOUT_DELAY', 10) * 60, 0):
                    try:
                        del request.session['last_touch']
                    except KeyError:
                        pass
                    auth.logout(request)

                    path = urlquote(request.get_full_path())
                    tup = self.login_url, self.redirect_field_name, path
                    return HttpResponseRedirect('%s?%s=%s' % tup)
