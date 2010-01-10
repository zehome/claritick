# -*- coding: utf-8 -*-

import django_tables as tables
from claritick.ticket.models import *

class DefaultTicketTable(tables.ModelTable):  
    id = tables.Column(verbose_name="N°")  
    client = tables.Column(verbose_name="Client")
    category = tables.Column(verbose_name="Cat.")
    project = tables.Column(verbose_name="Projet")
    title = tables.Column(verbose_name="Titre")
    contact = tables.Column(verbose_name='Contact')
    last_modification = tables.Column(verbose_name='MAJ')
    opened_by = tables.Column(verbose_name='Par')
    assigned_to = tables.Column(verbose_name='Pour')
    
    class Meta:
        sortable = True
