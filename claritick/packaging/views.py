# -*- coding: utf-8 -*-

from django import http
from django.template import RequestContext
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.views.decorators.csrf import csrf_exempt
from common.models import Client
from common.decorator import render_to_json
from packaging.forms import SearchPackageForm
from packaging.models import Package, ClientPackageAuth
from django.db.models import Q
import os.path

@permission_required("package.can_access")
def list(request, *args, **kwargs):
    data = request.POST

    # le form de filtres
    form = SearchPackageForm(data, user=request.user)

    qs = Package.objects.all()
    qs = qs.order_by("template__client")
    qs = qs.order_by("template__kind__name")
    qs = qs.order_by("template__name")

    context = {
        "form": form,
        "packages": qs,
    }

    return render_to_response('packaging/list.html', context, context_instance=RequestContext(request))

@csrf_exempt
def listxml(request, *args, **kwargs):
    data = request.POST
    try:
        authkey = data["authkey"]
    except KeyError:
        print "authkey not found"
        return http.HttpResponse('No permission without valid key.', 403)
    
    # First determine packageAuth client
    try:
        packageauth = ClientPackageAuth.objects.get(key=authkey)
    except ClientPackageAuth.DoesNotExist:
        print "packagehost not found with key [%s]" % (authkey,)
        return http.HttpResponse('No permission without valid key.', 403)
    
    qs = Package.objects.all()
    qs.filter(client=packageauth.client.id)
    
    qs = qs.order_by("template__kind__name")
    qs = qs.order_by("template__name")
    
    packages = [ p for p in qs if p.file ]
    context = {
        "packages": packages,
        "client": packageauth.client,
        "ABSOLUTE_PATH": "%s://%s" % (request.is_secure() and "https" or "http", request.get_host(),),
    }
    return render_to_response('packaging/list.xml', context, context_instance=RequestContext(request))

@csrf_exempt
@render_to_json(indent=2)
def listjson(request, *args, **kwargs):
    request.is_text_exception = True
    data = request.POST
    try:
        authkey = data["authkey"]
    except KeyError:
        print "authkey not found"
        return http.HttpResponse('No permission without valid key.', status=403)
    
    try:
        protocol_version = data["protocol_version"]
    except KeyError:
        protocol_version = 1 # First version
    
    # First determine packageAuth client
    try:
        packageauth = ClientPackageAuth.objects.get(key=authkey)
    except ClientPackageAuth.DoesNotExist:
        print "packagehost not found with key [%s]" % (authkey,)
        return http.HttpResponse('No permission without valid key.', status=403)
    
    # Filter platform
    try:
        platform = data["platform"]
    except KeyError:
        print "platform not found."
        return http.HttpResponse('Review protocol: platform not specified.')
    
    platform_q = Q(platform__identifier=platform) | Q(platform__isnull=True)
    
    qs = Package.objects.filter(platform_q, client=packageauth.client.id)
    
    qs = qs.order_by("template__kind__name")
    qs = qs.order_by("template__name")
    
    ABSOLUTE_PATH =  "%s://%s" % (request.is_secure() and "https" or "http", request.get_host(),)
    response = {
        "client": unicode(packageauth.client.label),
        "packages": [],
    }
    
    for p in qs:
        if not p.file:
            continue
        package_dict = {
            "name": unicode(p.template.name),
            "description": unicode(p.template.description),
            "required": p.required,
            "length": p.file.size,
            "sha1": unicode(p.sha1),
            "full_url": "%s%s" % (ABSOLUTE_PATH, unicode(p.download_url()),),
            "url": "%s" % (unicode(p.download_url()),),
            "filename": unicode(os.path.basename(p.file.name)),
            "platform": {
                "name": unicode(p.platform.name),
                "description": unicode(p.platform.description),
                "identifier": unicode(p.platform.identifier),
            },
            "version": {
                "major": p.version_major,
                "minor": p.version_minor,
                "revision": p.revision,
                "full": p.version,
            },
        }
        response["packages"].append(package_dict)
    return response

@csrf_exempt
def get_id(request, package_id):
    package = get_object_or_404(Package, pk=package_id)
    file = package.file
    
    response = http.HttpResponse(content_type="application/octet-stream")
    response['Cache-Control'] = 'no-cache'
    response['Pragma'] = 'no-cache'
    response['Content-Transfer-Encoding'] = 'binary'
    try:
        response["Content-Disposition"] = "attachment; filename=\"%s\"" % file.name
    except UnicodeEncodeError:
        ext = file.filename.split(".")[-1]
        response["Content-Disposition"] = "attachment; filename=package%s.%s" % (file_id, ext)
    
    response["Content-Length"] = file.size
    for c in file.chunks(chunk_size=512*1024): # 512kiB chunk
        response.write(c)
    print response["Content-Disposition"]
    response.flush()
    return response
