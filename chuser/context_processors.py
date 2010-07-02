# -*- coding: utf8 -*-

from forms import ChuserForm

def chuser(request):
    if request.user.is_superuser or request.session.get('was_superuser', False):
        return {"chuserform": ChuserForm(initial={'user': request.user.pk}),}
    return {}
