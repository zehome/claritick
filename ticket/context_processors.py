from claritick.ticket.models import TicketView

def ticket_views(request):
    return {
        "ticket_views": TicketView.objects.filter(user=request.user)
    }
