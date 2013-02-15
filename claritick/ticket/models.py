# -*- coding: utf-8 -*-

import datetime

from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
import django.contrib.comments
from django.contrib.comments.signals import comment_was_posted
from django.core.exceptions import ValidationError, FieldError

# for email
from django.core.mail import EmailMessage
from django.template.loader import get_template
from django.template import Context, Template
from django.core.mail.message import make_msgid

# Clarisys fields
from common.models import ColorField, Client, ClientField
from common.models import JsonField, ByteaField, PickleField
from django.db.models import AutoField

# Lock
from lock.decorators import locked_content

# Desktop notifications
from desktopnotifications.models import DesktopNotification


def copy_model_instance(obj):
    initial = dict([(f.name, getattr(obj, f.name))
                    for f in obj._meta.fields
                    if not isinstance(f, AutoField)
                    and not f in obj._meta.parents.values()])
    return obj.__class__(**initial)


class Priority(models.Model):
    class Meta:
        verbose_name = u"Priorité"
        ordering = ['warning_duration', 'label']

    label = models.CharField("Libellé", max_length=64, blank=True)
    forecolor = ColorField("Couleur du texte", blank=True, null=True)
    backcolor = ColorField("Couleur de fond", blank=True)
    alarm = models.CharField("Alarme automatique", max_length=128, null=True, blank=True)

    good_duration = models.IntegerField("Durée en seconde => Bon", blank=True, null=True)
    warning_duration = models.IntegerField("Durée en seconde => Attention", blank=True, null=True)
    critical_duration = models.IntegerField("Durée en seconde => Critique", blank=True, null=True)

    def __unicode__(self):
        return u"%s" % (self.label,)


class State(models.Model):
    class Meta:
        verbose_name = "État"
        verbose_name_plural = "État"
        ordering = ['weight', 'label']

    label = models.CharField("Libellé", max_length=64)
    weight = models.IntegerField("Poids", default=1)
    img = models.FileField(upload_to='images/states', blank=True, null=True)

    def __unicode__(self):
        return u"%s" % (self.label,)


class Category(models.Model):
    """

    Exemple: Admin, Formation, Support, Développement, TODO
    """
    class Meta:
        verbose_name = "Catégorie"
        ordering = ['label']

    label = models.CharField("Libellé", max_length=64)

    def __unicode__(self):
        return u"%s" % (self.label,)


class ProjectManager(models.Manager):
    def get_query_set(self):
        return super(ProjectManager, self).get_query_set().select_related('procedure__label')


class Project(models.Model):
    class Meta:
        verbose_name = u"Projet"
        ordering = ['label']

    objects = ProjectManager()
    label = models.CharField("Libellé", max_length=64)
    color = ColorField("Couleur associée", blank=True, null=True)
    #watchers = models.ManyToManyField(User, blank=True)
    procedure = models.ForeignKey('Procedure',
                                  verbose_name=u'Procédure',
                                  limit_choices_to={'active': True},
                                  blank=True, null=True)

    def __unicode__(self):
        if self.procedure:
            return u"%s (%s)" % (self.label, self.procedure)
        return u"%s" % self.label

    def save(self, client_id=None, *a, **kw):
        """ Override save in order to pass "client" from ModelAdmin form """
        created = bool(not self.id)
        r = super(Project, self).save(*a, **kw)
        if created:
            # Ajoute les tickets correspondant a la procédure
            if self.procedure:
                for ticketOriginal in self.procedure.tickets.all():
                    ticket = copy_model_instance(ticketOriginal)
                    ticket.date_open = None
                    ticket.template = False
                    ticket.project = self
                    if client_id and not ticket.client:
                        ticket.client = Client.objects.get(pk=int(client_id))
                    ticket.save()
        return r


class Procedure(models.Model):
    class Meta:
        verbose_name = u"Procédure"
        ordering = ['label']

    label = models.CharField("Libellé", max_length=64)
    active = models.BooleanField()
    category = models.ForeignKey(Category, verbose_name="Catégorie")
    tickets = models.ManyToManyField('Ticket', verbose_name="Ticket", limit_choices_to={'template': True})

    def __unicode__(self):
        return u"%s" % (self.label,)


class TicketQuerySet(models.query.QuerySet):
    def add_order_by(self, request):
        sort = request.GET.get('sort', 'id')
        sort_order = int(request.GET.get('sort_order', 1))
        return self.order_by('%s%s' % (sort_order and '-' or '', sort))

    def filter_ticket_by_user(self, user, **kwargs):
        """
            Filtre un queryset de ticket en fonction des clients qu'a le droit de voir l'utilisateur.
            kwargs:
                -> no_client à True accepte les ticket sans client
        """

        no_client = kwargs.pop("no_client", False)

        # Si on est root, on ne filtre pas la liste
        if user.is_superuser:
            return self

        qs = Ticket.objects.none()

        query = models.Q(client__in=user.clients)

        if no_client:
            query |= models.Q(client__isnull=True)

        qs = self.filter(query)

        return qs
    filter_by_user = filter_ticket_by_user

    @staticmethod
    def build_keywords_lookup(value):
        """ Si value contient
        motcle1+motcle2,-motcle3+motcle4,motcle5,-motcle6
        ça signifie qu'on veut les tickets qui ont :
                le motcle1 ET le motcle2
            Ou
                le motcle5
            mais pas
                (le motcle3 ET le motcle4)
            ni
                le motcle6
        Donc
        where
            (
                ('motcle1' = ANY(...) AND 'motcle2' = ANY(...)) or
                'motcle5' = ANY(string_to_array(keywords))
            ) and
            NOT ('motcle3' = ANY(...) AND 'motcle4' = ANY(...)) and
            'motcle6' != ALL(string_to_array(keywords))
        """
        kw_groups = value.split(',')
        where_list = []
        where_param_list = []
        or_filters = []
        or_param_list = []
        for kw_group in kw_groups:
            if kw_group[:1] == "-":
                # Exclusion
                kw_group=kw_group[1:]
                if '+' in kw_group:
                    kws = kw_group.split('+')
                    where_list.append(
                        """ NOT (%s) """ % (" AND ".join([
                            """%s = ANY(string_to_array("ticket_ticket"."keywords", ','))"""
                            for kw in kws
                        ])))
                    where_param_list.extend(kws)
                else:
                    where_list.append(
                        """ %s != ALL(string_to_array("ticket_ticket"."keywords", ',')) """)
                    where_param_list.append(kw_group)
            else:
                # Filtrage
                if '+' in kw_group:
                    kws = kw_group.split('+')
                    or_filters.append(
                        """ (%s) """ % (" AND ".join([
                            """%s = ANY(string_to_array("ticket_ticket"."keywords", ','))"""
                            for kw in kws
                        ])))
                    or_param_list.extend(kws)
                else:
                    or_filters.append(
                        """ %s = ANY(string_to_array("ticket_ticket"."keywords", ',')) """)
                    or_param_list.append(kw_group)
        where_list.append(u" OR ".join(or_filters))
        where_param_list.extend(or_param_list)
        return {
            "where": where_list,
            "params": where_param_list,
        }


    def filter_queryset(self, filters, inverted_filters=None, *args, **kwargs):
        """ Filtre un queryset de ticket a partir d'un dictionnaire de fields lookup. """
        search_mapping = {
            'title': 'icontains',
            'text': 'icontains',
            'contact': 'icontains',
            "keywords": TicketQuerySet.build_keywords_lookup,
            'client': None,
        }
        inverted_search_mapping = {
            "not_client": None,
        }

        qs = self.all()
        for key, value in filters.items():
            try:
                if not value:
                    continue
                try:
                    lookup = search_mapping[key]
                    if callable(lookup):
                        lookup = lookup(value)
                except KeyError:
                    if isinstance(value, (list, models.query.QuerySet)):
                        lookup = "in"
                    else:
                        lookup = 'exact'
                if lookup is None:
                    continue
                if isinstance(lookup, dict):
                    qs = qs.extra(**lookup)
                else:
                    qs = qs.filter_or_child({"%s__%s" % (key, lookup): value}, *args, **kwargs)
            except (AttributeError, FieldError):
                pass
        if inverted_filters is None:
            inverted_filters = {}
        for key, value in inverted_filters.items():
            realkey = key[len("not_"):]  # LC: Strip not_
            try:
                if not value:
                    continue
                try:
                    lookup = inverted_search_mapping[realkey]
                    if callable(lookup):
                        lookup = lookup(value)
                except KeyError:
                    if isinstance(value, (list, models.query.QuerySet)):
                        lookup = "in"
                    else:
                        lookup = 'exact'
                if lookup is None:
                    continue
                if isinstance(lookup, dict):
                    qs = qs.extra(**lookup)
                else:
                    qs = qs.exclude(models.Q(**{"%s__%s" % (realkey, lookup): value}))
            except (AttributeError, FieldError):
                pass

        client = filters.get("client", None)
        if client:
            clients = Client.objects.get_childs("parent", int(client))
            qs = qs.filter(models.Q(client__in=[c.id for c in clients]))

        not_client_list = inverted_filters.get("not_client", [])
        if not_client_list:
            for not_client in not_client_list:
                not_clients = Client.objects.get_childs("parent", int(not_client))
                qs = qs.exclude(models.Q(client__in=[c.id for c in not_clients]))

        return qs

    def filter_or_child(self, filter, user=None):
        """ Filtre suivant filterdict avec un OR sur les fils
        ne renvoie que le pêre si un fils matche filterdict """
        qs = self.all()

        child_condition = models.Q(child__isnull=False)

        # Matcher sur les fils qui ne sont pas en diffusion ?
        if user and not user.has_perm("ticket.can_list_all"):
            child_condition &= models.Q(child__diffusion=True)

        if isinstance(filter, models.query_utils.Q):
            query = models.Q()
            for k, v in filter.children:
                query |= models.Q(**{'child__%s' % k: v})
            qs = qs.filter(filter |
                (child_condition & query))
        else:
            for k, v in filter.items():
                qs = qs.filter(models.Q(**{k: v}) |
                        (child_condition &
                        models.Q(**{"child__%s" % k: v})))
        return qs.distinct()


class QuerySetManager(models.Manager):
    def get_query_set(self):
        return TicketQuerySet(self.model)


class BaseTicketManager(QuerySetManager):
    def get_query_set(self):
        qs = super(BaseTicketManager, self).get_query_set().\
            select_related("opened_by", "assigned_to",
            "priority", "state", "validated_by", "category", "project", "parent__id",
            "client", "client__coordinates", "client__parent", "client__parent__coordinates", "client__parent__parent")
        return qs


class TicketManager(BaseTicketManager):
    def get_query_set(self):
        qs = super(TicketManager, self).get_query_set()
        qs = qs.filter(text__isnull=False)
        qs = qs.exclude(template__exact=True)
        return qs


class OpenTicketManager(TicketManager):
    def get_query_set(self):
        qs = super(OpenTicketManager, self).get_query_set()
        qs = qs.exclude(state__id__in=(0, 4))
        return qs


class Ticket(models.Model):
    class Meta:
        verbose_name = "Ticket"
        ordering = ['-last_modification']
        permissions = (
            ("can_view_report", u"Consulter les rapports"),
            ("add_ticket_full", u"Peut creer des tickets complet"),
            ("can_resolve", u"Peut resoudre des tickets"),
            ("can_list_all", u"Peut voir la liste détaillée"),
            ("can_validate_ticket", u"Peut valider un ticket"),
            ("can_add_child", u"Peut créer un ticket fils"),
            ("can_view_internal_comments", u"Peut voir les commentaires internes"),
            ("can_view_qbuilder", u"Peut voir le Query Builder"),
        )

    minimal = QuerySetManager()
    objects = BaseTicketManager()
    tickets = TicketManager()
    open_tickets = OpenTicketManager()

    # Info client
    client = ClientField(Client, verbose_name="Client", blank=True, null=True)
    contact = models.CharField("Contact", max_length=128, blank=True)
    telephone = models.CharField("Téléphone", max_length=20, blank=True)

    date_open = models.DateTimeField("Date d'ouverture", auto_now_add=True)
    last_modification = models.DateTimeField("Dernière modification",
                                             auto_now_add=True, auto_now=True)
    date_close = models.DateTimeField("Date de fermeture", blank=True, null=True)

    state = models.ForeignKey(State, verbose_name="État", blank=True, null=True)
    priority = models.ForeignKey(Priority, verbose_name="Priorité", blank=True, null=True)

    assigned_to = models.ForeignKey(User,
                                    related_name="assigned_to",
                                    verbose_name="Assigné à",
                                    blank=True, null=True)
    opened_by = models.ForeignKey(User,
                                  related_name="opened_by",
                                  verbose_name="Ouvert par")
    title = models.CharField("Titre", max_length=128, blank=True, null=True)
    text = models.TextField("Texte", blank=True, null=True)

    category = models.ForeignKey(Category,
                                 verbose_name="Catégorie")
    project = models.ForeignKey(Project,
                                verbose_name="Projet",
                                blank=True, null=True)

    # Si le ticket est d'une provenance extérieure, alors validated_by
    # ne sera pas défini. Il faudra qu'un "clarimen" Valide le ticket
    validated_by = models.ForeignKey(User,
                                     related_name="validated_by",
                                     verbose_name="Validé par",
                                     blank=True, null=True, default=None)

    # Pour faciliter la recherche
    keywords = models.CharField(u"Mots clefs",
                                max_length=1024, blank=True, null=True)

    # Calendar
    calendar_start_time = models.DateTimeField(u"Début évenement",
                                               blank=True, null=True)
    calendar_end_time = models.DateTimeField(u"Fin évenement",
                                             blank=True, null=True)
    calendar_title = models.CharField(u"Titre évenement",
                                      max_length=64, blank=True, null=True)

    template = models.BooleanField(u"Modèle", default=False)

    # parent ticket
    parent = models.ForeignKey('Ticket',
                               related_name="child",
                               verbose_name=u"Ticket parent",
                               blank=True, null=True)
    diffusion = models.BooleanField(default=True)

    # TODO nombre de comments
    nb_comments = models.IntegerField(default=0, editable=False)

    # Nombre d'appels du client
    nb_appels = models.IntegerField(default=0, editable=False)

    # Message id (si crée par email)
    message_id = models.TextField(null=True, editable=False, blank=True)

    # Par defaut à false
    update_google = False

    @property
    def is_closed(self):
        return self.date_close or self.state.id == settings.TICKET_STATE_CLOSED

    @property
    def close_style(self):
        if self.is_closed:
            return "text-decoration: line-through;"
        return ""

    @property
    def priority_text_style(self):
        style = ""
        if self.priority:
            p = self.priority
            if p.forecolor:
                style += "color: %s;" % (p.forecolor,)
        return style

    @property
    def priority_back_style(self):
        style = ""
        p = self.priority
        if p:
            if p.backcolor:
                style += "background-color: %s;" % (p.backcolor,)
        return style

    def is_valid(self):
        return bool(self.text and self.title)

    def get_absolute_url(self):
        return "/ticket/modify/%i" % (self.id,)

    def get_current_alarm(self):
        """ Renvoie l'alarme courante si elle existe sinon None """
        try:
            ret = TicketAlarm.opened.get(ticket=self)
        except TicketAlarm.DoesNotExist:
            ret = None
        return ret

    def __unicode__(self):
        return u"n° % s: %s" % (self.id, self.title)

    @staticmethod
    def handle_comment_posted_signal(sender, **kwargs):
        """ Updates ticket last_modification to now() """
        comment = kwargs["comment"]
        if comment.content_type.model != "ticket":
            return

        ticket = comment.content_object
        ticket.last_modification = datetime.datetime.now()
        ticket.nb_comments = django.contrib.comments.get_model().objects.filter(content_type__model="ticket", object_pk=ticket.pk).count()
        ticket.save()

        # Send email
        if ticket.diffusion and (
                not comment.internal or
                (comment.internal and getattr(settings, "EMAIL_INTERNAL_COMMENTS", True))
                ):
            send_email_reasons = [u"Nouvelle réponse%s" % (comment.internal and " (Diffusion interne seulement)" or ''), ]
            #ticket.send_email(reasons=send_email_reasons)
            ticket.ticketmailaction_set.create(reasons=send_email_reasons)
        ticket.send_desktop_notification("TNR")

    @staticmethod
    def handle_ticket_presave_signal(sender, **kwargs):
        new_ticket = kwargs["instance"]
        if not new_ticket.id:
            return

        try:
            Ticket.objects.get(id=new_ticket.id)
        except Ticket.DoesNotExist:
            return

    def clean(self):
        if self.state_id == settings.TICKET_STATE_CLOSED and self.child.exclude(state=self.state).exists():
            raise ValidationError("Impossible de fermer le ticket si tous les tickets fils ne sont pas fermés")

    def send_desktop_notification(self, tag):
        def get_desktop_notification_html(n):
            return "<h3>[%s]</h3><p>%s: %s<a target=\"_new\" href=\"https://claritick.clarisys.fr/ticket/modify/%s/\">Go</a></p>" % (self.id, tag, n.get_tag_display(), self.id)
        dests = set()
        # La personne qui a ouvert
        if self.opened_by:
            dests.add(self.opened_by)
        # La personne sur qui le ticket est assignée
        if self.assigned_to:
            dests.add(self.assigned_to)
        # Ceux qui ont participé (comments)
        dests = dests.union(set([
            c.user
            for c in django.contrib.comments.get_model().objects.filter(content_type__model="ticket",
                                                                        object_pk=str(self.id))
            if c.user]))

        for dest in dests:
            notification = DesktopNotification(user=dest)
            notification.tag = tag
            notification.content = get_desktop_notification_html(notification)
            notification.save()

    @locked_content
    def save(self, *a, **kw):
        """
        Overwrite save in order to do checks if email should be sent,
        then send email
        """

        try:
            old_ticket = Ticket.objects.get(id=self.id)
        except Ticket.DoesNotExist:
            old_ticket = None

        # Override date_close
        if old_ticket:
            if not old_ticket.is_closed and self.is_closed:
                self.date_close = datetime.datetime.now()
            # PP: On ne peux pas changer date_closed
            # if old_ticket.is_closed and not self.is_closed
            if old_ticket.is_closed and self.state_id != settings.TICKET_STATE_CLOSED:
                self.date_close = None

        ret = super(Ticket, self).save(*a, **kw)
        send_fax_reasons = []
        send_email_reasons = []
        send_desktop_notifications = []

        if self.is_valid():
            if old_ticket is None:
                r = u"Création du ticket"
                send_email_reasons = [r, ]
                send_fax_reasons = [r, ]
                if not self.assigned_to:
                    send_desktop_notifications.append("TU")
                else:
                    send_desktop_notifications.append("TC")
            else:
                if old_ticket.state and old_ticket.state != self.state:
                    r = u"Statut modifié: %s => %s" % (old_ticket.state, self.state)
                    send_email_reasons.append(r)
                    send_fax_reasons.append(r)

                    if (self.state == settings.TICKET_STATE_CLOSED):
                        send_desktop_notifications.append("TCL")
                if old_ticket.client and old_ticket.client != self.client:
                    r = u"Erreur d'affectation client"
                    send_email_reasons.append(r)
                    send_fax_reasons.append(r)
                if old_ticket.validated_by is None and self.validated_by:
                    send_email_reasons.append(u"Ticket accepté par %s" % (self.validated_by,))
                if (old_ticket.assigned_to and old_ticket.assigned_to != self.assigned_to):
                    if old_ticket.assigned_to and self.assigned_to and old_ticket.assigned_to.pk != self.assigned_to.pk:
                        send_email_reasons.append(u"Ticket re-affecté à %s" % (self.assigned_to,))
                        send_desktop_notifications.append("TA")
                elif (not old_ticket.assigned_to and self.assigned_to):
                    send_email_reasons.append(u"Ticket affecté à %s" % (self.assigned_to,))
                    send_desktop_notifications.append("TA")
            # Copie des paramêtres du père à reporter sur les fils
            # (Temporaire ?)
            if old_ticket and self.child:
                if old_ticket.priority != self.priority:
                    self.child.exclude(priority=self.priority).update(priority=self.priority)
                if old_ticket.client != self.client:
                    self.child.exclude(client=self.client).update(client=self.client)
                if old_ticket.contact != self.contact:
                    self.child.exclude(contact=self.contact).update(contact=self.contact)
                if old_ticket.telephone != self.telephone:
                    self.child.exclude(telephone=self.telephone).update(telephone=self.telephone)
                # PP: TODO Optimiser...
                for c in self.child.all():
                    c.save()

            # Si on change le paramètre diffusion de "True" vers "False",
            # On ne veut pas envoyer les emails en file d'attente!
            if old_ticket and old_ticket.diffusion and not self.diffusion:
                self.ticketmailtrace_set.all().delete()

        if self.parent:
            send_email_reasons = ["Ticket enfant %d : %s" % (self.pk, string) for string in send_email_reasons]
            send_fax_reasons = ["Ticket enfant %d : %s" % (self.pk, string) for string in send_fax_reasons]
            target_ticket = self.parent
        else:
            target_ticket = self

        if self.diffusion:
            if send_email_reasons:
                # LC: Do not send the email right now, wait some time before for grouping actions.
                #self.send_email(send_email_reasons)
                target_ticket.ticketmailaction_set.create(reasons=send_email_reasons)
            if send_fax_reasons:
                target_ticket.send_fax(send_fax_reasons)

        for tag in send_desktop_notifications:
            self.send_desktop_notification(tag)

        return ret

    def send_fax(self, reasons=[u'Demande spécifique']):
        """ Send a fax for this particuliar ticket """
        pass

    def send_email(self, reasons=[u"Demande spécifique", ]):
        """ Send an email for this particuliar ticket """
        dests = set()
        if self.client:
            dests = dests.union(set(self.client.get_emails()))

        # La personne qui a ouvert
        if self.opened_by.email:
            dests.add(self.opened_by.email)

        # La personne sur qui le ticket est assignée
        if self.assigned_to and self.assigned_to.email:
            dests.add(self.assigned_to.email)

        # Les project watchers ?
        # LC: TODO watchers

        # Ceux qui ont participé (comments)
        dests = dests.union(set([c.user.email
                                for c in django.contrib.comments.get_model().objects.filter(content_type__model="ticket",
                                                                                            object_pk=str(self.id))
                                if c.user and c.user.email]))

        #print "Envoi d'email à %s. Raisons: %s" % (dests, reasons)
        if not dests:
        #    print "Aucun destinataire email ?!"
            return

        # Application du template email
        template = get_template("email/ticket.txt")
        context = Context({"ticket": self,
                          'childs': self.child.order_by('date_open'),
                          'reasons': reasons})
        data = template.render(context)

        template = Template("{% autoescape off %}[Ticket {{ ticket.id }} ({{ ticket.state }})]: {{ ticket.title|striptags|truncatewords:64 }}{% endautoescape %}")
        subject = template.render(context)

        # Send the email
        mail = EmailMessage(subject, data, settings.DEFAULT_FROM_EMAIL, dests)

        if self.message_id:
            mail.extra_headers['In-Reply-To'] = self.message_id
            mail.extra_headers['References'] = self.message_id
        else:
            self.message_id = make_msgid()
            self.save()
            mail.extra_headers['Message-ID'] = self.message_id

        if self.keywords:
            mail.extra_headers['X-CLARITICK-KEYWORDS'] = self.keywords

        self.ticketmailtrace_set.create(email=mail)
        mail.send()


class TicketView(models.Model):
    """
    Represente un ensemble de critere de recherches.
    """
    user = models.ForeignKey(User)
    name = models.TextField(default=u"Nom de la vue")
    filters = JsonField()
    inverted_filters = JsonField(null=True, blank=True)
    notseen = models.BooleanField(default=False)

    class Meta:
        verbose_name = u"Vue"

    def __unicode__(self):
        return u"%s (%s)" % (self.name, self.user)


class TicketFileManager(models.Manager):
    def get_query_set(self):
        qs = super(TicketFileManager, self).get_query_set().defer('data').select_related('ticket__id')
        return qs


class TicketFile(models.Model):
    """
    Pièces jointe attachées aux tickets.
    """
    objects = TicketFileManager()
    with_data = models.Manager()
    ticket = models.ForeignKey(Ticket)
    filename = models.TextField()
    content_type = models.TextField()
    data = ByteaField()


class TicketMailAction(models.Model):
    class Meta:
        permissions = (
            ("can_delete_tma", u"Peut supprimer des ticket mail action"),
        )
        ordering = ["date"]
    """

    Une action d'envoie d'email a faire plus tard
    """

    date = models.DateTimeField(verbose_name=u"Date d'ajout",
                                auto_now_add=True, blank=False)
    reasons = PickleField(blank=False)
    ticket = models.ForeignKey(Ticket)

    class Meta:
        verbose_name = u"Email à envoyer"
        verbose_name_plural = u"Emails à envoyer"

    def __unicode__(self):
        return u"Email pour ticket %s à envoyer" % (self.ticket.id,)


class TicketMailTrace(models.Model):
    """
        Trace des mails envoyés par tickets.
    """
    ticket = models.ForeignKey(Ticket)
    date_sent = models.DateTimeField(auto_now_add=True)
    email = PickleField()

    class Meta:
        verbose_name = u"Logs des mails envoyés"
        verbose_name_plural = u"Logs des mails envoyés"
        ordering = ["date_sent"]


class TicketAlarmManager(models.Manager):
    def get_query_set(self):
        qs = super(TicketAlarmManager, self).get_query_set().select_related('user_open')
        return qs


class TicketAlarmOpenManager(TicketAlarmManager):
    def get_query_set(self):
        qs = super(TicketAlarmOpenManager, self).get_query_set().\
            select_related('ticket__title').\
            filter(user_close__isnull=True)
        return qs


class TicketAlarm(models.Model):

    objects = TicketAlarmManager()
    opened = TicketAlarmOpenManager()

    reason = models.CharField(u"Raison", max_length=128)
    date_open = models.DateTimeField(u"Date de creation", auto_now_add=True)
    user_open = models.ForeignKey(User, related_name="ticket_alarm_open")
    date_close = models.DateTimeField(u"Date de fermeture", null=True)
    user_close = models.ForeignKey(User,
                                   related_name="ticket_alarm_close", null=True)
    ticket = models.ForeignKey(Ticket)

    def title_string(self):
        if self.id:
            ret = "Alarme ouverte le %s par %s" % (
                self.date_open.strftime('%d/%m/%Y à %H:%M'), self.user_open,)
        else:
            ret = "Nouvelle alarme"
        return ret

    def __unicode__(self):
        return self.reason


class TicketAppelManager(models.Manager):
    def get_query_set(self):
        return super(TicketAppelManager, self).get_query_set().\
            select_related('user')


class TicketAppel(models.Model):
    """ Liste de date où le client a rappelé  """
    class Meta:
        ordering = ["date"]

    objects = TicketAppelManager()

    date = models.DateTimeField(auto_now_add=True)
    ticket = models.ForeignKey(Ticket)
    user = models.ForeignKey(User)

    def save(self, *args, **kwargs):
        ticket = Ticket.minimal.get(pk=self.ticket.pk)
        # peut être mieux de recalculer à chaque fois ....
        ticket.nb_appels = models.F('nb_appels') + 1
        ticket.save()
        return super(TicketAppel, self).save(*args, **kwargs)

#moderator.register(Ticket, TicketCommentModerator)

# Update last_modification time
comment_was_posted.connect(Ticket.handle_comment_posted_signal)

# Google calendar sync
models.signals.pre_save.connect(Ticket.handle_ticket_presave_signal,
                                sender=Ticket)
