# -*- coding: utf-8 -*-

from djangogcal.adapter import CalendarAdapter, CalendarEventData
#from djangogcal.observer import CalendarObserver
from claritick.ticket.observer import TicketCalendarObserver
from claritick.ticket.models import Ticket
from django.contrib.auth.models import User

class TicketCalendarAdapter(CalendarAdapter):
    """
    A calendar adapter for the Showing model.
    """
    
    def can_save(self, ticket):
        return bool(ticket.calendar_start_time and ticket.calendar_end_time)
    
    def get_event_data(self, ticket):
        """
        Returns a CalendarEventData object filled with data from the adaptee.
        """
        if ticket.calendar_title:
            title = ticket.calendar_title
        else:
            title = ticket.title
        
        content = ticket.text

        return CalendarEventData(
            start=ticket.calendar_start_time,
            end=ticket.calendar_end_time,
            title=ticket.title,
            content = content
        )

observers = []

def register_all_users():
    # Register all users
    users = User.objects.all()
    for user in users:
        try:
            profile = user.get_profile()
        except:
            print "Utilisateur %s sans profil." % (user,)
            continue
        
        if not profile.google_account:
            print "%s no google account." % (profile,)
            continue
        
        print "Registering google Calendar Observer for %s" % (user,)
        
        observer = TicketCalendarObserver(email=profile.google_account.login,
                                    password=profile.google_account.password)
        observer.observe(Ticket, TicketCalendarAdapter())
        observers.append(observer)

try:
    register_all_users()
except:
    print "Unable to register google calendars."
