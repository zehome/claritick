# -*- coding: utf-8 -*-

from django import http
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.db import models
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils.html import escape
from django.contrib.auth.decorators import login_required, permission_required
from django.conf import settings
from django.views.generic import list_detail
from django.utils import simplejson

from claritick.ticket.models import Ticket, TicketView
from claritick.ticket.forms import *
from claritick.ticket.tables import DefaultTicketTable

from claritick.common.diggpaginator import DiggPaginator
from claritick.common.models import Client, UserProfile
from common.exceptions import NoProfileException

def get_filters(request):
    if request.method == "POST":
        return request.POST
    return request.session["list_filters"]

def set_filters(request, datas=None):
    request.session["list_filters"] = request.POST.copy()
    if datas:
        request.session["list_filters"].update(datas)

@login_required
def list_me(request, *args, **kw):
    form = None
    if not request.POST.get("assigned_to", None):
        form = SearchTicketForm({'assigned_to': request.user.id}, get_filters(request), user=request.user)
        set_filters(request, form.data)
    return list_all(request, form, *args, **kw)

@login_required
def list_unassigned(request, *args, **kw):
    filterdict = {'assigned_to__isnull': True}
    set_filters(request, filterdict)
    return list_all(request, None, filterdict = filterdict, *args, **kw)

@login_required
def list_all(request, form=None, filterdict=None, view_id=None, *args, **kw):
    """
    
    Liste tous les tickets sans aucun filtre
    """
    search_mapping={'title': 'icontains',
        'text': 'icontains',
        'contact': 'icontains',
        'keywords': 'icontains',
    }

    action_form = TicketActionsForm(request.POST)
    action_form.process_actions()

    if request.GET.get("reset", False) or view_id is not None:
        request.session["list_filters"] = {}

    if view_id is not None:
        view = TicketView.objects.get(pk=view_id)
        set_filters(request, view.filters)

    if not form:
        if request.method == "POST":
            set_filters(request, filterdict)
        form = SearchTicketForm(get_filters(request), user=request.user)

    form.is_valid()

    if not form.cleaned_data.get("state"):
        qs = Ticket.open_tickets.all()
    else:
        qs = Ticket.tickets.all()

    # unassigned
    if filterdict:
        qs = qs.filter(**filterdict)

    # Form cleaned_data ?
    if form.cleaned_data:
        cd = form.cleaned_data
        for key, value in cd.items():
            try:
                if value:
                    try:
                        lookup = search_mapping[key]
                    except KeyError:
                        lookup = 'exact'
                    qs = qs.filter(**{"%s__%s"%(key,lookup):value})
            except AttributeError:
                pass

    # On va filtrer la liste des tickets en fonction de la relation user => client
    try:
        client_list = request.user.get_profile().get_clients()
        qs = qs.filter(client__pk__in=[x.id for x in client_list])
    except UserProfile.DoesNotExist:
        raise NoProfileException(request.user)

    qs = qs.order_by(request.GET.get('sort', '-id'))

    if request.user.has_perm("can_commit_full"):
        template_name = ""
    
    # On va enregistrer les criteres actuels en tant que nouvelle liste
    saved_list_form = SavedListForm(request.POST, user=request.user)
    if request.method == "POST" and request.POST.get("save_new_list", False) and saved_list_form.is_valid():
        tuf, created = TicketView.objects.get_or_create(user=request.user, name=saved_list_form.cleaned_data["filter_list"])
        tuf.filters = form.data
        tuf.save()

    columns = ["Priority", "Client", "Category", "Project", "Title", "Comments", "Contact", "Last modification", "Opened by", "Assigned to"]
    return list_detail.object_list(request, queryset=qs,  paginate_by=settings.TICKETS_PER_PAGE, page=request.GET.get("page", 1),
        template_name="ticket/list.html", extra_context={
            "form": form, 
            "columns": columns, 
            "saved_list_form": saved_list_form,
            "action_form": action_form,
        })

@permission_required("ticket.add_ticket")
@login_required
def partial_new(request, form=None):
    """
    Create a new ticket.
    """
    if not form:
        form = PartialNewTicketForm()
    return render_to_response('ticket/partial_new.html', {'form': form }, context_instance=RequestContext(request))

@permission_required("ticket.add_ticket")
@login_required
def new(request):
    """
    Create a new ticket.
    """
    
    form = PartialNewTicketForm(request.POST)
    if not form.is_valid():
        return partial_new(request, form)
    
    ticket = form.save(commit=False)
    ticket.opened_by = request.user
    ticket.title = "Invalid title"
    ticket.state = None
    ticket.save()
    return redirect("/ticket/modify/%d" % (ticket.id,) )

@permission_required("ticket.change_ticket")
@login_required
def modify(request, ticket_id):
    ticket = get_object_or_404(Ticket, pk=ticket_id)

    # On verifie que l'utilisateur a les droits de modifier le ticket_id
    try:
        if ticket.client and ticket.client not in request.user.get_profile().get_clients():
            raise PermissionDenied()
    except UserProfile.DoesNotExist:
        raise NoProfileException(request.user)

    if not ticket.text:
        ticket.title = None
        ticket.state = State.objects.get(pk=1)
        ticket.priority = Priority.objects.get(pk=2)
        ticket.validated_by = request.user
    
    if request.method == "POST":
        form = NewTicketForm(request.POST, instance=ticket, user=request.user)
        if form.is_valid():
            form.save()
    else:
        form = NewTicketForm(instance=ticket, user=request.user)

    if request.user.has_perm("ticket.add_ticket_full"):
        template_name = "ticket/modify.html"
    else:
        template_name = "ticket/modify_small.html"

    return render_to_response(template_name, {"form": form, "ticket": ticket}, context_instance=RequestContext(request))
