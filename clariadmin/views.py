# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext
from django.contrib.auth.decorators import login_required

from claritick.clariadmin.models import Host
from claritick.clariadmin.forms import *
from claritick.clariadmin.tables import DefaultHostTable

@login_required
def list_all(request, *args, **kw):
    """
    
    Liste tous les tickets sans aucun filtre
    """
    form = SearchHostForm(request.POST)
    form.is_valid()
    
    qs = Host.objects.all()
    
    # Form cleaned_data ?
    try:
        if form.cleaned_data:
            cd = form.cleaned_data
            for key, value in cd.items():
                if value:
                    qs = qs.filter(**{key:value})
    except AttributeError:
        pass
    table = DefaultHostTable(data=qs, order_by=request.GET.get('sort', 'title'))
    
    return render_to_response('clariadmin/list.html', {'table': table, 'form': form }, context_instance=RequestContext(request))

@login_required
def new(request):
    """
    Create a new host.
    """
    
    form = HostForm(request.POST)
    if request.POST:
        if form.is_valid():
            host = form.save()
            return redirect(host.get_absolute_url())
    return render_to_response('clariadmin/host.html', {'form': form }, context_instance=RequestContext(request))

@login_required
def modify(request, host_id):
    host = get_object_or_404(Host, pk=host_id)
    if not request.POST:
        form = HostForm(instance=host)
    else:
        form = HostForm(request.POST, instance=host)
    
    if request.POST:
        if form.is_valid():
            form.save()
    return render_to_response("clariadmin/host.html", {"form": form, "host": host}, context_instance=RequestContext(request))

