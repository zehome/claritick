# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext
from django.contrib.auth.decorators import permission_required
from django.conf import settings
from django.views.generic import list_detail
from django.http import HttpResponse, Http404
from django.db.models import Q
from django.utils import simplejson as json

from clariadmin.models import Host, HostType
from clariadmin.forms import HostForm, SearchHostForm, AdditionnalFieldForm
from common.diggpaginator import DiggPaginator
from operator import ior

def filter_hosts(qs, sorting, search, search_extra={}):
    """
    Returns results according to search and search_extra dictionnays.
    It will look in fields related to the keyword.
    """
    search_mapping={'ip': 'contains',
        'hostname': 'icontains',
        'commentaire': 'icontains',
        'status': 'icontains'
        }
    for key, value in search.iteritems():
        if value:
            lookup = search_mapping.get(key,'exact')
            if key == 'site':
                qs= qs.filter_by_site(value)
            else:
                qs = qs.filter(**{"%s__%s" % (key, lookup): value})
    for key, value in search_extra.iteritems():
        if value:
            qs = qs.filter(Q(additionnalfield__field__id__exact=key.replace("val_",""))
                         & Q(additionnalfield__value__icontains=value))
    return qs.order_by(sorting)

def global_search(user, search, qs):
    """
    Returns results according to search keyword.
    It will look in all available fields.
    """
    fks = {'os': 'name',
           'site':'label',
           'supplier':'name',
           'type':'text'}
    # Filtre les foreign key en fonction du niveau de securite.
    authorized_keys = SearchHostForm.filter_list(user,fks.keys())
    fks = dict([(k,v) for k,v in fks.iteritems()
        if k in authorized_keys])

    # Filter local fields
    fields = SearchHostForm.filter_list(user, SearchHostForm.Meta.fields)
    qs = qs.filter(
        (
            Q(additionnalfield__field__fast_search__exact=True)
            & ~Q(additionnalfield__field__data_type__in=('2','3','6'))
            & Q(additionnalfield__value__icontains=search)
        ) | (
            # Do search only for local fields
            reduce(ior,(Q(**{"%s__icontains" % (key,): search})
                     for key in fields if key not in fks.keys()))
        ) | (
            # Do search on filtered foreign keys
            reduce(ior,(Q(**{"%s__%s__icontains" % (key, value): search})
                     for key, value in fks.iteritems()))
        )
    )
    # Distict is needed because could match 2 fields in the or just above
    return qs.distinct()

def get_host_or_404(user, *args, **kw):
    """wrap get_object_or_404 to restrict access by user"""
    h = get_object_or_404(Host, *args, **kw)
    if not h.available_for(user):
        raise Http404
    return h

@permission_required("clariadmin.can_access_clariadmin")
def list_all(request, *args, **kw):
    """
    Vue permettant de lister les machines que l'on souhaite.
    Variables de session utilisées:
        global_search_adm_list : dernier mot clef de recherche globale
        search_host_form_fields : dernier formulaire de rechere
        additionnal_field_form_fields : dernier formulaire additionnel
        sort_adm_list : dernier tri
    """
    POST = HostForm.filter_querydict(request.user, request.POST)
    new_search = False
    form_extra = False
    sort_default = "-id"
    columns = HostForm.filter_list(request.user, (
        "hostname", "ip", "site", "type", "os", "model", "status"))

    # Récupère le type d'hote pour adapter si besoin l'AdditionnalFieldForm.
    host_type = request.session.get('search_host_form_fields', {}).get('type', False)

    if POST:
        if POST.get('filter_reset', False):
            # Reset form
            form = SearchHostForm(request.user,{})
        else:
            # Init forms
            form = SearchHostForm(request.user, POST )
            if form.is_valid():
                # récupère les éléments de POST propre à SearchHostForm
                post_filtred = dict((k, v) for k, v in POST.iteritems()
                                    if k in form.cleaned_data.keys())

                # si recherche != dernière recherche, retour page 1 et update session
                if request.session.get('search_host_form_fields', {}) != post_filtred:
                    new_search = True
                    request.session['search_host_form_fields'] = post_filtred

                if host_type:
                    form_extra = AdditionnalFieldForm.get_form(POST,
                                 host_type=HostType.objects.get(pk=host_type))
                    # if search != last search => page 1 and update session
                    post_filtred = dict([(k,v) for k,v in POST.iteritems()
                                            if k in form_extra.fields.keys()])
                    if request.session.get('additionnal_field_form_fields',{}) != post_filtred:
                        new_search = True
                        request.session['additionnal_field_form_fields'] = post_filtred
                    form_extra.is_valid()
    else:
        form = SearchHostForm(request.user, request.session.get('search_host_form_fields', {}))
        if host_type:
            form_extra = AdditionnalFieldForm.get_form((request.session.get('additionnal_field_form_fields',{})),host_type=HostType.objects.get(pk=host_type))
            form_extra.is_valid()

    # filter SearchHostFrom
    form.fields = SearchHostForm.filter_querydict(request.user, form.fields)

    # get sorting
    sorting = sort_default
    sort_get = request.GET.get('sort',
                               request.session.get("sort_adm_list", sort_default))
    if sort_get in columns:
        sorting = sort_get
    if sort_get.startswith('-') and sort_get[1:] in columns:
        sorting = sort_get
    request.session["sort_adm_list"] = sorting

    # apply searchs if any.
    qs = Host.objects.none()
    if form.is_valid():
        search = form.cleaned_data.pop('global_search', False)
        if search or [e for e in form.cleaned_data.values() if e]:
            qs = Host.objects.filter_by_user(request.user)
            if search:
                qs = global_search(request.user, search, qs)
            if form_extra:
                qs = filter_hosts(qs, sorting, form.cleaned_data,
                     form_extra.get_data())
            else:
                qs = filter_hosts(qs, sorting, form.cleaned_data)
            form.update(qs)

    # fill paginator
    paginator = DiggPaginator(qs, settings.TICKETS_PER_PAGE, body=5, tail=2, padding=2)

    # get page
    page_num = 1
    page_asked = int(request.session.get('page_adm_list',
                                         request.GET.get('page', 1)))
    if ((page_asked <= paginator.num_pages) and not new_search):
        page_num = page_asked
    request.session["page_adm_list"] = page_num
    page = paginator.page(page_num)

    return render_to_response("clariadmin/list.html", {
        "page": page,
        "form": form,
        "columns": columns,
        "sorting": sorting,
        "form_extra": form_extra
    }, context_instance=RequestContext(request))

@permission_required("clariadmin.can_access_clariadmin")
def new(request, from_host=False):
    """
    View to Create a new host. (eventualy copied from an existing one)
    """
    POST = HostForm.filter_querydict(request.user, request.POST)
    add_fields = None

    if POST:
        form = HostForm(request.user, POST)
        if form.is_valid():
            host = form.save()
            form_comp = AdditionnalFieldForm.get_form(data = POST, host = host)
            if form_comp.is_valid():
                form_comp.save()
            redir = POST.get('submit_button', False)
            if redir == 'new':
                form = HostForm(request.user)
            elif redir == 'save':
                return redirect(host)
            elif redir == 'return':
                return redirect('list_hosts')
    else:
        if from_host:
            inst, comp = get_host_or_404(request.user, pk = from_host).copy_instance()
            form = HostForm(request.user, instance = inst)
            add_fields = AdditionnalFieldForm.get_form(comp, host = inst)
        else:
            form = HostForm(request.user)
    return render_to_response('clariadmin/host.html', {
            'form': form,
            'additionnal_fields': add_fields},
            context_instance=RequestContext(request))

@permission_required("clariadmin.can_access_clariadmin")
def modify(request, host_id):
    """
    View to modify a Host.
    """
    POST = HostForm.filter_querydict(request.user, request.POST)
    host = get_host_or_404(request.user, pk=host_id)

    if POST:
        if POST.get("delete", False):
            host.delete()
            return redirect('list_hosts')
        form = HostForm(request.user, POST, instance=host)
        add_fields = AdditionnalFieldForm.get_form(POST, host=host)
        if add_fields.is_valid() and form.is_valid():
            add_fields.save()
            form.save()
            redir = POST.get('submit_button', False)
            if redir == 'new':
                return redirect('new_host')
            elif redir == 'save':
                pass
            elif redir == 'return':
                return redirect('list_hosts')
        #add_fieds = AdditionnalFieldForm.get_form(POST, host=host)
    else:
        form = HostForm(request.user,instance=host)
        add_fields = AdditionnalFieldForm.get_form(host=host)

    return render_to_response("clariadmin/host.html", {
        "form": form,
        'additionnal_fields': add_fields,
        "host": host}, context_instance=RequestContext(request))

@permission_required("clariadmin.can_access_clariadmin")
def ajax_extra_fields_form(request, host_type_id, blank=False):
    """
    Return raw html (tr) AdditionnalFieldForm for given host_type_id.
    blank parametter allow to have empty fields instead of defaults.
    """
    try:
        host_type = get_object_or_404(HostType, pk=host_type_id)
    except:
        return HttpResponse("<tr></tr>")
    form=AdditionnalFieldForm.get_form(host_type=host_type, blank=bool(blank))
    return HttpResponse(form.as_table())
