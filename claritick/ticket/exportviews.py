# -*- coding: utf-8 -*-

import csv
import codecs
import cStringIO
import datetime

from django.http import HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.db.models import Q

from django.contrib.auth.decorators import login_required

from ticket.views import get_context, get_filters, set_filters
from ticket.forms import SearchTicketForm, SearchTicketViewForm, SearchTicketViewFormInverted
from ticket.models import Ticket, TicketView

csv.register_dialect('claritick', delimiter=';', quoting=csv.QUOTE_ALL)

class UTF8Recoder(object):
    """
    Iterator that reads an encoded stream and reencodes the input to UTF-8
    See : http://docs.python.org/library/csv.html
    """
    def __init__(self, f, encoding):
        self.reader = codecs.getreader(encoding)(f)

    def __iter__(self):
        return self

    def next(self):
        return self.reader.next().encode("utf-8")

class UnicodeWriter(object):
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    See : http://docs.python.org/library/csv.html
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        self.writer.writerow([s.encode("utf-8") for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)

@login_required
def export_me(request, *args, **kw):
    form = None
    if not request.POST.get("assigned_to", None):
        form = SearchTicketForm({'assigned_to': request.user.id}, get_filters(request), user=request.user)
        set_filters(request, form.data)
    return export_all(request, form, filename=request.user.username, *args, **kw)

@login_required
def export_unassigned(request, *args, **kw):
    filterdict = {'assigned_to__isnull': True}
    return export_all(request, None, filterdict = filterdict, filename='unassigned', *args, **kw)

@login_required
def export_nonvalide(request):
    """
    liste des tickets ã  valider.
    """
    filterdict = {"validated_by__isnull": True}
    return export_all(request, filterdict=filterdict, filename='nonvalide')

@login_required
def export_notseen(request):
    """liste des tickets non consultes."""
    profile = request.user.my_userprofil
    ticket_vus = profile.tickets_vus or {}

    def postfiltercallback(qs):
        for k,v in ticket_vus.items():
            if k == "all":
                q = Q(last_modification__gt=datetime.datetime.fromtimestamp(int(v)))
                qs = qs.filter(q)
            else:
                q = Q(pk=int(k)) & Q(last_modification__lt=datetime.datetime.fromtimestamp(int(v)))
                qs = qs.exclude(q)
        return qs

    return export_all(request, postfiltercallback=postfiltercallback, filename='notseen')

def make_csv_response(queryset, filename):
    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=%s.csv' % (filename,)

    writer = UnicodeWriter(response, 'claritick')
    writer.writerow(['Id','Client', u'Catégorie', 'Projet', 'Titre', 'Contact', 'Ouvert par', u'Assigné à', 'Statut','Contenu'])
    for tick in queryset:
        writer.writerow([unicode(I) for I in [
            tick.pk,
            tick.client,
            tick.category,
            tick.project,
            tick.title,
            tick.contact,
            tick.opened_by,
            tick.assigned_to,
            tick.state,
            tick.text,
            ]])

    return response

@login_required
def export_all(request, form=None, filename='tickets',
    filterdict=None, postfiltercallback=None, *args, **kw):
    """
        Exporte tous les tickets sans aucun filtre
    """

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
            qs = qs.filter_or_child(Q(title__icontains=form.cleaned_data["text"]) | Q(text__icontains=form.cleaned_data["text"]), user=request.user)
            del data["text"]
        qs = qs.filter_queryset(data, user=request.user)

    # unassigned / nonvalide
    if filterdict:
        qs = qs.filter_or_child(filterdict, user=request.user)

    # On va filtrer la liste des tickets en fonction de la relation user => client
    qs = qs.filter_ticket_by_user(request.user)

    if postfiltercallback:
        qs = postfiltercallback(qs)

    # Le tri
    qs = qs.add_order_by(request)
    return make_csv_response(qs, filename)

@login_required
def export_view(request, view_id=None):
    context = get_context(request)

    # On charge la vue de la liste
    inverted_filters = {}
    filters = {}
    if view_id:
        profile = request.user.my_userprofile
        ticket_vus = profile.tickets_vus or {}

        view = get_object_or_404(TicketView, pk=view_id, user=request.user)
        data = view.filters
        inverted_filters = view.inverted_filters
        data.update({"view_name": view.name})
        filters = data.copy()
        context["view"] = view

    # le form de filtres
    form = SearchTicketViewForm(data, user=request.user)    
    form_inverted = SearchTicketViewFormInverted(inverted_filters, user=request.user)

    if not data.get("state"):
        qs = Ticket.open_tickets.filter(parent__isnull=True)
    else:
        qs = Ticket.tickets.filter(parent__isnull=True)

    # On filtre la liste a partir des datas de la vue
    if not request.user.has_perm("ticket.can_list_all") and data.get("text"):
        qs = qs.filter_or_child(models.Q(title__icontains=data["title"]) | models.Q(text__icontains=data["text"]), user=request.user)
        del filters["text"]
    qs = qs.filter_queryset(filters, user=request.user, inverted_filters=inverted_filters)

    # On va filtrer la liste des tickets en fonction de la relation user => client
    qs = qs.filter_ticket_by_user(request.user)

    if context.get("view", False) and view.notseen: 
        for k,v in ticket_vus.items():
            if k == "all":
                q = models.Q(last_modification__gt=datetime.datetime.fromtimestamp(int(v)))
                qs = qs.filter(q)
            else:
                q = models.Q(pk=int(k)) & models.Q(last_modification__lt=datetime.datetime.fromtimestamp(int(v)))
                qs = qs.exclude(q)

    # Le tri
    qs = qs.add_order_by(request)
    filename = view.name
    return make_csv_response(qs, filename)
