# -*- coding: utf-8 -*-

from claritick.models import AccessLog


def get_client_ip(request):
    return request.META.get("REMOTE_ADDR", "")


def login_success(request):
    user = request.user
    if user and not user.is_anonymous():
        AccessLog.objects.create(user=user,
                                 message="AUTH_OK",
                                 ip=get_client_ip(request))


def login_error(request, username):
    AccessLog.objects.create(user=None,
                             username=username,
                             message="AUTH_BAD",
                             ip=get_client_ip(request))
