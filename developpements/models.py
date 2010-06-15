from django.db import models

# Create your models here.

class Client(models.Model):
    nom = models.TextField()
    
    def __unicode__(self):
        return self.nom

class Version(models.Model):
    majeur = models.IntegerField()
    mineur = models.IntegerField()
    date_sortie = models.DateField(null = True, blank = True)
    contenu = models.ManyToManyField('Developpement')
    
    def __unicode__(self):
        return "%i.%i" % (self.majeur, self.mineur,)

class GroupeDev(models.Model):
    nom = models.TextField()
    description = models.TextField(null = True, blank = True)
    lien = models.TextField(null = True, blank = True)
    poids = models.IntegerField(default = 1)
    version_requise = models.ForeignKey(Version, null = True, blank = True)
    
    def __unicode__(self):
        return self.nom

class Developpement(models.Model):
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

    def calcul_poids(self):
        n_clients = max(1, self.client_demandeur.count())
        poids = n_clients * self.groupe.poids * self.poids
        if self.bug:
            poids += 100000
        poids += self.poids_manuel * 1000000
        return poids

    def __unicode__(self):
        return self.nom