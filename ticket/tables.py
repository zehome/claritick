# -*- coding: utf-8 -*-

import django_tables as tables
from claritick.ticket.models import *
from dojango import forms as df

class AssignToForm(df.ModelForm):
    class Meta:
        model = Ticket
        fields = ("client", "category", "project", "title", "contact", "assigned_to")

class DefaultTicketTable(tables.ModelTable):  
    id = tables.Column(verbose_name="N°")  
    client = tables.Column(verbose_name="Client")
    category = tables.Column(verbose_name="Cat.")
    project = tables.Column(verbose_name="Projet")
    title = tables.Column(verbose_name="Titre")
    comments = tables.Column(verbose_name="Rep.")
    contact = tables.Column(verbose_name='Contact')
    last_modification = tables.Column(verbose_name='MAJ')
    opened_by = tables.Column(verbose_name='Par')
    assigned_to = tables.Column(verbose_name='Pour')
    close_style = tables.Column(visible=False)
    priority_text_style = tables.Column(visible=False)
    priority_back_style = tables.Column(visible=False)
    
    class Meta:
        sortable = True
