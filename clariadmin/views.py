# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext
from django.contrib.auth.decorators import permission_required
from django.conf import settings
from django.views.generic import list_detail
from django.http import HttpResponse, Http404
from django.db.models import Q

from clariadmin.models import Host, HostType
from clariadmin.forms import *
from common.diggpaginator import DiggPaginator
from operator import ior

def filter_hosts(qs, sorting, search, search_extra=False):
    search_mapping={'ip': 'istartswith',
        'hostname': 'icontains',
        'commentaire': 'icontains',
        'status': 'icontains'
        }
    try:
        if search:
            for key, value in search.iteritems():
                if value:
                    try:
                        lookup = search_mapping[key]
                    except KeyError:
                        lookup = 'exact'
                    if key == 'site':
                        qs= qs.filter_by_site(value)
                    else:
                        qs = qs.filter(**{"%s__%s"%(key,lookup):value})
    except AttributeError:
        pass
    try:
        if search_extra:
            for key, value in search_extra.iteritems():
                if value:
                    qs = qs.filter(Q(additionnalfield__field__id__exact=key.replace("val_","")) &
                                   Q(additionnalfield__value__icontains=value))
    except AttributeError:
        pass
    return qs.order_by(sorting)

def global_search(search,qs):
    fks={'os':'name','site':'label','supplier':'name','type':'text'}
    return qs.filter((Q(additionnalfield__field__fast_search__exact=True)
            & Q(additionnalfield__value__icontains=search))
            | reduce(ior,(Q(**{key+"__icontains":search}) for key in SearchHostForm.Meta.fields if key not in fks.keys()))
            | reduce(ior,(Q(**{"%s__%s__icontains"%(key,value):search}) for key,value in  fks.iteritems()))).distinct()

def get_host_or_404(user,*args, **kw):
    h=get_object_or_404(Host,*args,**kw)
    if not h.available_for(user):
        raise Http404
    return h

@permission_required("clariadmin.can_access_clariadmin")
def list_all(request, *args, **kw):
    """
    Liste toutes les machines sans aucun filtre
        variables de session utilisées:
            global_search_adm_list : dernier mot clef de recherche globale
            filter_adm_list : dernier formulaire de rechere
            filter_extra_adm_list : dernier formulaire de recherche (extra_fields)
            sort_adm_list : dernier tri
    """
    new_search=False
    form_extra=False
    search = kw.pop('global_search',False)
    qs = Host.objects.filter_by_user(request.user)
    if search:
        qs = global_search(search, qs)
        if request.session.get("global_search_adm_list",False)!=search:
            new_search=True
        else:
            request.session["global_search_adm_list"]=search
    if request.POST:
        form = SearchHostForm(request.POST)
        if form.is_valid():
            post_filtred=dict((k,v)for k,v in request.POST.iteritems() if k in form.Meta.fields)
            if request.session.get('filter_adm_list',{})!=post_filtred:
                new_search=True
                request.session['filter_adm_list']=post_filtred
            host_type = request.session.get('filter_adm_list',{}).get('type', False)
            if host_type:
                form_extra = ExtraFieldForm.get_form(request.POST, host=HostType.objects.get(pk=host_type))
                request.session['filter_extra_adm_list']=dict([(k,v) for k,v in request.POST.iteritems() if k in form_extra.fields.keys()])
                form_extra.is_valid()
    else:
        form = SearchHostForm(request.session.get('filter_adm_list',{}))
        host_type = request.session.get('filter_adm_list',{}).get('type', False)
        if host_type:
            form_extra = ExtraFieldForm.get_form((request.session.get('filter_extra_adm_list',{})),host=HostType.objects.get(pk=host_type))
            form_extra.is_valid()

    columns = ["id", "hostname","ip", "site", "type", "os", "model", "inventory", "status"]
    sorting=request.session.get("sort_adm_list","-id")
    paginator = DiggPaginator(
        filter_hosts(qs, sorting, form.is_valid() and form.cleaned_data,
            form_extra and form_extra.cleaned_data),
        settings.TICKETS_PER_PAGE, body=5, tail=2, padding=2)
    if request.GET.get('sort', False):
        request.session["sort_adm_list"]=request.GET.get('sort', False)
    if request.GET.get('page', False):
        request.session["page_adm_list"]=request.GET.get('page', False)
    page = paginator.page(1 if new_search else request.session.get('page_adm_list', 1)
        if int(request.session.get('page_adm_list', 1)) <= paginator.num_pages else 1)
    return render_to_response("clariadmin/list.html", {
        "page": page,
        "form": form,
        "columns": columns,
        "sorting": sorting,
        "form_extra":form_extra
    }, context_instance=RequestContext(request))

@permission_required("clariadmin.can_access_clariadmin")
def new(request, from_host=False):
    """
    Create a new host.
    """
    if from_host:
        n = get_host_or_404(request.user, pk=from_host).copy_instance()
        return redirect(n)
    if request.POST:
        form = HostForm(request.POST)
        if form.is_valid():
            host = form.save()
            return redirect(host)
    else:
        form = HostForm()

    return render_to_response('clariadmin/host.html', {
            'form': form,
            'additionnal_fields':None }, context_instance=RequestContext(request))

@permission_required("clariadmin.can_access_clariadmin")
def modify(request, host_id):
    host = get_host_or_404(request.user, pk=host_id)
    if request.user.site not in (host.site, host.site.parent, host.site.parent.parent):
        a
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
            return redirect("/clariadmin/list/all")
    return render_to_response("clariadmin/host.html", {
        "form": form,
        'additionnal_fields':form_comp,
        "host": host}, context_instance=RequestContext(request))

@permission_required("clariadmin.can_access_clariadmin")
def new_extra_field(request):
    form = NewExtraFieldForm(request.POST)
    if form.is_valid():
        cd=form.cleaned_data
        ParamAdditionnalField(name=cd["name"], host_type=cd["host_type"],
                data_type=cd["data_type"], fast_search=cd["fast_search"],
                default_values=form.get_default_values()).save()
    return render_to_response("clariadmin/extra_field.html", {
        u"form" : form,
        }, context_instance=RequestContext(request))

@permission_required("clariadmin.can_access_clariadmin")
def ajax_extra_fields_form(request, host_id, blank=False):
    if int(host_id) < 0:
        return HttpResponse("<tr></tr>")
    host_type = get_object_or_404(HostType, pk=host_id)
    form=ExtraFieldForm.get_form(host=host_type, blank=bool(blank))
    return HttpResponse(form.as_table())

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
    return render_to_response("clariadmin/extra_field.html",{
        "form": form,
        "field": c_field,}, context_instance=RequestContext(request))
