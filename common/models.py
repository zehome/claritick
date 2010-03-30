# -*- coding: utf-8 -*-

from django.contrib.auth.models import User, Group
from django.db import models
from django.utils import simplejson
from claritick.common.widgets import ColorPickerWidget

class JsonField(models.TextField):

    __metaclass__ = models.SubfieldBase

    def to_python(self, value):
        if isinstance(value, (str, unicode)) and value != "":
            return simplejson.loads(value)
        return value

    def get_prep_value(self, value):
        return simplejson.dumps(value)

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

class ClientManager(models.Manager):
    
    def get_query_set(self):
        qs = super(ClientManager, self).get_query_set().select_related("parent", "parent__parent", "coordinates")
        return qs

    def get_childs(self, field, object_pk):
        """
            Effectue un WITH RECURSIVE Postgres sur field à partir de l'objet object_pk.
        """
        from django.db import connection
        qn = connection.ops.quote_name

        # le nom de la table
        db_table = self.model._meta.db_table

        # le nom de la pk
        if self.model._meta.pk.db_column:
            pk = self.model._meta.pk.db_column
        else:
            pk = self.model._meta.pk.column

        # le nom du champs faisant la relation parent <-> enfant
        model_field = getattr(self.model, field).field
        if model_field.db_column:
            db_field = model_field.db_column
        else:
            db_field = model_field.column
        
        query = """
            WITH RECURSIVE deep(n) AS (
                SELECT %(db_table)s.%(pk)s FROM %(db_table)s WHERE %(db_table)s.%(pk)s = %(value)i
                UNION
                SELECT %(db_table)s.%(pk)s FROM %(db_table)s JOIN deep ON %(db_table)s.%(relation_field)s = deep.n
            ) SELECT * FROM deep
        """ % {
            "db_table": qn(db_table),
            "pk": qn(pk),
            "relation_field": qn(db_field),
            "value": object_pk,
        }
        return self.extra(where=["%s.%s IN (%s)" % (qn(db_table), qn(pk), query)])

# Models
class Client(models.Model):
    class Meta:
        verbose_name = "Client"
        ordering = ['parent__label', 'label']
    
    label = models.CharField("Nom", max_length=64) 
    parent = ClientField('Client', verbose_name='Parent', null=True, blank=True, limit_choices_to = {'parent__parent': None})
    coordinates = models.ForeignKey(Coordinate, verbose_name=u'Coordonnées', blank=True, null=True)
    emails = models.CharField("Emails séparés par des virgule", max_length=2048, blank=True, null=True)
    notifications_by_fax = models.BooleanField(u"Transmission des notifications par fax", default=False)

    objects = ClientManager()

    def __unicode__(self):
        if self.parent and self.parent.parent:
            return u"%s - %s" % (self.label, self.parent.label)
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

class UserProfileManager(models.Manager):
    
    def get_for_combo(self):
        return [(x.user.pk, x) for x in self.get_query_set().select_related("user", "client").order_by("client__label")]

class UserProfile(models.Model):
    user = models.ForeignKey(User, verbose_name="Utilisateur", unique=True)
    google_account = models.ForeignKey(GoogleAccount, verbose_name="Compte google", null=True, blank=True)
    client = ClientField(Client, verbose_name="Client", blank=True, null=True)
    
    objects = UserProfileManager()

    def __unicode__(self):
        if self.client:
            return u"%s (%s)" % (self.user, self.client.label)
        return u"%s" % self.user

    def get_clients(self):
        if self.user.is_superuser:
            return Client.objects.all()
        if self.client:
            return Client.objects.get_childs("parent", self.client.pk)
        return Client.objects.none()
