# -*- coding: utf-8 -*-

import re

from django.core import validators
from django.http import HttpResponse
from django.template import RequestContext
from dojango.decorators import json_response
from django.shortcuts import render_to_response
from django.core.exceptions import ValidationError
from django.contrib.auth.decorators import permission_required

from clariadmin.models import Host
from common.models import Client, HostChar


@permission_required("clariadmin.can_access_clariadmin")
def ajax_load_host_client(request, client_id):
    # List all the host of the current user
    host_list = HostChar.objects.filter(client=client_id)
    ip_table = []
    for host in host_list:
        host_ip = host.host.ip.split()
        for ip in host_ip:
            try:
                validators.validate_ipv4_address(ip)
                ip_table.append([host.host.site,
                                 ip, host.host.type,
                                 host.name])
            except ValidationError:
                pass
    return render_to_response('hostclient.html',
                              {"host_list": ip_table},
                              context_instance=RequestContext(request))

@permission_required("clariadmin.can_access_clariadmin")
@json_response
def ajax_delete_host_client(request):
    # Delete an host from many to many field client host
    host = HostChar.objects.get(host=request.POST['host_id'],
                                client=request.POST['client_id'])
    response_dict = {'hostchar_delete_id': str(host.id)}
    host.delete()
    return response_dict


@permission_required("clariadmin.can_access_clariadmin")
@json_response
def ajax_add_host_client(request):
    # Add an host to many to many field client host
    currenthost = Host.objects.get(pk=request.POST['host_id'])
    currentclient = Client.objects.get(pk=request.POST['client_id'])
    # control if the data to create allready exist
    # protection for integrity error in data base
    try:
        HostChar.objects.get(host=currenthost, client=currentclient)
        response_dict = {'hostchar_add_id': 'already existing, nothing to do.',
                         'error': 'true'}
        return response_dict
    except HostChar.DoesNotExist:
        currentname = request.POST['name']
        currentmany = HostChar(host=currenthost,
                               client=currentclient,
                               name=currentname)
        currentmany.save()
        response_dict = {'hostchar_add_id': str(currenthost.id)}
        return response_dict
