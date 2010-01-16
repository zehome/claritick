# -*- coding: utf-8 -*-

import django_tables as tables
from claritick.clariadmin.models import Host

class DefaultHostTable(tables.ModelTable):
    id = tables.Column('Id', visible=False)
    hostname = tables.Column('Hostname')
    site = tables.Column('Site')
    ip = tables.Column('IP(s)')
    os = tables.Column('OS')
    automate = tables.Column('Automate(s)')
    type = tables.Column('Type')

    class Meta:
        sortable = True
