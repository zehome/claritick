# -*- coding: utf-8 -*-

from django import http
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils.html import escape
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.views.generic import list_detail

from claritick.ticket.models import Ticket
from claritick.ticket.forms import *
from claritick.ticket.tables import DefaultTicketTable

from claritick.common.diggpaginator import DiggPaginator

@login_required
def list_me(request, *args, **kw):
    form = None
    if not request.POST.get("assigned_to", None):
        form = SearchTicketForm({'assigned_to': request.user.id}, request.POST)
    return list_all(request, form, *args, **kw)

@login_required
def list_unassigned(request, *args, **kw):
    filterdict = {'assigned_to__isnull': True}
    return list_all(request, None, filterdict = filterdict, *args, **kw)

@login_required
def list_all(request, form=None, filterdict=None, *args, **kw):
    """
    
    Liste tous les tickets sans aucun filtre
    """
    search_mapping={'title': 'icontains',
        'text': 'icontains',
        'contact': 'icontains',
        'keywords': 'icontains',
    }

    if not form:
        form = SearchTicketForm(request.POST)
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
    
    qs = qs.order_by(request.GET.get('sort', '-id'))

    return list_detail.object_list(request, queryset=qs, paginate_by=settings.TICKETS_PER_PAGE, page=request.GET.get("page", 1),
        template_name="ticket/list.html", extra_context={"form": form})

@login_required
def partial_new(request, form=None):
    """
    Create a new ticket.
    """
    if not form:
        form = PartialNewTicketForm()
    return render_to_response('ticket/partial_new.html', {'form': form }, context_instance=RequestContext(request))

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

@login_required
def modify(request, ticket_id):
    data = request.POST.copy()
    
    ticket = get_object_or_404(Ticket, pk=ticket_id)
    if not ticket.text:
        ticket.title = None
        ticket.state = State.objects.get(pk=1)
        ticket.priority = Priority.objects.get(pk=2)
        ticket.validated_by = request.user
    
    if request.POST:
        form = NewTicketForm(request.POST, instance=ticket)
    else:
        form = NewTicketForm(instance=ticket)
    
    if data:
        if form.is_valid():
            form.save()

    return render_to_response("ticket/modify.html", {"form": form, "ticket": ticket}, context_instance=RequestContext(request))
