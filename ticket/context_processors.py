from ticket.models import TicketView, Ticket, TicketAlarm
import qsstats
import datetime
import settings

def get_active_alarms(request):
    return TicketAlarm.opened.all()

def ticket_views(request):
    if request.user and not request.user.is_anonymous():
        return {
        "ticket_views": TicketView.objects.filter(user=request.user),
        "settings": {
            "TICKET_STATE_CLOSED": settings.TICKET_STATE_CLOSED,
            "TICKET_STATE_NEW": settings.TICKET_STATE_NEW,
            "TICKET_STATE_ACTIVE": settings.TICKET_STATE_ACTIVE,
            },
        "ticket_alarms": get_active_alarms(request),
        }
    return {}

