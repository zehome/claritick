# -*- coding: utf8 -*-

from django.db import models
from dojango import forms as df

from ticket.models import Ticket
from developpements.models import Developpement, GroupeDev

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
            self.base_fields["groupe"].queryset = GroupeDev.objects.\
                    filter(project=instance.groupe.project)
        else:
            tickets = Ticket.minimal.none()
            self.base_fields["groupe"].choices = \
                [(g.pk, u"%s - %s" % (g.project, g,)) for g in GroupeDev.objects.all()]

        self.base_fields["ticket"].queryset = tickets

        return super(DeveloppementForm, self).__init__(*a, **kw)
