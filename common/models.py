# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from django.db import models
from claritick.common.widgets import ColorPickerWidget

# Utilities
class ColorField(models.CharField):
    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 10
        super(ColorField, self).__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        kwargs['widget'] = ColorPickerWidget
        return super(ColorField, self).formfield(**kwargs)


# Models
class Groupement(models.Model):
    label = models.CharField("Nom", help_text="Nom du groupement", max_length=64)
    
    def __unicode__(self):
        return "%s" % (self.label,)
    
class Site(models.Model):
    label = models.CharField("Nom", help_text="Nom du site", max_length=64)
    groupement = models.ForeignKey(Groupement)
    
    def __unicode__(self):
        return "%s / %s" % (self.groupement, self.label)

class GoogleAccount(models.Model):
    login = models.EmailField("Login")
    password = models.CharField("Mot de passe", max_length=64)
    
    def __unicode__(self):
        return "Compte google pour %s" % (self.login,)
    

class UserProfile(models.Model):
    user = models.ForeignKey(User, verbose_name="Utilisateur", unique=True)
    google_account = models.ForeignKey(GoogleAccount, verbose_name="Compte google")
    
    def __unicode__(self):
        return "Profil utilisateur"