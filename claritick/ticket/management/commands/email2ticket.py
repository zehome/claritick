# -*- coding: utf-8 -*-

import settings
import imaplib
import re
import email
from common.models import Client
from ticket.models import Category, Ticket, State, TicketFile
from ticket.views import post_comment
from common.html2text import html2text
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.template.loader import get_template
from django.template import Context

pattern_from = re.compile('.*<(.*@.*)>')
pattern_subject = re.compile('^(\d+)\ ')
pattern_body = re.compile('\[contenu\](.+)\[/contenu\]', re.DOTALL | re.IGNORECASE)


def send_error(to, reasons):
    """ Envoie un mail d'érreur """
    template = get_template("email/ticket_error.txt")
    context = Context({"reasons": reasons})
    data = template.render(context)
    send_mail("Ticket invalide", data, settings.DEFAULT_FROM_EMAIL, [to])
    print "Erreur <%s> : %s" % (to, ", ".join(reasons))


def email2ticket(string):
    """ Parse un mail et crée ou modifie le ticket concerné """
    errors = []

    mail = email.message_from_string(string)
    cur = None

    match = pattern_from.search(mail.get('From', ''))

    mail_from = mail.get('Return-Path',
        mail.get('Reply-To', match.groups()[0] if match else None))

    references = mail.get('References', '').split()

    if not references:
        references = mail.get('In-Reply-To', '').split()

    if references:
        ticket = Ticket.objects.get(message_id__in=references)
    else:
        ticket = Ticket()

    # Get first part
    for part in mail.walk():
        if part.get_content_type() in ('text/html', 'text/plain'):
            cur = part
            break

    if cur is None:
        return send_error(mail_from, ['Impossible de parser le message'])

    content = cur.get_payload(decode=True)

    if cur.get_content_type() == 'text/html':
        enc = cur.get_charsets()[0]
        content = content.decode(enc, 'ignore')
        content = html2text(content)

    match = pattern_body.search(content)

    if not match:
        errors.append('Contenu vide ou non encadré par [contenu][/contenu]')
        content = None
    else:
        content = match.groups()[0]

    user = User.objects.get(pk=settings.EMAIL_USER_PK)

    if references and content:  # New comment
        form = type("", (), {})()
        form.cleaned_data = {'comment': content, 'internal': False}
        form.instance = ticket
        request = type("", (), {})()
        request.user = user
        post_comment(form, request)
        print "Ticket commenté ", ticket.pk
    elif not references:  # New ticket
        try:
            subject = mail.get('Subject', '')
            match = pattern_subject.search(subject)
            ticket.client = Client.objects.get(pk=match.groups()[0])
            subject = subject[match.span()[1]:]
            ticket.title = " ".join([part[0].decode(part[1] or 'utf8') for part in email.header.decode_header(subject)])
        except:
            errors.append('Impossible de parser le sujet, client invalide ou sujet mal formé')

        if errors:
            send_error(mail_from, errors)
        else:
            ticket.message_id = mail.get('Message-ID', None)
            ticket.opened_by = user
            ticket.state = State.objects.get(pk=settings.TICKET_STATE_NEW)
            ticket.category = Category.objects.get(pk=settings.EMAIL_TICKET_CATEGORY_DEFAULT)
            ticket.text = content
            ticket.save()
            print "Ticket crée : ", ticket.pk
    elif errors:
        send_error(mail_from, errors)

    # Get attachements
    for part in mail.walk():
        filename = part.get_filename()
        content_type = part.get_content_type()
        if filename and content_type in settings.IMAP_ALLOWED_CONTENT_TYPES:
            ticket_file = TicketFile(ticket=ticket,
                                     filename=filename,
                                     content_type=content_type,
                                     data=part.get_payload(decode=True))
            ticket_file.save()


class Command(BaseCommand):
    def handle(self, *a, **kw):
        srv = imaplib.IMAP4_SSL(settings.IMAP_SERVER)

        if getattr(settings, 'IMAP_CRAM_MD5_LOGIN', False):
            srv.login_cram_md5(settings.IMAP_LOGIN, settings.IMAP_PASSWORD)
        else:
            srv.login(settings.IMAP_LOGIN, settings.IMAP_PASSWORD)

        srv.select('INBOX')
        typ, data = srv.search(None, 'UNSEEN')
        for n in data[0].split():
            typ, content = srv.fetch(n, '(RFC822)')
            content = content[0][1]
            email2ticket(content)
