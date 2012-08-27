# -*- coding: utf-8 -*-

import base64
import random
import string
from django.conf import settings

try:
    import cPickle as pickle
except ImportError:
    import pickle

from django.contrib.auth.models import User
from django.db import models
from django.utils import simplejson as json
from django import forms

# On charge psycopg2 pour ByteaField
try:
    import psycopg2
except ImportError:
    raise Exception(u"le module pyscopg2 est indispensable pour le field ByetaField.")

from common.widgets import ColorPickerWidget
from common.utils import sort_queryset


class ByteaField(models.TextField):
    """
    Field pour gerer le type bytea de porstgres.
    psycopg2 obligatoire.
    """
    description = "A field to handle postgres bytea fields"

    def db_type(self, connection):
        return 'bytea'

    def get_db_prep_lookup(self, lookup_type, value,
                           connection, prepared=False):
        raise TypeError('Lookup type %r not supported.' % lookup_type)

    def get_db_prep_value(self, value, connection, prepared=False):
        return self.get_prep_value(value, connection)

    def get_prep_value(self, value, connection):
        return buffer(value)


class PickleField(models.TextField):
    """
    Un ByteaField qui fait des pickle loads/dumps en entrée/sortie.
    """
    __metaclass__ = models.SubfieldBase

    def db_type(self, connection):
        return 'bytea'

    def get_db_prep_lookup(self, lookup_type, value, connection,
                           prepared=False):
        raise TypeError('Lookup type %r not supported.' % lookup_type)

    def get_prep_value(self, value, connection):
        return buffer(pickle.dumps(value, 2))

    def get_db_prep_value(self, value, connection, prepared=False):
        return self.get_prep_value(value, connection)

    def to_python(self, value):
        if isinstance(value, buffer):
            return pickle.loads(str(value))
        return value


class Base64Field(models.TextField):
    def contribute_to_class(self, cls, name):
        if self.db_column is None:
            self.db_column = name
        self.field_name = name + '_base64'
        super(Base64Field, self).contribute_to_class(cls, self.field_name)
        setattr(cls, name, property(self.get_data, self.set_data))

    def get_data(self, obj):
        return base64.decodestring(getattr(obj, self.field_name))

    def set_data(self, obj, data):
        setattr(obj, self.field_name, base64.encodestring(data))


class JsonField(models.TextField):
    __metaclass__ = models.SubfieldBase

    def to_python(self, value):
        if isinstance(value, (str, unicode)) and value != "":
            return json.loads(value)
        return value

    def get_db_prep_value(self, value, connection, prepared=False):
        return self.get_prep_value(value, connection)

    def get_prep_value(self, value, connection):
        return json.dumps(value)


class TelephoneField(models.CharField):
    def __init__(self, *args, **kw):
        kw["max_length"] = 10
        kw["blank"] = True
        kw["null"] = True
        super(TelephoneField, self).__init__(*args, **kw)


class OneLineTextField(models.TextField):
    """
    Un TextField au niveau db qui s'affiche comme un CharField
    dans les formulaires.
    """
    def formfield(self, **kwargs):
        defaults = {
            "widget": forms.TextInput
        }
        defaults.update(kwargs)
        return super(OneLineTextField, self).formfield(**defaults)


class Coordinate(models.Model):
    class Meta:
        verbose_name = u"Coordonnées"
        ordering = ["destinataire", "address_line1"]

    telephone = TelephoneField(u"Téléphone fixe")
    gsm = TelephoneField(u"Téléphone portable")
    fax = TelephoneField(u"Fax")
    destinataire = models.CharField(u"Destinataire",
                                    max_length=128, blank=True, null=True)
    address_line1 = models.CharField(u"Ligne1",
                                     max_length=128, blank=True, null=True)
    address_line2 = models.CharField(u"Ligne2",
                                     max_length=128, blank=True, null=True)
    address_line3 = models.CharField(u"Ligne3",
                                     max_length=128, blank=True, null=True)
    postalcode = models.CharField(u"Code postal",
                                  max_length=6, blank=True, null=True)
    city = models.CharField(u"Ville",
                            max_length=64, blank=True, null=True)
    email = models.EmailField(u"Email",
                              blank=True, null=True)
    more = models.TextField(u"Complément d'information", blank=True, null=True)

    def __unicode__(self):
        return u"%s%s%s%s" % (
            self.destinataire and self.destinataire + ' ' or '',
            self.address_line1 and self.address_line1 + ' ' or '',
            self.postalcode and self.postalcode + ' ' or '',
            self.city and self.city + ' ' or '')


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
        defaults = kwargs
        return super(ClientField, self).formfield(**defaults)


class ClientManager(models.Manager):

    def get_query_set(self):
        qs = super(ClientManager, self).get_query_set() \
                    .select_related("parent", "parent__parent", "coordinates")
        return qs

    def get_childs(self, field, object_pk):
        """
        Effectue un WITH RECURSIVE Postgres sur field
        a partir de l'objet object_pk.
        """
        if settings.POSTGRESQL_VERSION >= 8.4:
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
        else:
            ## SLOW METHOD
            clients = list(self.select_related("parent", "id").all().exclude(id=object_pk))
            childs = [ object_pk, ]

            def recurse_get_child(parent_pk):
                for client in clients[:]:  # for the remove
                    if client.parent and client.parent.id == parent_pk:
                        clients.remove(client)
                        childs.append(client.id)
                        recurse_get_child(client.id)

            recurse_get_child(object_pk)
            return self.filter(id__in=childs)


class Client(models.Model):
    class Meta:
        verbose_name = "Client"
        ordering = ['parent__label', 'label']

    label = models.CharField(u"Nom", max_length=64) 
    parent = ClientField(u'Client',
                         verbose_name=u'Parent',
                         null=True, blank=True)
    coordinates = models.ForeignKey(Coordinate,
                                    verbose_name=u'Coordonnées',
                                    blank=True, null=True)
    emails = models.CharField(u"Emails séparés par des virgule",
                              max_length=2048,
                              blank=True, null=True)
    notifications_by_fax = models.BooleanField(
                                u"Transmission des notifications par fax",
                                default=False)

    objects = ClientManager()

    def __unicode__(self):
#        if self.parent and self.parent.parent:
        if self.parent and self.parent.label != 'Clarisys':
            return u"%s - %s" % (self.parent.label, self.label)
        return u"%s" % (self.label,)

    def get_emails(self):
        """ Returns emails of this site plus email of the parent """
        if self.emails:
            emails = [e.strip() for e in self.emails.split(",")]
        else:
            emails = []
        if self.parent:
            emails.extend(self.parent.get_emails())
        return emails

    def get_faxes(self):
        """ Returns list of fax numbers """
        if self.coordinates and self.coordinates.fax:
            faxes = [self.coordinates.fax, ]
        else:
            faxes = []
        if self.parent:
            faxes.extend(self.parent.get_faxes())
        return faxes


class GoogleAccount(models.Model):
    login = models.EmailField("Login")
    password = models.CharField("Mot de passe", max_length=64)

    def __unicode__(self):
        return u"Compte google %s" % (self.login,)


class ClaritickUserManager(models.Manager):
    """
        ModelManager de ClaritickUser
    """
    def get_query_set(self):
        """
        On va chercher le userprofile et client,
        ainsi que d'autre attributs du profil.

        En sortie, l'objet aura un attribut client correspondant
        au userprofileclient__label de l'utilisateur.
        """
        return super(ClaritickUserManager, self).get_query_set().\
            extra(select={"client": '"common_client"."label"',
                  "security_level": '"common_userprofile"."security_level"'}).\
            select_related("userprofile", "userprofile__client",
                           "userprofile__security_level")\
                        .order_by("userprofile__client__label")


class ClaritickUser(User):
    """
        Model proxy de User.
    """
    client = u""
    #security_level = 99
    objects = ClaritickUserManager()

    def __unicode__(self):
        if self.client:
            return u"%s (%s)" % (self.username, self.client)
        return u"%s" % self.username

    def get_client(self):
        if hasattr(self, "client"):
            return self.client or u""
        return u""
    get_client.short_description = u"Client"

    def get_security_level(self):
        print dir(self)
        return getattr(self, "security_level", 99)
    get_security_level.short_description = u"Security level"

    def get_child_users(self):
        """
            Retourne tous les ClaritickUser de l'arbre client de l'utilisateur.
        """
        client = self.get_profile().client
        if client:
            return ClaritickUser.objects.filter(
                userprofile__client__in=Client.objects.get_childs("parent", self.get_profile().client.pk)
            )
        return ClaritickUser.objects.none()

    class Meta:
        verbose_name = u"Utilisateur Claritick"
        verbose_name_plural = u"Utilisateurs Claritick"
        proxy = True
        permissions = (
            ("no_autologout", u"Pas de logout automatique"),
        )

    @staticmethod
    def generate_random_password():
        """
            Genere un mot de passe aléatoire de 8 caracteres.
        """
        words = string.letters + string.digits
        return "".join(map(lambda x: random.choice(words), range(8)))


class UserProfileManager(models.Manager):
    def get_query_set(self):
        return super(UserProfileManager, self).get_query_set().\
                select_related("user", "client")


class UserProfile(models.Model):

    objects = UserProfileManager()
    user = models.ForeignKey(User, verbose_name=u"Utilisateur", unique=True)
    google_account = models.ForeignKey(GoogleAccount,
                                       verbose_name=u"Compte google",
                                       null=True, blank=True)
    client = ClientField(Client, verbose_name=u"Client",
                         blank=True, null=True)
    trafiquables = models.TextField(null=True, blank=True)

    # Liste des tickets vus / date derni�re modif ticket
    tickets_vus = JsonField(null=True, blank=True)

    # Niveau de s�curit�
    # null = default level (from settings)
    security_level = models.IntegerField(null=True)

    def __unicode__(self):
        if self.client:
            return u"%s (%s)" % (self.user, self.client.label)
        return u"%s" % self.user

    def get_clients(self):
        if self.user.is_superuser:
            return sort_queryset(Client.objects.all())
        if self.client:
            return sort_queryset(Client.objects.get_childs("parent", self.client.pk))
        return Client.objects.none()

    def get_security_level(self):
        """
        Returns the user security level.

        Lower level is higher security level.
        If the user has no security level defined,
        then it gets the DEFAULT_USER_SECURITY_LEVEL from settings.

        If settings is not defined, then it gains security level 99
        """

        if self.security_level is None:
            try:
                return settings.SECURITY["DEFAULT_USER_LEVEL"]
            except (AttributeError, KeyError):
                return 99
        else:
            return self.security_level

    # Trafiquables
    def _get_trafiquables(self):
        if not self.trafiquables:
            return {}
        try:
            traf = json.loads(self.trafiquables)
        except (ValueError, TypeError):
            traf = {}
        return traf

    def set_trafiquable(self, id_table, liste_colonnes):
        traf = self._get_trafiquables()
        traf.update({id_table: liste_colonnes})
        self.trafiquables = json.dumps(traf)
        self.save()

    def get_trafiquable(self, id_table):
        traf = self._get_trafiquables()
        return traf.get("id_table", [])

    def clear_trafiquable(self, id_table):
        traf = self._get_trafiquables()
        traf.pop(id_table)
        self.trafiquables = json.dumps(traf)
        self.save()
