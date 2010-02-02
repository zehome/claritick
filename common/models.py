# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from django.db import models
from claritick.common.widgets import ColorPickerWidget

class TelephoneField(models.CharField):
    def __init__(self, *args, **kw):
        kw["max_length"] = 10
        kw["blank"] = True
        kw["null"] = True
        super(TelephoneField, self).__init__(*args,**kw)

class Coordinate(models.Model):
    class Meta:
        verbose_name = u"Coordonnées"
        ordering = ["destinataire", "address_line1"]
    
    telephone = TelephoneField(u"Téléphone fixe")
    gsm = TelephoneField(u"Téléphone portable")
    fax = TelephoneField(u"Fax")
    destinataire = models.CharField(u"Destinataire", max_length=128, blank=True, null=True)
    address_line1 = models.CharField(u"Ligne1", max_length=128, blank=True, null=True)
    address_line2 = models.CharField(u"Ligne2", max_length=128, blank=True, null=True)
    address_line3 = models.CharField(u"Ligne3", max_length=128, blank=True, null=True)
    postalcode = models.CharField(u"Code postal", max_length=6, blank=True, null=True)
    city = models.CharField(u"Ville", max_length=64, blank=True, null=True)
    email = models.EmailField(u"Email", blank=True, null=True)
    more = models.TextField(u"Complément d'information", blank=True, null=True)
    
    def __unicode__(self):
        return u"%s%s%s%s" % (self.destinataire and self.destinataire+' ' or '', 
            self.address_line1 and self.address_line1+' ' or '', 
            self.postalcode and self.postalcode+' ' or '', 
            self.city and self.city+' ' or '')
 
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
    class Meta:
        verbose_name = "Client"
        ordering = ['parent__label', 'label']
        permissions = (
            ("can_access", "Accès CLARIADMIN"),
        )
    
    label = models.CharField("Nom", max_length=64) 
    parent = ClientField('Client', verbose_name='Parent', null=True, blank=True, limit_choices_to = {'parent__parent': None})
    coordinates = models.ForeignKey(Coordinate, verbose_name=u'Coordonnées', blank=True, null=True)
    emails = models.CharField("Emails séparés par des virgule", max_length=2048, blank=True, null=True)
    notifications_by_fax = models.BooleanField(u"Transmission des notifications par fax", default=False)
    
    def __unicode__(self):
        if self.parent:
            return u"%s - %s" % (self.label, self.parent)
        return u"%s" % (self.label,)
    
    def get_emails(self):
        """ Returns emails of this site plus email of the parent """
        if self.emails:
            emails = [ e.strip() for e in self.emails.split(",") ]
        else:
            emails = []
        if self.parent:
            emails.extend( self.parent.get_emails() )
        return emails
    
    def get_faxes(self):
        """ Returns list of fax numbers """
        if self.coordinates and self.coordinates.fax:
            faxes = [ self.coordinates.fax, ]
        else:
            faxes = []
        if self.parent:
            faxes.extend( self.parent.get_faxes() )
        return faxes

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
            ustr += u" (%s)" % (self.client,)
        return ustr