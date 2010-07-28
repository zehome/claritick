# -*- coding: utf-8 -*-

import datetime

from django.db import models
from django.core.exceptions import ValidationError

from common.models import Client as ClaritickClient

FORCE_DEV = 55 # heures par semaine

def week_start_date(year, week):
    d = datetime.date(year, 1, 1)
    delta_days = d.isoweekday() - 1
    delta_weeks = week
    if year == d.isocalendar()[0]:
        delta_weeks -= 1
    delta = datetime.timedelta(days = -delta_days, weeks = delta_weeks)
    return (d + delta)

class ClientManager(models.Manager):
    def get_query_set(self):
        return super(ClientManager, self).get_query_set().\
                select_related("client")

class Client(models.Model):
    nom = models.TextField(null=True, blank=True)
    client = models.ForeignKey(ClaritickClient, null=True, blank=True, related_name="dev_client")

    def save(self, *a, **kw):
        if (not self.client and not self.nom) or \
            (self.client and self.nom):
                raise ValidationError("Un seul des deux champs, name ou client doit être renseigné")

        ret = super(Client, self).save(*a, **kw)

        for d in self.developpement_set.all():
            d.save()
        return ret

    def __unicode__(self):
        return self.nom or unicode(self.client)

class Version(models.Model):
    class Meta:
        ordering = ["date_sortie"]
        permissions = (
            ("can_view_versions", u"Voir versions"),
        )

    majeur = models.IntegerField()
    mineur = models.IntegerField()
    revision = models.IntegerField()
    date_sortie = models.DateField(null = True, blank = True)
    contenu = models.ManyToManyField('Developpement')

    def __cmp__(self, other):
        count0 = int("%i%i%i", (self.majeur, self.mineur, self.revision,))
        count1 = int("%i%i%i", (other.majeur, other.mineur, other.revision,))
        return count0 - count1

    def __unicode__(self):
        ret = "%i.%i" % (self.majeur, self.mineur,)
        if self.revision:
            ret = "%s.%i" % (ret, self.revision,)
        return ret

class GroupeDev(models.Model):
    nom = models.TextField()
    description = models.TextField(null = True, blank = True)
    lien = models.TextField(null = True, blank = True)
    poids = models.IntegerField(default = 1)
    version_requise = models.ForeignKey(Version, null = True, blank = True)

    def save(self, *a, **kw):
        ret = super(GroupeDev, self).save(*a, **kw)
        for d in self.developpement_set.all():
            d.save()
        return ret

    def __unicode__(self):
        return self.nom

class DeveloppementManager(models.Manager):

    def get_query_set(self, *a, **kw):
        return super(DeveloppementManager, self).\
                get_query_set(*a, **kw).\
                select_related("groupe", "version_requise")

    def populate(self):

        ret = []
        devs = super(DeveloppementManager, self).all()

        now = datetime.datetime.now()
        semaine_en_cours = now.isocalendar()[1]+1
        heures_dev = 0
        couleurs = []

        for d in devs:

            if d.couleur and not d.couleur in couleurs:
                couleurs.append(d.couleur)

            if not hasattr(d, "date_sortie"):
                d.date_sortie = None

            if d.done or d.temps_prevu:
                if d.temps_prevu:
                    heures_dev += d.temps_prevu
                semaine = semaine_en_cours + (heures_dev / FORCE_DEV)
                d.date_sortie = week_start_date(now.year, int(semaine))

            gvr = d.groupe.version_requise
            dvr = d.version_requise
            if (gvr and dvr and gvr < dvr) or (not dvr):
                d.version_requise = gvr

            if not d.done:
                if d.date_sortie and d.engagement and d.date_sortie > d.engagement:
                    d.alerte = u"Date de sortie prévue dépasse la date d'engagement"
                if not d.date_sortie:
                    d.alerte = u"Pas de date sortie calculable pour ce dev"
                elif d.version_requise and d.version_requise.date_sortie and d.date_sortie > d.version_requise.date_sortie:
                    d.alerte = u"Date de sortie prévue dépasse la date de sortie de la version"

            ret.append(d)

        return (ret, couleurs)


class Developpement(models.Model):
    class Meta:
        permissions = (
            ("can_view_liste", u"Voir roadmap"),
            ("can_access_suividev", u"Accès suividev"),
        )
        ordering = ["-poids_total"]

    objects = DeveloppementManager()

    nom = models.TextField()
    description = models.TextField(null = True, blank = True)
    lien = models.TextField(null = True, blank = True)
    poids = models.IntegerField(default = 1)
    poids_manuel = models.FloatField(default = 0)
    version_requise = models.ForeignKey(Version, null = True, blank = True)
    groupe = models.ForeignKey(GroupeDev)
    bug = models.BooleanField()
    engagement = models.DateField(null = True, blank = True)
    temps_prevu = models.IntegerField(null = True, blank = True)
    client_demandeur = models.ManyToManyField(Client, null = True, blank = True)
    done = models.BooleanField()
    couleur = models.TextField(null = True, blank = True)
    poids_total = models.FloatField(default=0)

    @property
    def calcul_poids(self):
        if not hasattr(self, "clients"):
            self.clients = self.client_demandeur.all()
        n_clients = max(1, len(self.clients))
        poids = n_clients * self.groupe.poids * self.poids
        if self.bug:
            poids += 100000
        poids += self.poids_manuel * 1000000
        return poids

    def save(self, *a, **kw):
        super(Developpement, self).save(*a, **kw)
        self.poids_total = self.calcul_poids
        return super(Developpement, self).save(*a, **kw)

    def __unicode__(self):
        return self.nom

