# -*- coding: utf-8 -*-

from djangogcal.adapter import CalendarAdapter, CalendarEventData
from djangogcal.observer import CalendarObserver

from claritick.ticket.models import Ticket
from django.contrib.auth.models import User

class TicketCalendarAdapter(CalendarAdapter):
    """
    A calendar adapter for the Showing model.
    """
    
    def get_event_data(self, instance):
        """
        Returns a CalendarEventData object filled with data from the adaptee.
        """
        return CalendarEventData(
            start=instance.start_time,
            end=instance.end_time,
            title=instance.title
        )


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
            continue
        
        print "Registering google Calendar Observer for %s" % (user,)
        
        observer = CalendarObserver(email=profile.google_account.login,
                                password=profile.google_account.password)
        observer.observe(Ticket, TicketCalendarAdapter())

register_all_users()