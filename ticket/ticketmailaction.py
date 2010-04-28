# -*- coding: utf-8 -*-

"""

Send really emails based on TicketMailAction
"""

from ticket.models import Ticket, TicketMailAction
from django.conf import settings
from django.db.models import Max
import datetime

def send_emails():
    email_delay = getattr(settings, "TICKET_EMAIL_DELAY", 120)
    # Defaults to 120 seconds delay before sending tickets
    now = datetime.datetime.now()
    ticket_tmas = TicketMailAction.objects.filter(date__lte=now-datetime.timedelta(seconds=email_delay)).values('ticket').annotate(datemax=Max('date'))
    for ticket_tma in ticket_tmas:
        ticket_id = ticket_tma["ticket"]
        try:
            ticket = Ticket.objects.get(pk=ticket_id)
        except Ticket.DoesNotExist:
            # Delete all tmas
            TicketMailAction.filter(ticket__pk=ticket_id).delete()
            continue
        
        reasons = []
        tmas = TicketMailAction.objects.filter(ticket__pk=ticket_id).order_by('date') # Ordre ascendant
        for tma in tmas:
            reasons.extend(tma.reasons)

        reasons_unique = list(set(reasons)) # Suppression des doublons
        ticket.send_email(reasons_unique)
        tmas.delete()
