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
    