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
    new_search=False
    search_mapping={'ip': 'istartswith',
        'hostname': 'icontains',
        'commentaire': 'icontains',
        'status': 'icontains'
        }
    if request.POST:
        form = SearchHostForm(request.POST)
        if form.is_valid():
            if request.session.get('filter_adm_list',{})!=request.POST:
                new_search=True
                request.session['filter_adm_list']=request.POST
    else:
        form = SearchHostForm(request.session.get('filter_adm_list',{}))
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
    columns = ["id", "hostname","ip", "site", "type", "os", "model", "inventory", "status"]
    sorting=request.session.get("sort_adm_list","-id")
    qs = qs.order_by(sorting)
    paginator = DiggPaginator(qs, settings.TICKETS_PER_PAGE, body=5, tail=2, padding=2)
    if request.GET.get('sort', False):
        request.session["sort_adm_list"]=request.GET.get('sort', False)
    if request.GET.get('page', False):
        request.session["page_adm_list"]=request.GET.get('page', False)
    current_page_num = (1 if new_search else request.session.get('page_adm_list', 1)
            if int(request.session.get('page_adm_list', 1)) <= paginator.num_pages else 1)
    page = paginator.page(current_page_num)
    return render_to_response("clariadmin/list.html", {
        "page": page,
        "form": form,
        "columns": columns,
        "sorting": sorting,
    }, context_instance=RequestContext(request))

@permission_required("clariadmin.can_access_clariadmin")
def new(request, from_host=False):
    """
    Create a new host.
    """
    if from_host:
        n = get_object_or_404(Host, pk=from_host).copy_instance()
        return redirect(n)
    if request.POST:
        form = HostForm(request.POST)
        if form.is_valid():
            host = form.save()
            return redirect(host)
    else:
        form = HostForm()

    return render_to_response('clariadmin/host.html', {'form': form, 'additionnal_fields':None }, context_instance=RequestContext(request))

@permission_required("clariadmin.can_access_clariadmin")
def modify(request, host_id):
    host = get_object_or_404(Host, pk=host_id)
    if not request.POST:
        form = HostForm(instance=host)
        form_comp = ExtraFieldForm.get_form(host=host)
    else:
        if request.POST.get("delete",False):
            host.delete()
            return redirect("/clariadmin/list/all")
        form = HostForm(request.POST, instance=host)
        form_comp = ExtraFieldForm.get_form(data=request.POST, host=host)

    if request.POST:
        if form_comp.is_valid():
            form_comp.save()
        if form.is_valid():
            form.save()
        if request.GET.get("from_list",False):
            return redirect("/clariadmin/list/all")

    return render_to_response("clariadmin/host.html", {"form": form,
        'additionnal_fields':form_comp, "host": host}, context_instance=RequestContext(request))

@permission_required("clariadmin.can_access_clariadmin")
def new_extra_field(request):
    form = NewExtraFieldForm(request.POST)
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
