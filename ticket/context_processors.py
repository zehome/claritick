from claritick.ticket.models import TicketUserFilter

def ticket_views(request):
    return {
        "ticket_views": TicketUserFilter.objects.filter(user=request.user)
    }
