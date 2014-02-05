# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext

from loggingauth.signals import auth_username_failed, auth_password_failed

ACTION_CHOICES = (
    ("LOGIN", _(u"Login")),
    ("LOGOUT", _(u"Logout")),
)

REASON_CHOICES = (
    ("BADPASS", _(u"Bad password")),
    ("BADUSER", _(u"Invalid username")),
)


def get_request_remote_addr(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR", None)
    if x_forwarded_for:
        ip = x_forwarded_for
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip


class UserLoginTrace(models.Model):
    class Meta:
        verbose_name = u"User login trace"
        permissions = (
            ("can_see_userlogintraces", ugettext(u"Can view user login/logout traces")),
        )

    user = models.ForeignKey(User, null=True, blank=True)
    username = models.CharField(_(u"Username"),
                                max_length=1024,
                                blank=False, null=False)
    date = models.DateTimeField(_(u"Date"),
                                auto_now_add=True)
    granted = models.BooleanField(_(u"Granted"), blank=False, null=False)
    action = models.CharField(_(u"Action"),
                              blank=False,
                              null=False, max_length=32,
                              choices=ACTION_CHOICES)
    reason = models.CharField(_(u"Reason"),
                              blank=True, null=True,
                              max_length=32,
                              choices=REASON_CHOICES)
    ip = models.IPAddressField(blank=True, null=True)

    @staticmethod
    def auth_username_failed(username, **kwargs):
        ulog = UserLoginTrace(username=username,
            granted=False,
            action="LOGIN",
            reason="BADUSER")
        ulog.save()

    @staticmethod
    def auth_password_failed(user, **kwargs):
        ulog = UserLoginTrace(username=user.username,
            user=user,
            granted=False,
            action="LOGIN",
            reason="BADPASS")
        ulog.save()

    @staticmethod
    def user_logged_in(request, user, **kwargs):
        ulog = UserLoginTrace(username=user.username,
            user=user,
            granted=True,
            action="LOGIN",
            ip=get_request_remote_addr(request))
        ulog.save()

    @staticmethod
    def user_logged_out(request, user, **kwargs):
        ulog = UserLoginTrace(username=user.username,
            user=user,
            granted=True,
            action="LOGOUT",
            ip=get_request_remote_addr(request))
        ulog.save()


# Register signals
SIGNAL_ID = "loggingauthbackend"

auth_username_failed.connect(UserLoginTrace.auth_username_failed,
                             dispatch_uid=SIGNAL_ID)
auth_password_failed.connect(UserLoginTrace.auth_password_failed,
                             dispatch_uid=SIGNAL_ID)
user_logged_in.connect(UserLoginTrace.user_logged_in,
                       dispatch_uid=SIGNAL_ID)
user_logged_out.connect(UserLoginTrace.user_logged_out,
                        dispatch_uid=SIGNAL_ID)
