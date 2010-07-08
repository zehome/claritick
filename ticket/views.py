# -*- coding: utf-8 -*-

import qsstats
import datetime

from django import http
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.db import models
from django.db import connection, transaction
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext
from django.contrib.auth.decorators import login_required, permission_required
from django.core.urlresolvers import reverse

from dojango.decorators import json_response

from ticket.models import Ticket, TicketView, TicketFile
from ticket_comments.views import post_comment
from ticket.forms import *
from django.forms.models import modelformset_factory

from common.diggpaginator import DiggPaginator
from common.models import Client, UserProfile, ClaritickUser
from common.exceptions import NoProfileException
from common.utils import user_has_perms_on_client, filter_form_for_user

from backlinks.decorators import backlink_setter
from django.utils.datastructures import SortedDict

INVALID_TITLE = "Invalid title"

def get_and_child(parents, cqs):
    """ Retourne les valeurs d'un SortedDict avec parents (liste reduite)
    et enfants accessibles par l'attribut enfants, les enfants sont données
    en queryset par le param cqs """
    ret = SortedDict()

    for p in parents:
        p.enfants = []
        p.file = False
        ret[p.id] = p

    parent_ids = ret.keys()
    cqs = cqs.filter(parent__in=parent_ids)
    alarms = TicketAlarm.opened.filter(ticket__in=parent_ids)
    files = TicketFile.objects.select_related().only('id', 'ticket__id').filter(ticket__in=parent_ids)

    for e in cqs:
        ret[e.parent.id].enfants.append(e)

    for a in alarms:
        ret[a.ticket_id].alarm = a

    for f in files:
        ret[f.ticket.id].file = True

    return ret.values()

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
@backlink_setter
def list_me(request, *args, **kw):
    form = None
    if not request.POST.get("assigned_to", None):
        form = SearchTicketForm({'assigned_to': request.user.id}, get_filters(request), user=request.user)
        set_filters(request, form.data)
    return list_all(request, form, *args, **kw)

@login_required
@backlink_setter
def list_unassigned(request, *args, **kw):
    filterdict = {'assigned_to__isnull': True}
    return list_all(request, None, filterdict = filterdict, *args, **kw)

@login_required
@backlink_setter
def list_nonvalide(request):
    """
        Liste des tickets à valider.
    """
    filterdict = {"validated_by__isnull": True}
    return list_all(request, filterdict=filterdict)

@login_required
@backlink_setter
def list_view(request, view_id=None):
    context = get_context(request)
    data = request.POST

    # On charge la vue de la liste
    if view_id:
        view = get_object_or_404(TicketView, pk=view_id, user=request.user)
        if request.method == "POST" and request.POST.get("validate-filters", None):
            if request.POST.get("delete_view", None):
                view.delete()
                return redirect("ticket_list_view")
            data = request.POST.copy()
        else:
            data = view.filters
            data.update({"view_name": view.name})
        context["view"] = view

    # le form de filtres
    form = SearchTicketViewForm(data, user=request.user)

    # le template a charger
    if request.user.has_perm("ticket.can_list_all") or request.user.is_superuser:
        template_name = "ticket/view.html"
    else:
        template_name = "ticket/view_small.html"

    # le form d'actions
    if request.user.has_perm("ticket.can_list_all") or request.user.is_superuser:
        action_form = TicketActionsForm(request.POST, prefix="action")
    else:
        action_form = TicketActionsSmallForm(request.POST, prefix="action")

    if action_form.process_actions(request):
        return http.HttpResponseRedirect("%s?%s" % (request.META["PATH_INFO"], request.META["QUERY_STRING"]))

    if not data.get("state"):
        qs = Ticket.open_tickets.filter(parent__isnull=True)
    else:
        qs = Ticket.tickets.filter(parent__isnull=True)

    cqs = Ticket.tickets.filter(parent__isnull=False)

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
    filters = data.copy()
    if not request.user.has_perm("ticket.can_list_all") and data.get("text"):
        qs = qs.filter_or_child(models.Q(title__icontains=data["title"]) | models.Q(text__icontains=data["text"]), user=request.user)
        del filters["text"]
        cqs = cqs.filter(diffusion=True)
    qs = qs.filter_queryset(filters, user=request.user)

    # On va filtrer la liste des tickets en fonction de la relation user => client
    qs = qs.filter_ticket_by_user(request.user)
    cqs = cqs.filter_ticket_by_user(request.user)

    # Le tri
    qs = qs.add_order_by(request)
    cqs = cqs.add_order_by(request)

    pagination = get_pagination(qs, request)
    pagination.object_list = get_and_child(pagination.object_list, cqs)

    context.update({
        "form": form,
        "action_form": action_form,
        "tickets": pagination,
    })

    return render_to_response(template_name, context, context_instance=RequestContext(request))

@login_required
@backlink_setter
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

    if request.GET.get("reset", False) and request.session.get("list_filters", {}):
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
        qs = Ticket.open_tickets.filter(parent__isnull=True)
    else:
        qs = Ticket.tickets.filter(parent__isnull=True)

    # Form cleaned_data ?
    if form.is_valid():
        data = form.cleaned_data.copy()
        if not request.user.has_perm("ticket.can_list_all") and form.cleaned_data["text"]:
            qs = qs.filter_or_child(models.Q(title__icontains=form.cleaned_data["text"]) | models.Q(text__icontains=form.cleaned_data["text"]), user=request.user)
            del data["text"]
        qs = qs.filter_queryset(data, user=request.user)

    # unassigned / nonvalide
    if filterdict:
        qs = qs.filter_or_child(filterdict, user=request.user)

    # On va filtrer la liste des tickets en fonction de la relation user => client
    qs = qs.filter_ticket_by_user(request.user)
    cqs = Ticket.objects.filter(parent__isnull=False).filter_ticket_by_user(request.user)

    # Le tri
    qs = qs.add_order_by(request)
    cqs = cqs.add_order_by(request)

    # TODO choisir le bon template en fonction des permissions
    if template_name is None:
        if request.user.has_perm("ticket.can_list_all") or request.user.is_superuser:
            template_name = "ticket/list.html"
        else:
            template_name = "ticket/list_small.html"
            cqs = cqs.filter(diffusion=True)

    pagination = get_pagination(qs, request)
    pagination.object_list = get_and_child(pagination.object_list, cqs)

    context.update({
        "form": form, 
        "action_form": action_form,
        "tickets": pagination,
    })
    return render_to_response(template_name or "ticket/list.html", context, context_instance=RequestContext(request))

@permission_required("ticket.add_ticket")
def partial_new(request, form=None):
    """
    Create a new ticket.
    """
    if not form:
        form = PartialNewTicketForm()
    return render_to_response('ticket/partial_new.html', {'form': form }, context_instance=RequestContext(request))

@permission_required("ticket.add_ticket")
def new(request):
    """
    Create a new ticket.
    """
    
    form = PartialNewTicketForm(request.POST)
    if not form.is_valid():
        return partial_new(request, form)
    
    ticket = form.save(commit=False)
    ticket.opened_by = request.user
    ticket.title = INVALID_TITLE
    #ticket.state = None
    ticket.state = State.objects.get(pk=settings.TICKET_STATE_NEW)
    ticket.priority = Priority.objects.get(pk=settings.TICKET_PRIORITY_NORMAL)
    
    if request.user.has_perm("ticket.add_ticket_full"):
        ticket.validated_by = request.user

    ticket.save()
    return redirect("ticket_modify", ticket_id=ticket.pk)

@permission_required("ticket.change_ticket")
def modify(request, ticket_id):
    def exit_action():
        saveaction = request.POST.get("savebutton", "save")
        if saveaction == "save":
            return redirect("ticket_modify", ticket_id=ticket_id)
        elif saveaction == "new":
            return redirect("ticket_partial_new")
        elif saveaction == "return":
            backlinks = request.backlinks
            precedent = backlinks[-1:]
            if not precedent:
                return redirect("ticket_modify", ticket_id=ticket_id) 
            else:
                return precedent[0].redirect(request)
        else:
            raise PermissionDenied("Hacking attempt!")

    qs = Ticket.objects.all().filter_ticket_by_user(request.user, no_client=True)
    ticket = get_object_or_404(qs, pk=ticket_id)

    # Si c'est un fils rediriger vers le pêre au bon endroit
    if ticket.parent:
        return http.HttpResponseRedirect("/ticket/modify/%d/#child%s" % (ticket.parent_id, ticket_id))

    if not ticket.text and ticket.title == INVALID_TITLE:
        ticket.title = None

    # Si le ticket n'est pas rattaché à aucun client, on l'affecte au client de l'utilisateur
    if not ticket.client:
        ticket.client = request.user.get_profile().client

    if request.user.has_perm("ticket.add_ticket_full"):
        template_name = "ticket/modify.html"
        TicketForm = NewTicketForm
        child = ticket.child.order_by('date_open')
        TicketChildForm = ChildForm
    else:
        template_name = "ticket/modify_small.html"
        TicketForm = NewTicketSmallForm
        child = ticket.child.filter(diffusion=True).order_by('date_open')
        TicketChildForm = ChildFormSmall


    ChildFormSet = modelformset_factory(Ticket, form=TicketChildForm, extra=0, can_delete=True)

    if request.method == "POST":
        if request.POST.get("_validate-ticket", None) and request.user.has_perm("ticket.can_validate_ticket")\
            and ticket.validated_by is None:
            ticket.validated_by = request.user
            ticket.save()

        form = TicketForm(request.POST, request.FILES, instance=ticket, user=request.user)

        # Il faut valider les fils en premier pour ne pas se faire jetter si on ferme tout
        child_formset = ChildFormSet(request.POST, queryset=child)
        deleted_forms = child_formset.deleted_forms if hasattr(child_formset, 'deleted_forms') else []

        # Save existing childs
        for f in child_formset.initial_forms:
            if not f in deleted_forms and f.is_valid():
                f.save()
                post_comment(f, request)


        for f in deleted_forms:
            f.instance.delete()

        # Add new childs
        if request.user.has_perm('ticket.can_add_child'):
            for f in child_formset.extra_forms:
                if f.is_valid():
                    new_child = copy_model_instance(ticket)

                    # Valeurs à écraser
                    for a in f.Meta.fields:
                        setattr(new_child, a, f.cleaned_data.get(a))

                    new_child.opened_by = request.user
                    new_child.date_open = datetime.datetime.now()
                    new_child.parent = ticket
                    new_child.save()
                    f.instance = new_child
                    post_comment(f, request)

        if form.is_valid():
            # Si l'utilisateur peut assigner ce ticket à l'utilisateur passé en POST
            if not request.user.is_superuser and form.cleaned_data["assigned_to"] and form.cleaned_data["assigned_to"]\
                    not in ClaritickUser.objects.get(pk=request.user.pk).get_child_users():
                raise PermissionDenied()

            form.save()
            post_comment(form, request)

            # Alarme automatique
            if ticket.priority \
                    and ticket.priority.alarm \
                    and not ticket.ticketalarm_set.all():
                        ticket.ticketalarm_set.create(reason=ticket.priority.alarm,
                                user_open = request.user)

            file = form.cleaned_data["file"]
            if file:
                ticket_file = TicketFile(ticket=ticket, filename=file.name, content_type=file.content_type)
                if file.multiple_chunks():
                    data = None
                    for chunk in file.chunks():
                        data += chunk
                else:
                    data = file.read()
                ticket_file.data = data
                ticket_file.save()

            return exit_action()
    else:
        form = TicketForm(instance=ticket, user=request.user)
        child_formset = ChildFormSet(queryset=child)
        filter_form_for_user(child_formset.forms, request.user)

    return render_to_response(template_name,
            { "form": form, "child_formset": child_formset },
        context_instance=RequestContext(request))

@login_required
def get_file(request, file_id):
    """
        Retourne au client le TicketFile file_id avec le bon mimetype.
    """
    file = get_object_or_404(TicketFile, pk=file_id)

    if not Ticket.minimal.all().filter_ticket_by_user(request.user).get(pk=file.ticket_id):
        raise PermissionDenied

    response = http.HttpResponse(str(file.data), mimetype=file.content_type)
    response["Content-Disposition"] = "attachment; filename=%s" % file.filename
    return response

@permission_required("ticket.can_add_child")
def ajax_load_child(request, ticket_id):
    """
    Renvoie un formulaire HTML pour création d'un fils de ticket_id
    """
    if not ticket_id:
        raise PermissionDenied

    try:
        ticket = Ticket.minimal.all().filter_ticket_by_user(request.user, no_client=True).get(pk=ticket_id)
    except Ticket.DoesNotExist:
        raise PermissionDenied

    prefix = 'form-%d' % (int(request.GET.get('count', 0)))

    if ticket.parent:
        raise PermissionDenied("Ce ticket est déjà un fils")

    if request.user.has_perm("ticket.add_ticket_full"):
        form = ChildForm(user=request.user, prefix=prefix)
        template = "ticket/child.html"
    else:
        form = ChildFormSmall(prefix=prefix)
        template = "ticket/child_small.html"

    return render_to_response(template,
            {"cf": form, },
            context_instance=RequestContext(request))

@permission_required("ticket.can_delete_tma")
def ajax_delete_tma(request, ticket_id):
    """ Supprime le/les tma(s) du ticket """
    if not ticket_id:
        raise PermissionDenied

    try:
        ticket = Ticket.minimal.all().\
            filter_ticket_by_user(request.user, no_client=True).get(pk=ticket_id)
    except Ticket.DoesNotExist:
        raise PermissionDenied

    tma_id = int(request.GET.get('tma_id', 0))

    if not tma_id: # Delete all
        ticket.ticketmailaction_set.all().delete()
    else:
        ticket.ticketmailaction_set.filter(pk=tma_id).delete()
    return http.HttpResponse()

@login_required
def ajax_load_ticketmailtrace(request, ticket_id):
    """ Renvoie les ticketmailtrace pour le ticket ticket_id """
    if not ticket_id:
        raise PermissionDenied

    try:
        ticket = Ticket.minimal.all().\
            filter_ticket_by_user(request.user, no_client=True).get(pk=ticket_id)
    except Ticket.DoesNotExist:
        raise PermissionDenied

    ticketmailtrace = TicketMailTrace.objects.filter(ticket=ticket)

    return render_to_response("ticket/ticketmailtrace.html",
            {"ticketmailtrace": ticketmailtrace},
            context_instance=RequestContext(request))

@login_required
def ajax_set_alarm(request, ticket_id):
    """ Met (ou enlève) une alarme sur le ticket """
    if not ticket_id:
        raise PermissionDenied

    try:
        ticket = Ticket.minimal.all().\
            filter_ticket_by_user(request.user, no_client=True).get(pk=ticket_id)
    except Ticket.DoesNotExist:
        raise PermissionDenied

    try:
        reason = request.POST.keys()[0]
    except IndexError:
        reason = ''

    alarm = ticket.get_current_alarm()

    if reason:
        if not alarm:  # Nouvelle alarme
            alarm = TicketAlarm(reason=reason,
                    user_open = request.user,
                    ticket = ticket)
        else: # Changement de raison (on change l'user aussi)
            alarm.reason = reason
            alarm.user_open = request.user

        alarm.save()
        ret = alarm.title_string()
    else: # not reason
        if alarm: # Fermeture
            alarm.user_close = request.user
            alarm.date_close = datetime.datetime.now()
            alarm.save()
        ret = "Nouvelle Alarme"

    return http.HttpResponse(ret)

@login_required
@json_response
def ajax_load_telephone(request):
    """
    Renvoie un json contenant les numéros uniques de téléphone/dernier numéro de téléphone du client/enfants
    """
    
    ret = {}
    
    client_id = request.POST.get("client_id", None)
    if not client_id:
        raise PermissionDenied
    
    client = get_object_or_404(Client, pk=client_id)
    if not user_has_perms_on_client(request.user, client):
        raise PermissionDenied
    
    # Récupère la liste des numéros
    telephones = {}

    if settings.POSTGRESQL_VERSION >= 8.4:
        client_and_childs = Client.objects.get_childs("parent", client.pk)
    else:
        client_and_childs = [ client, ]
    
    for client in client_and_childs:
        coord = client.coordinates
        if coord and coord.telephone and not coord.telephone in telephones:
            coord_supp = ''
            if coord.postalcode or coord.city:
                coord_supp += ' (Client '
                if coord.postalcode:
                    coord_supp += str(coord.postalcode)
                if coord.city:
                    coord_supp += ' ' + str(coord.city)
                coord_supp += ')'
            telephones[coord.telephone] = (("", str(coord.telephone), "%s%s" % (coord.telephone, coord_supp)))

    # Récupère la liste des derniers tickets
    tickets = Ticket.tickets.filter(parent__isnull=True).filter(client__in=client_and_childs)
    tickets = tickets.exclude(telephone__isnull=True).exclude(telephone='')
    tickets = tickets.filter_ticket_by_user(request.user).order_by("-id")[:5]
    # TODO il faudrait faire un queryset avec des telephones uniques et après faire le [:5]

    for ticket in tickets:
        if not ticket.telephone in telephones:
            telephones[ticket.telephone] = ((ticket.contact, ticket.telephone, "%s %s (Ticket %s de %s)" % (ticket.contact, ticket.telephone, ticket.id, ticket.client)))

    ret["telephones"] = telephones.values()
    return ret

@login_required
@json_response
def ajax_graph_permonth(request):
    """
    
    """
    ret = {}
    
    today = datetime.datetime.now()
    qs = Ticket.objects.all().filter_ticket_by_user(request.user)
    if not qs:
        return ret
    
    ret["charts"] = []
    
    def get_chart(tss, series_properties):
        chart = {}
        chart["y_values"] = [ t[1] for t in tss ]
        chart["x_labels"] = [
            {'value': idx+1, 'text': t[0].strftime("%b")} \
            for idx, t in enumerate(tss)
        ]
        chart["series_properties"] = series_properties
        return chart
    
    ## Opened ticket chart
    qss = qsstats.QuerySetStats(qs, 'date_open')
    tss = qss.time_series(today-datetime.timedelta(days=360), today, interval='months')
    ret["charts"].append(get_chart(tss, series_properties = {'legend': 'Tickets ouverts'}))
    
    ## Critical tickets chart
    chart = {}
    qs = qs.filter(priority__gt=3)
    if not qs:
        return {}
    qss = qsstats.QuerySetStats(qs, 'date_open')
    tss = qss.time_series(today-datetime.timedelta(days=360), today, interval='months')
    ret["charts"].append(get_chart(tss, series_properties = {'legend': 'Tickets critiques', 'stroke': 'red'}))

    return ret

@login_required
@json_response
def ajax_graph_average_close_time(request):
    """
    
    Returns data for generating "average close time" graph
    """
    ret = {}
    
    if not request.user.is_staff:
        client_list = request.user.get_profile().get_clients()
        filterquery = """AND ticket_ticket.client_id IN (%s)""" % (",".join(map(str, [ c.id for c in client_list ])),)
    else:
        filterquery = ""
    
    rawquery = """SELECT 
        extract('epoch' from AVG((date_close - date_open)::interval)) AS delay, 
        date_trunc('month', date_open) AS date,
        priority_id
    FROM 
        ticket_ticket 
    WHERE
        state_id = 4
    AND
        date_open > (now() - interval '1 year')
    AND
        ticket_ticket.id NOT IN (SELECT id FROM ticket_ticket WHERE (date_close-date_open) > interval '40 days')
    %s
    GROUP BY 
        date, priority_id
    HAVING
        AVG((date_close - date_open)::interval) > interval '0'
    ORDER BY
        priority_id, date;""" % (filterquery,)
    
    today = datetime.datetime.now()
    current_month = today.month
    mapping = [ ((i+current_month) % 12)+1 for i in range(0,12) ]
    text_mapping = ("Jan", "Fev", "Mar", "Avr", "Mai", "Jun", "Jul", "Aou", "Sep", "Oct", "Nov", "Dec")
    
    def get_chart(serie, properties):
        chart = {}
        chart["values"] = [ {'x': mapping.index(s[1].month), 'y': s[0]/3600} for s in serie ] # En heures
        chart["properties"] = properties
        return chart
    
    cursor = connection.cursor()
    cursor.execute(rawquery)
    data = cursor.fetchall()
    #data = [(850743.80952400004, datetime.datetime(2009, 7, 1, 0, 0), 1), (5205087.4000000004, datetime.datetime(2009, 8, 1, 0, 0), 1), (28206.0, datetime.datetime(2009, 9, 1, 0, 0), 1), (143188.5, datetime.datetime(2009, 11, 1, 0, 0), 1), (127069.333333, datetime.datetime(2009, 12, 1, 0, 0), 1), (162324.0, datetime.datetime(2010, 1, 1, 0, 0), 1), (1894222.096102, datetime.datetime(2010, 3, 1, 0, 0), 1), (522988.93457899999, datetime.datetime(2009, 7, 1, 0, 0), 2), (547603.640288, datetime.datetime(2009, 8, 1, 0, 0), 2), (368607.906716, datetime.datetime(2009, 9, 1, 0, 0), 2), (561494.17058799998, datetime.datetime(2009, 10, 1, 0, 0), 2), (623945.57837700006, datetime.datetime(2009, 11, 1, 0, 0), 2), (647219.15001900005, datetime.datetime(2009, 12, 1, 0, 0), 2), (399448.89853300003, datetime.datetime(2010, 1, 1, 0, 0), 2), (507396.04899099999, datetime.datetime(2010, 2, 1, 0, 0), 2), (204780.30123700001, datetime.datetime(2010, 3, 1, 0, 0), 2), (222393.817759, datetime.datetime(2010, 4, 1, 0, 0), 2), (1595656.538462, datetime.datetime(2009, 7, 1, 0, 0), 3), (600649.68421099999, datetime.datetime(2009, 8, 1, 0, 0), 3), (287347.47619000002, datetime.datetime(2009, 9, 1, 0, 0), 3), (746089.95833299996, datetime.datetime(2009, 10, 1, 0, 0), 3), (614552.60089300002, datetime.datetime(2009, 11, 1, 0, 0), 3), (289317.22395800002, datetime.datetime(2009, 12, 1, 0, 0), 3), (367416.75990300003, datetime.datetime(2010, 1, 1, 0, 0), 3), (148866.46093199999, datetime.datetime(2010, 2, 1, 0, 0), 3), (181966.69768000001, datetime.datetime(2010, 3, 1, 0, 0), 3), (72059.588652999999, datetime.datetime(2010, 4, 1, 0, 0), 3), (1288154.0, datetime.datetime(2009, 7, 1, 0, 0), 4), (10974.5, datetime.datetime(2009, 9, 1, 0, 0), 4), (479802.11111100001, datetime.datetime(2009, 10, 1, 0, 0), 4), (357279.33333300002, datetime.datetime(2009, 11, 1, 0, 0), 4), (1157326.5, datetime.datetime(2009, 12, 1, 0, 0), 4), (482023.45454499999, datetime.datetime(2010, 1, 1, 0, 0), 4), (26748.099999999999, datetime.datetime(2010, 2, 1, 0, 0), 4), (890311.0, datetime.datetime(2010, 3, 1, 0, 0), 4), (220048.82686900001, datetime.datetime(2010, 4, 1, 0, 0), 4)]
    transaction.commit_unless_managed()
    if not data:
        return ret
    
    serie = []
    series = []
    old_priority = data[0][2]
    for d in data:
        if d[2] != old_priority:
            if serie:
                series.append(serie)
            old_priority = d[2]
            serie = []
        serie.append(d)
    
    if serie:
        series.append(serie)
    ret["series"] = [ get_chart(serie, 
        properties = {
            "legend": u"Priorité %s" % (serie[0][2],),
#            "color": Priority.objects.get(pk=int(serie[0][2])).forecolor,
#            "stroke": Priority.objects.get(pk=int(serie[0][2])).forecolor
        }) for serie in series ]
    
    ret["x_labels"] = [ {'value': idx+1, 'text': text_mapping[month-1]} for idx, month in enumerate(mapping) ]
    
    return ret


def get_critical_tickets(request):
    qs = Ticket.open_tickets.select_related().only('id', 'title').\
            filter_ticket_by_user(request.user).\
            filter(priority__gt=3).\
            order_by('-date_open')
    return qs[:settings.SUMMARY_TICKETS]

def get_ticket_text_statistics(request):
    statList = []
    statList.append(u"Tickets sans client: %s" % (Ticket.objects.filter(client__isnull = True).count()),)
    qs = Ticket.minimal.only('id', 'date_open').\
            filter_ticket_by_user(request.user)
    if qs:
        qss = qsstats.QuerySetStats(qs, 'date_open')
        statList.append(u"Ouverts aujourd'hui: %s" % (qss.this_day(),))
        statList.append(u"Ouverts ce mois: %s" % (qss.this_month(),))
        statList.append(u"Ouverts en %s: %s" % (datetime.date.today().year, qss.this_year(),))
    return statList

def get_ticket_alarm(request):
    alarms = TicketAlarm.opened.select_related().only('id')
    qs = Ticket.minimal.filter(ticketalarm__in=alarms).\
            filter_ticket_by_user(request.user)
    return qs[:settings.SUMMARY_TICKETS]


