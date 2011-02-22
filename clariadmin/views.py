# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext
from django.contrib.auth.decorators import permission_required
from django.conf import settings
from django.views.generic import list_detail
from django.http import HttpResponse, Http404
from django.db.models import Q

from clariadmin.models import Host, HostType
from clariadmin.forms import HostForm, SearchHostForm, AdditionnalFieldForm
from common.diggpaginator import DiggPaginator
from operator import ior
from itertools import chain

def filter_hosts(qs, sorting, search, search_extra=False):
    search_mapping={'ip': 'icontains',
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
            sort_adm_list : dernier tri
    """
    #declare
    new_search = False
    form_extra = False
    reset=False
    qs = Host.objects.filter_by_user(request.user)

    #instanciate forms
    if request.POST:
        reset = request.POST.get('filter_reset',False)
        form = SearchHostForm(request.user,request.POST if not reset else {})
        if form.is_valid():
            post_filtred = dict((k,v) for k,v in request.POST.iteritems()
                                if k in chain(form.Meta.fields,("global_search",)))
            if request.session.get('filter_adm_list',{})!=post_filtred:
                new_search=True
                request.session['filter_adm_list']=post_filtred
            host_type = request.session.get('filter_adm_list',{}).get('type', False)
            if host_type:
                form_extra = AdditionnalFieldForm.get_form(request.POST if not reset else {}, host=HostType.objects.get(pk=host_type))
                request.session['filter_extra_adm_list'] = dict(
                    [(k,v) for k,v in request.POST.iteritems()
                        if k in form_extra.fields.keys()])
                form_extra.is_valid()
    else:
        form = SearchHostForm(request.user,request.session.get('filter_adm_list',{}))
        host_type = request.session.get('filter_adm_list',{}).get('type', False)
        if host_type:
            form_extra = AdditionnalFieldForm.get_form((request.session.get('filter_extra_adm_list',{})),host=HostType.objects.get(pk=host_type))
            form_extra.is_valid()

    #global_search
    search = form.cleaned_data.pop('global_search',False) if form.is_valid() else False
    if search:
        qs = global_search(search, qs)

    #get session/GET parametters
    sorting=request.GET.get('sort',request.session.get("sort_adm_list", '-id'))
    if request.GET.get('sort', False):
        request.session["sort_adm_list"]=request.GET.get('sort', False)
    if request.GET.get('page', False):
        request.session["page_adm_list"]=request.GET.get('page', False)

    #fill paginator
    paginator = DiggPaginator(
        filter_hosts(qs, sorting, form.is_valid() and form.cleaned_data,
            form_extra and form_extra.get_data()),
        settings.TICKETS_PER_PAGE, body=5, tail=2, padding=2)
    page = paginator.page(1 if new_search else request.session.get('page_adm_list', 1)
        if int(request.session.get('page_adm_list', 1)) <= paginator.num_pages else 1)
    return render_to_response("clariadmin/list.html", {
        "page": page,
        "form": form,
        "columns": ("hostname","ip", "site", "type", "os", "model", "status"),
        "sorting": sorting,
        "form_extra":form_extra
    }, context_instance=RequestContext(request))

@permission_required("clariadmin.can_access_clariadmin")
def new(request, from_host=False):
    """
    Create a new host.
    """
    add_fields=None
    if from_host and not request.POST:
        inst, comp = get_host_or_404(request.user, pk=from_host).copy_instance()
        form = HostForm(request.user, instance=inst)
        add_fields = AdditionnalFieldForm.get_form(comp, host=inst)
    elif request.POST:
        filtered_POST = HostForm.filter_querydict(request.user, 'HostForm', request.POST)
        form = HostForm(request.user, filtered_POST)
        if form.is_valid():
            host = form.save()
            form_comp = AdditionnalFieldForm.get_form(data=request.POST, host=host)
            if form_comp.is_valid():
                form_comp.save()
            redir=request.POST.get('submit_button',False)
            if redir == 'new':
                pass
            elif redir == 'save':
                return redirect(host)
            elif redir == 'return':
                return redirect('list_hosts')
    else:
        form = HostForm(request.user)
    return render_to_response('clariadmin/host.html', {
            'form': form,
            'additionnal_fields':add_fields }, context_instance=RequestContext(request))

@permission_required("clariadmin.can_access_clariadmin")
def modify(request, host_id):
    host = get_host_or_404(request.user, pk=host_id)
    if not request.POST:
        form = HostForm(request.user,instance=host)
        form_2 = AdditionnalFieldForm.get_form(host=host)
    else:
        if request.POST.get("delete",False):
            host.delete()
            return redirect('list_hosts')
        form = HostForm(request.user,request.POST, instance=host)
        form_comp = AdditionnalFieldForm.get_form(request.POST, host=host)
        if form_comp.is_valid() and form.is_valid():
            form_comp.save()
            form.save()
            redir=request.POST.get('submit_button',False)
            if redir == 'new':
                return redirect('new_host')
            elif redir == 'save':
                pass
            elif redir == 'return':
                return redirect('list_hosts')
        form_2 = AdditionnalFieldForm.get_form(request.POST, host=host)
    return render_to_response("clariadmin/host.html", {
        "form": form,
        'additionnal_fields':form_2,
        "host": host}, context_instance=RequestContext(request))

@permission_required("clariadmin.can_access_clariadmin")
def ajax_extra_fields_form(request, host_id, blank=False):
    if int(host_id) < 0:
        return HttpResponse("<tr></tr>")
    host_type = get_object_or_404(HostType, pk=host_id)
    form=AdditionnalFieldForm.get_form(host=host_type, blank=bool(blank))
    return HttpResponse(form.as_table())
