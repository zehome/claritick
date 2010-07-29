# -*- coding: utf8 -*-

from django.db import models
from dojango import forms as df

from ticket.models import Ticket
from developpements.models import Developpement

class DeveloppementForm(df.ModelForm):
    class Meta:
        model = Developpement
        exclude = ("lien",)

    nom = df.CharField()
    couleur = df.CharField()

    def __init__(self, *a, **kw):
        instance = kw.get("instance", None)

        if instance and instance.pk:
            tickets = Ticket.minimal.\
                    filter(client__in=instance.client_demandeur.\
                    filter(client__isnull=False))
        else:
            tickets = Ticket.minimal.none()

        self.base_fields["ticket"].queryset = tickets

        return super(DeveloppementForm, self).__init__(*a, **kw)
