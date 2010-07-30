# -*- coding: utf8 -*-

from django.db import models
from dojango import forms as df

from ticket.models import Ticket
from common.models import Client as ClaritickClient
from developpements.models import Developpement, GroupeDev, Project, Version

class DeveloppementForm(df.ModelForm):
    class Meta:
        model = Developpement
        exclude = ("lien",)

    nom = df.CharField()
    couleur = df.CharField()

    def __init__(self, *a, **kw):
        instance = kw.get("instance", None)

        if instance and instance.pk:
            # On cherche les tickets des clients claritick
            clients_pk = []
            for c in instance.client_demandeur.filter(client__isnull=False):
                clients_pk.extend([x.pk for x in ClaritickClient.objects.\
                        get_childs("parent", c.client.pk)])

                tickets = Ticket.minimal.filter(client__in=clients_pk)

            self.base_fields["groupe"].queryset = GroupeDev.objects.\
                    filter(project=instance.groupe.project)
            self.base_fields["version_requise"].queryset = Version.objects.\
                    filter(project=instance.groupe.project)

        else:
            tickets = Ticket.minimal.none()

            self.base_fields["groupe"].choices = [("", "")]
            self.base_fields["version_requise"].choices = [("", "")]

            projet_field = df.ChoiceField(label="Projet", choices=[(x.pk, x) for x in Project.objects.all()],
                widget=df.widgets.Select(attrs={'onChange': 'get_project_content(this);'}))
            projet_field.choices.insert(0, ("",""))

            self.base_fields.insert(0, "projet", projet_field)

        self.base_fields["ticket"].choices = [(x.pk, x) for x in tickets[:5]]
        self.base_fields["ticket"].choices.insert(0, ("", ""))

        return super(DeveloppementForm, self).__init__(*a, **kw)
