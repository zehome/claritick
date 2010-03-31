# -*- coding: utf-8 -*-

from django import http
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied, FieldError
from django.db import models
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext
from django.contrib.auth.decorators import login_required, permission_required
from django.core.urlresolvers import reverse

from django.contrib.comments.forms import CommentForm
from django.contrib.comments.views.comments import post_comment

from claritick.ticket.models import Ticket, TicketView
from claritick.ticket.forms import *

from claritick.common.diggpaginator import DiggPaginator
from claritick.common.models import Client, UserProfile
from common.exceptions import NoProfileException
from common.utils import user_has_perms_on_client

def get_filters(request):
    if "list_filters" in request.session:
        return request.session["list_filters"]
    return {}

def set_filters(request, datas=None):
    if not "list_filters" in request.session:
        request.session["list_filters"] = {}
    if request.method == "POST":
        request.session["list_filters"] = request.POST.copy()
    if datas:
        request.session["list_filters"].update(datas)

def filter_quersyset(qs, filters):
    """
        Filtre un queryset de ticket a partir d'un dictionnaire de fields lookup.
    """
    search_mapping = {
        'title': 'icontains',
        'text': 'icontains',
        'contact': 'icontains',
        'keywords': 'icontains',
    }

    d = {}
    for key, value in filters.items():
        try:
            if value:
                try:
                    lookup = search_mapping[key]
                except KeyError:
                    if isinstance(value, (list, models.query.QuerySet)):
                        lookup = "in"
                    else:
                        lookup = 'exact'
                qs = qs.filter(**{"%s__%s"%(str(key),lookup): value})
        except (AttributeError, FieldError):
            pass

    return qs

def filter_ticket_by_user(qs, user):
    """
        Filtre un queryset de ticket en fonction des clients qu'a le droit de voir l'utilisateur.
    """
    try:
        client_list = user.get_profile().get_clients()
        qs = qs.filter(client__pk__in=[x.id for x in client_list])
    except UserProfile.DoesNotExist:
        raise NoProfileException(request.user)

    return qs

def add_order_by(queryset, request):
    """
        Rajoute le orderby au queryset en fonction du GET de la requete.
    """
    sort = request.GET.get('sort', 'id')
    sort_order = int(request.GET.get("sort_order", 1))
    return queryset.order_by("%s%s" % (not sort_order and "-" or "", sort))

def get_context(request):
    """
        Context commun aux listes de tickets.
    """
    return {
        "TICKET_STATE_CLOSED": settings.TICKET_STATE_CLOSED,
        "sort_order": int(not int(request.GET.get("sort_order", 1)))
    }

def get_pagination(queryset, request):
    """
        Mets en place la pagination via DiggPaginator.
    """
    paginator = DiggPaginator(queryset, settings.TICKETS_PER_PAGE, body=5, tail=2, padding=2)
    return paginator.page(request.GET.get("page", 1))

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
    return list_all(request, None, filterdict = filterdict, *args, **kw)

@login_required
def list_nonvalide(request):
    """
        Liste des tickets à valider.
    """
    filterdict = {"validated_by__isnull": True}
    return list_all(request, filterdict=filterdict)

@login_required
def list_view(request, view_id=None):
    context = get_context(request)
    data = request.POST

    # On charge la vue de la liste
    if view_id:
        view = get_object_or_404(TicketView, pk=view_id, user=request.user)
        if request.method == "POST" and request.POST.get("validate-filters", None):
            if request.POST.get("delete_view", None):
                view.delete()
                return redirect("ticket_list")
            data = request.POST.copy()
        else:
            data = view.filters
            data.update({"view_name": view.name})
        context["view"] = view

    # le form de filtres
    form = SearchTicketViewForm(data, user=request.user)

    # le template a charger
    if request.user.has_perm("can_commit_full") or request.user.is_superuser:
        template_name = "ticket/view.html"
    else:
        template_name = "ticket/view_small.html"

    # le form d'actions
    if request.user.has_perm("can_commit_full") or request.user.is_superuser:
        action_form = TicketActionsForm(request.POST, prefix="action")
    else:
        action_form = TicketActionsSmallForm(request.POST, prefix="action")

    if action_form.process_actions(request):
        return http.HttpResponseRedirect("%s?%s" % (request.META["PATH_INFO"], request.META["QUERY_STRING"]))

    if not data.get("state"):
        qs = Ticket.open_tickets.all()
    else:
        qs = Ticket.tickets.all()
    
    # On va enregistrer les criteres actuels en tant que nouvelle liste
    if request.method == "POST" and form.is_valid():
        if view_id:
            TicketView.objects.filter(pk=view_id).update(
                name=form.cleaned_data["view_name"],
                filters=form.cleaned_data
            )
        else:
            t = TicketView.objects.create(
                user=request.user,
                name=form.cleaned_data["view_name"],
                filters=form.cleaned_data
            )


        if request.POST.get("validate-filters", None):
            return redirect("ticket_list_view", view_id=view_id or t.pk)

    # On filtre la liste a partir des datas de la vue
    qs = filter_quersyset(qs, data)

    # On va filtrer la liste des tickets en fonction de la relation user => client
    qs = filter_ticket_by_user(qs, request.user)

    # Le tri
    qs = add_order_by(qs, request)

    context.update({
        "form": form,
        "action_form": action_form,
        "tickets": get_pagination(qs, request),
    })

    return render_to_response(template_name, context, context_instance=RequestContext(request))

@login_required
def list_all(request, form=None, filterdict=None, template_name=None, *args, **kw):
    """
        Liste tous les tickets sans aucun filtre
    """
    context = get_context(request)

    if request.user.has_perm("can_commit_full") or request.user.is_superuser:
        action_form = TicketActionsForm(request.POST, prefix="action")
    else:
        action_form = TicketActionsSmallForm(request.POST, prefix="action")

    if action_form.process_actions(request):
        return http.HttpResponseRedirect("%s?%s" % (request.META["PATH_INFO"], request.META["QUERY_STRING"]))

    if request.GET.get("reset", False):
        request.session["list_filters"] = {}
        return http.HttpResponseRedirect(".")

    if not form:
        if request.method == "POST" and request.POST.get("validate-filters", None):
            form = SearchTicketForm(request.POST, user=request.user)
            if form.is_valid():
                set_filters(request, filterdict)
        else:
            form = SearchTicketForm(get_filters(request), user=request.user)

    if not get_filters(request).get("state"):
        qs = Ticket.open_tickets.all()
    else:
        qs = Ticket.tickets.all()

    # Form cleaned_data ?
    if form.is_valid():
        qs = filter_quersyset(qs, form.cleaned_data)

    # unassigned / nonvalide
    if filterdict:
        qs = qs.filter(**filterdict)

    # On va filtrer la liste des tickets en fonction de la relation user => client
    qs = filter_ticket_by_user(qs, request.user)

    # Le tri
    qs = add_order_by(qs, request)

    # TODO choisir le bon template en fonction des permissions
    if template_name is None:
        if request.user.has_perm("ticket.can_list_all") or request.user.is_superuser:
            template_name = "ticket/list.html"
        else:
            template_name = "ticket/list_small.html"

    context.update({
        "form": form, 
        "action_form": action_form,
        "tickets": get_pagination(qs, request),
    })
    return render_to_response(template_name or "ticket/list.html", context, context_instance=RequestContext(request))

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
    #ticket.state = None
    ticket.state = State.objects.get(pk=settings.TICKET_STATE_NEW)
    ticket.priority = Priority.objects.get(pk=settings.TICKET_PRIORITY_NORMAL)
    ticket.save()
    return redirect("ticket_modify", ticket_id=ticket.pk)

@permission_required("ticket.change_ticket")
@login_required
def modify(request, ticket_id):
    ticket = get_object_or_404(Ticket, pk=ticket_id)

    # On verifie que l'utilisateur a les droits de modifier le ticket_id
    if not user_has_perms_on_client(request.user, ticket.client):
        raise PermissionDenied

    if not ticket.text:
        ticket.title = None
        ticket.validated_by = request.user
    
    if request.user.has_perm("ticket.add_ticket_full"):
        template_name = "ticket/modify.html"
        TicketForm = NewTicketForm
    else:
        template_name = "ticket/modify_small.html"
        TicketForm = NewTicketSmallForm

    if request.method == "POST":

        form = TicketForm(request.POST, instance=ticket, user=request.user)
        if not request.POST.get("submit-comment", None):
            comment_form  = CommentForm(ticket)
            if form.is_valid():
                form.save()
                return redirect("ticket_modify", ticket_id=ticket_id)
        else:
            comment_form = CommentForm(ticket, data=request.POST)
            if comment_form.is_valid():
                post_comment(request)
                return redirect("ticket_modify", ticket_id=ticket_id)
    else:
        form = TicketForm(instance=ticket, user=request.user)
        comment_form  = CommentForm(ticket)

    return render_to_response(template_name, {"form": form, "ticket": ticket, "form_comment": comment_form }, context_instance=RequestContext(request))
