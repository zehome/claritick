from ticket.models import TicketView, Ticket
from ticket.views import filter_ticket_by_user
import qsstats
import datetime

SUMMARY_TICKETS=15

def get_critical_tickets(request):
    qs = Ticket.open_tickets.all()
    qs = filter_ticket_by_user(qs, request.user).filter(priority__gt=3).order_by('-date_open')
    return qs[:SUMMARY_TICKETS]

def get_ticket_text_statistics(request):
    statList = []
    #statList.append(u"Tickets sans client: %s" % (Ticket.objects.filter(client__isnull = True).count()),)
    #qs = Ticket.objects.all()
    #qs = filter_ticket_by_user(qs, request.user)
    #if qs:
    #    qss = qsstats.QuerySetStats(qs, 'date_open')
    #    #tss = qss.time_series(days_ago, today)
    #    statList.append(u"Ouverts aujourd'hui: %s" % (qss.this_day(),))
    #    statList.append(u"Ouverts ce mois: %s" % (qss.this_month(),))
    #    statList.append(u"Ouverts en %s: %s" % (datetime.date.today().year, qss.this_year(),))
    

    return statList

def ticket_views(request):
    if request.user and not request.user.is_anonymous():
        return {
        "ticket_views": TicketView.objects.filter(user=request.user),
        "ticket_dashboard_critical": get_critical_tickets(request),
        "ticket_dashboard_text_statistics": get_ticket_text_statistics(request),
        }
    return {}
