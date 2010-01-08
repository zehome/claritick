# -*- coding: utf-8 -*-

import django_tables as tables
from claritick.ticket.models import *

class DefaultTicketTable(tables.ModelTable):  
    id = tables.Column(sortable=False, visible=False)  
    
    class Meta:  
        model = Ticket
        exclude = ( 'validated_by', 'telephone', 'opened_by', 'text', 'keywords', 
                    'calendar_start_time', 'calendar_end_time', 'calendar_title' )
