# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from django.db import models
from claritick.common.widgets import ColorPickerWidget

class ColorField(models.CharField):
    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 10
        super(ColorField, self).__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        kwargs['widget'] = ColorPickerWidget
        return super(ColorField, self).formfield(**kwargs)

class ClientField(models.ForeignKey):
    def formfield(self, **kwargs):
        # This is a fairly standard way to set up some defaults
        # while letting the caller override them.
        #defaults = {'form_class': dojangoforms.Select}
        #defaults.update(kwargs)
        defaults=kwargs
        return super(ClientField, self).formfield(**defaults)

# Models
class Client(models.Model):
    label = models.CharField("Nom", max_length=64) 
    parent = ClientField('Client', verbose_name='Parent', null=True, blank=True, limit_choices_to = {'parent': None})
    
    def __unicode__(self):
        if self.parent:
            return u"%s - %s" % (self.parent, self.label)
        return u"%s" % (self.label,)

class GoogleAccount(models.Model):
    login = models.EmailField("Login")
    password = models.CharField("Mot de passe", max_length=64)
    
    def __unicode__(self):
        return u"Compte google %s" % (self.login,)
    

class UserProfile(models.Model):
    user = models.ForeignKey(User, verbose_name="Utilisateur", unique=True)
    google_account = models.ForeignKey(GoogleAccount, verbose_name="Compte google", null=True, blank=True)
    client = ClientField(Client, verbose_name="Client", blank=True, null=True)
    
    def __unicode__(self):
        ustr = u"Profil %s" % (self.user,)
        if self.client:
            ustr += " (%s)" (self.client,)
        return ustr