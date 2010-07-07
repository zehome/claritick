from ticket.models import TicketView, Ticket, TicketAlarm
import qsstats
import datetime
import settings

SUMMARY_TICKETS=15

def get_critical_tickets(request):
    qs = Ticket.open_tickets.all()
    qs = qs.filter_ticket_by_user(request.user).filter(priority__gt=3).order_by('-date_open')
    return qs[:SUMMARY_TICKETS]

def get_ticket_text_statistics(request):
    statList = []
    statList.append(u"Tickets sans client: %s" % (Ticket.objects.filter(client__isnull = True).count()),)
    qs = Ticket.objects.all()
    qs = qs.filter_ticket_by_user(request.user)
    if qs:
        qss = qsstats.QuerySetStats(qs, 'date_open')
        statList.append(u"Ouverts aujourd'hui: %s" % (qss.this_day(),))
        statList.append(u"Ouverts ce mois: %s" % (qss.this_month(),))
        statList.append(u"Ouverts en %s: %s" % (datetime.date.today().year, qss.this_year(),))
    
    return statList

def get_ticket_alarm(request):
    alarms = TicketAlarm.opened.all()
    qs = Ticket.objects.all().\
            filter_ticket_by_user(request.user).\
            filter(ticketalarm__in=alarms)[:SUMMARY_TICKETS]
    return qs

def ticket_views(request):
    if request.user and not request.user.is_anonymous():
        return {
        "ticket_views": TicketView.objects.filter(user=request.user),
        "settings": {
            "TICKET_STATE_CLOSED": settings.TICKET_STATE_CLOSED,
            "TICKET_STATE_NEW": settings.TICKET_STATE_NEW,
            "TICKET_STATE_ACTIVE": settings.TICKET_STATE_ACTIVE,
            },
        }
    return {}

