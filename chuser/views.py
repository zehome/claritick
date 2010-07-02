# -*- coding: utf8 -*-

from django.http import HttpResponseRedirect
from django.core.exceptions import PermissionDenied
from django.views.decorators.http import require_POST
from django.contrib.auth import SESSION_KEY
from django.contrib.auth.decorators import login_required
from forms import ChuserForm

@require_POST
@login_required
def change_user(request):

    if not (request.user.is_superuser or request.session.get('was_superuser', False)):
        raise PermissionDenied

    form = ChuserForm(request.POST)

    if form.is_valid():
        user = form.cleaned_data['user']
        request.session[SESSION_KEY] = user.id
        request.user = user
        request.session['was_superuser'] = True

    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
