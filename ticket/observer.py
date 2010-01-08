# -*- coding: utf-8 -*-

try:
  from xml.etree import ElementTree
except ImportError:
  from elementtree import ElementTree
import gdata.calendar.service
import gdata.service
import atom.service
import gdata.calendar
import atom

import claritick.settings

from djangogcal.adapter import CalendarAdapter, CalendarEventData
from djangogcal.observer import CalendarObserver


class TicketCalendarObserver(CalendarObserver):
    _calendars = []


    def _InsertCalendar(self, title, description=None,
          time_zone='Europe/Paris', hidden=False, location='',
          color=''):
        """Creates a new calendar using the specified data."""
        
        if not description:
            description = title
        
        calendar = gdata.calendar.CalendarListEntry()
        calendar.title = atom.Title(text=title)
        
        if description:
            calendar.summary = atom.Summary(text=description)
        
        if location:
            calendar.where = gdata.calendar.Where(value_string=location)
        if color:
            calendar.color = gdata.calendar.Color(value=color)
        
        calendar.timezone = gdata.calendar.Timezone(value=time_zone)

        if hidden:
            calendar.hidden = gdata.calendar.Hidden(value='true')
        else:
            calendar.hidden = gdata.calendar.Hidden(value='false')
        
        service = self.get_service()
        new_calendar = service.InsertCalendar(new_calendar=calendar)
        return new_calendar
    
    def _get_feeds_uri(self, instance):
        calendar_titles = [ instance.category.label, ]
        if instance.project:
            calendar_titles.append(instance.project.label)
        
        service = self.get_service()
        feed = service.GetOwnCalendarsFeed()
        
        calendars = [ (a_calendar.GetEditLink().href.split("/")[-1], a_calendar.title.text) for a_calendar in feed.entry ]
        
        print "Available calendars: %s" % (calendars,)
        for cal_title in calendar_titles:
            if cal_title not in [ c[1] for c in calendars ]:
                new_cal = self._InsertCalendar(title = cal_title)
        feed = service.GetOwnCalendarsFeed()
        calendars = [ (a_calendar.GetEditLink().href.split("/")[-1], a_calendar.title.text) for a_calendar in feed.entry ]
        
        print "After add available: %s" % (calendars,)
        
        # LC: TODO REMOVE THIS SHIT
        return calendars
    
    def update(self, sender, instance):
        """
        
        Overridden method from GCAL to handle multiple feeds
        """
        
        adapter = self.adapters[sender]
        if adapter.can_save(instance):
            service = self.get_service()
            event = self.get_event(service, instance) or CalendarEventEntry()
            adapter.get_event_data(instance).populate_event(event)
            if adapter.can_notify(instance):
                event.send_event_notifications = SendEventNotifications(
                    value='true')
            
            self._get_feeds_uri(instance)
            
            if event.GetEditLink():
                service.UpdateEvent(event.GetEditLink().href, event)
            else:
                new_event = service.InsertEvent(event, self.feed)
                CalendarEvent.objects.set_event_id(instance, self.feed,
                                                   new_event.id.text)
    