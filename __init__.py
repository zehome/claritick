# -*- coding: utf-8 -*-

from djangogcal.adapter import CalendarAdapter, CalendarEventData
from djangogcal.observer import CalendarObserver
from ticket.models import Ticket
from common.models import UserProfile, GoogleAccount, ClaritickUser
from django.contrib.auth.models import User
from django.db.models import signals

observers = {}

class TicketCalendarAdapter(CalendarAdapter):
    """
    A calendar adapter for the Showing model.
    """
    
    def can_save(self, ticket, observer):
        if not ticket.assigned_to:
            return False
        if ticket.assigned_to != observer.user:
            return False
        return bool(ticket.calendar_start_time and ticket.calendar_end_time)
    
    def can_delete(self, ticket, observer):
        """ To implement """
        return super(TicketCalendarAdapter, self).can_delete(ticket)
    
    def get_event_data(self, ticket):
        """
        Returns a CalendarEventData object filled with data from the adaptee.
        """
        if ticket.calendar_title:
            title = "[%s] %s" % (ticket.id, ticket.calendar_title)
        else:
            title = "[%s] %s" % (ticket.id, ticket.title)
        content = "[%s] %s" % (ticket.id, ticket.text)

        return CalendarEventData(
            start=ticket.calendar_start_time,
            end=ticket.calendar_end_time,
            title=ticket.title,
            content = content
        )

def register_all_users():
    """ Register an observer for each user """
    global observers
    users = User.objects.all()
    for user in users:
        if observers.get(user, None) is not None:
            continue
        set_observer(user)


def get_observer(user):
    """
    Try to return a googleCalendar observer related to the User
    """
    global observers
    try:
        return observers[user]
    except KeyError:
        return None

def del_observer(user):
    global observers
    try:
        del observers[user]
    except KeyError:
        pass

def set_observer(user):
    """ Sets an observer attached to this user """
    try:
        profile = user.get_profile()
    except:
        return
    
    if not profile.google_account:
        return
    
    observer = CalendarObserver(email=profile.google_account.login,
                                password=profile.google_account.password,
                                user=user)
    observer.observe(Ticket, TicketCalendarAdapter())
    observers[user] = observer

def handle_update_user_signal(sender, **kw):
    user = kw["instance"]
    created = kw["created"]
    if created:
        set_observer(user)

def handle_del_user_signal(sender, **kw):
    user = kw["instance"]
    del_observer(instance)

def handle_update_profile_signal(sender, **kw):
    userprofile = kw["instance"]
    created = kw.get("created", False)
    if not userprofile.user:
        return
    if not created and userprofile.user and userprofile.google_account:
        del_observer(userprofile.user)
    set_observer(userprofile.user)

def handle_update_googleaccount_signal(sender, **kw):
    googleaccount = kw["instance"]
    global observers
    good_user=None
    for user, observer in observers.items():
        if googleaccount.login == observer.email:
            good_user = user
    if not good_user:
        return
    del_observer(user)
    set_observer(user)

def handle_claritickuser_add_signal(sender, **kwargs):
    """
        Lorsqu'un ClaritickUser est ajouté.
    """
    if kwargs["created"]:
        kwargs["instance"].userprofile_set.create()

try:
    # User and profile modifications
    signals.post_save.connect(handle_update_user_signal, sender=User)
    signals.pre_delete.connect(handle_del_user_signal, sender=User)
    signals.post_save.connect(handle_claritickuser_add_signal, sender=ClaritickUser)
    signals.post_save.connect(handle_update_profile_signal, sender=UserProfile)
    signals.pre_delete.connect(handle_update_profile_signal, sender=UserProfile)
    signals.post_save.connect(handle_update_googleaccount_signal, sender=GoogleAccount)
    signals.pre_delete.connect(handle_update_googleaccount_signal, sender=GoogleAccount)
    register_all_users()
except:
    print "Unable to register google calendars."
