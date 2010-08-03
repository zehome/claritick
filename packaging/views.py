# -*- coding: utf-8 -*-

from django.template import RequestContext
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, permission_required
from common.models import Client
from packaging.forms import SearchPackageForm
from packaging.models import Package

@permission_required("package.can_access")
def list(request, *args, **kwargs):
    data = request.POST

    # le form de filtres
    form = SearchPackageForm(data, user=request.user)

    packages = Package.objects.all()
    
    context = {
        "form": form,
        "packages": packages,
    }

    return render_to_response('packaging/list.html', context, context_instance=RequestContext(request))
