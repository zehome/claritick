# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext
from django.contrib.auth.decorators import permission_required
from django.conf import settings
from django.views.generic import list_detail

from clariadmin.models import Host, CHOICES_FIELDS_AVAILABLE
from clariadmin.forms import *
from common.diggpaginator import DiggPaginator

@permission_required("clariadmin.can_access_clariadmin")
def list_all(request, *args, **kw):
    """
    Liste toutes les machines sans aucun filtre
    """
    search_mapping={'ip': 'istartswith',
        'hostname': 'istartswith'}
    form = SearchHostForm(request.POST)
    form.is_valid()

    qs = Host.objects.all()

    # Form cleaned_data ?
    try:
        if form.cleaned_data:
            cd = form.cleaned_data
            for key, value in cd.items():
                if value:
                    try:
                        lookup = search_mapping[key]
                    except KeyError:
                        lookup = 'exact'
                    qs = qs.filter(**{"%s__%s"%(key,lookup):value})
    except AttributeError:
        pass
    columns = ["id", "hostname", "site", "type", "inventory", "status"]
    sorting=request.GET.get('sort', '-id')
    qs = qs.order_by(sorting)
    paginator = DiggPaginator(qs, settings.TICKETS_PER_PAGE, body=5, tail=2, padding=2)
    page = paginator.page(request.GET.get("page", 1))
    import pdb
    return render_to_response("clariadmin/list.html", {
        "page": page,
        "form": form,
        "columns": columns,
        "sorting": sorting,
    }, context_instance=RequestContext(request))

@permission_required("clariadmin.can_access_clariadmin")
def new(request):
    """
    Create a new host.
    """

    form = HostForm(request.POST)
    if request.POST:
        if form.is_valid():
            host = form.save()
            return redirect(host.get_absolute_url())
    return render_to_response('clariadmin/host.html', {'form': form, 'additionnal_fields':None }, context_instance=RequestContext(request))

@permission_required("clariadmin.can_access_clariadmin")
def modify(request, host_id):
    host = get_object_or_404(Host, pk=host_id)
    if not request.POST:
        form = HostForm(instance=host)
        form_comp = ExtraFieldForm.get_form(host=host)
    else:
        form = HostForm(request.POST, instance=host)
        form_comp = ExtraFieldForm.get_form(data=request.POST, host=host)

    if request.POST:
        if form.is_valid():
            form.save()
        if form_comp.is_valid():
            form_comp.save()
    return render_to_response("clariadmin/host.html", {"form": form,
        'additionnal_fields':form_comp, "host": host}, context_instance=RequestContext(request))

@permission_required("clariadmin.can_access_clariadmin")
def new_extra_field(request):
    form = NewExtraFieldForm(request.POST)
    print form.is_valid()
    if form.is_valid():
        cd=form.cleaned_data
        ParamAdditionnalField(name=cd["name"], host_type=cd["host_type"],
                data_type=cd["data_type"], fast_search=cd["fast_search"],
                default_values=form.get_default_values()).save()
    return render_to_response("clariadmin/extra_field.html",
            {u"form" : form,
            }, context_instance=RequestContext(request))

@permission_required("clariadmin.can_access_clariadmin")
def mod_extra_field(request, field_id):
    c_field = get_object_or_404(ParamAdditionnalField, pk=field_id)
    if request.POST:
        form = NewExtraFieldForm(request.POST)
    else:
        data = {"name":c_field.name,
                "host_type":c_field.host_type.id,
                "data_type":c_field.data_type,
                "fast_search":c_field.fast_search}
        if c_field.data_type=="1":
            data['text_val']=c_field.default_values
        elif c_field.data_type=="2":
            data['bool_val']=c_field.default_values
        elif c_field.data_type=="3" or c_field.data_type=="6":
            data.update(dict(
                [("choice%s_val"%(str(i+1).rjust(2,'0'),),val)
                    for i, val in enumerate(c_field.default_values) ]))
        elif c_field.data_type=="4":
            data['int_val']=c_field.default_values
        elif c_field.data_type=="5":
            data['date_val']=c_field.default_values
        form = NewExtraFieldForm(data)
    if form.is_valid():
        cd=form.cleaned_data
        c_field.name=cd["name"]
        c_field.host_type=cd["host_type"]
        c_field.data_type=cd["data_type"]
        c_field.fast_search=cd["fast_search"]
        c_field.default_values=form.get_default_values()
        c_field.save()
    return render_to_response("clariadmin/extra_field.html",
        {"form": form, "field": c_field,
        }, context_instance=RequestContext(request))
