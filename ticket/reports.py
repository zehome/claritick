# -*- coding: utf-8 -*-

import reporting
from django.db.models import Sum, Avg, Count
from claritick.ticket.models import Ticket

class TicketReport(reporting.Report):
    model = Ticket
    verbose_name = 'Ticket report'
    annotate = (                    # Annotation fields (tupples of field, func, title)
        ('id', Count, 'Total'),     # example of custom title for column 
    )
    aggregate = (                   # columns that will be aggregated (syntax the same as for annotate)
        ('id', Count, 'Total'),
    )
    group_by = [                   # list of fields and lookups for group-by options
        'state',
        'priority',
        'client',
        'client__parent',
    ]
    list_filter = [                # This are report filter options (similar to django-admin)
        'state',
        'priority',
        'category',
    ]
    
    detail_list_display = [        # if detail_list_display is defined user will be able to see how rows was grouped  
        'client', 
        'state',
    ]

    date_hierarchy = 'date_open' # the same as django-admin


reporting.register('ticket', TicketReport) # Do not forget to 'register' your class in reports
