# -*- coding: utf-8 -*-

import settings
import imaplib
import re
import email
from common.models import Client
from ticket.models import Category, Ticket, State
from ticket.views import post_comment
from common.html2text import html2text
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.core.mail import send_mail

def email2ticket(string):
    """ Parse un mail et crée ou modifie le ticket concerné """

    ticket = Ticket()

    cur = mail = email.message_from_string(string)

    references = cur.get('References', '').split()

    if not references:
        references = cur.get('In-Reply-To', '').split()

    if references:
        ticket = Ticket.objects.get(message_id__in=references)
    else:
        ticket = Ticket()

    # Get first part
    while cur.is_multipart():
        cur = cur.get_payload(0)
    content = cur.get_payload(decode=True)

    if cur.get_content_type() == 'text/html':
        try:
            pos = content.index('blockquote')
            content = content[:pos]
        except ValueError:
            pass

        enc = cur.get_charsets()[0]
        content = contend.decode(enc, 'ignore')
        content = html2text(content)

    if references: # Separation avec citation mail precedent
        m = re.compile('(On|Le).*,\ .*\s?.*@.*(wrote|écrit):').search(content)
        if m:
            content = content[:m.span()[0]]

    splited = []
    for line in content.split('\n'):
        if line == '--': # Thunderbird signature
            break
        elif line and line[0] != '>':
            splited.append(line)
    content = '\n'.join(splited)

    # TODO à reflechir
    user = User.objects.get(username='admin')

    if references: # New comment
        form = type("", (), {})()
        form.cleaned_data = {'comment': content, 'internal': False }
        form.instance = ticket
        request = type("", (), {})()
        request.user = user
        post_comment(form, request)
        print "Ticket commenté ", ticket.pk
    else: # New ticket
        try:
            ticket.text = content
            pattern = re.compile('(\d+) (.*)')
            m = pattern.search(cur.get('Subject', None))
            m = m.groups()
            ticket.client = Client.objects.get(pk=m[0])
            ticket.title = " ".join([part[0].decode(part[1] or 'utf8') for part in email.header.decode_header(m[1])])
            ticket.message_id = cur.get('Message-ID', None)
            ticket.opened_by = user
            ticket.state = State.objects.get(pk=settings.TICKET_STATE_NEW)
            ticket.category = Category.objects.get(label='Ticket')
            ticket.save()
            print "Ticket crée : ", ticket.pk
        except:
            m = re.compile('.*<(.*@.*)>').search(cur.get('From', ''))
            to = cur.get('Return-Path', cur.get('Reply-To', m.groups()[0] if m else None))
            if to:
                send_mail("Ticket invalide",
                        "Votre ticket est invalide, veuillez recommencer s'il vous plait\n"
                        "Rappels:\n"
                        "- Le mail doit avoir pour sujet votre numéro client suivi par le titre du ticket\n"
                        "- Le contenu du mail sera le contenu du ticket, il ne doit pas être vide\n"
                        "- Pour des raisons de compatibilité nous vous conseillons d'utiliser un programme de messagerie tel que Thunderbird : http://fr.www.mozillamessaging.com/fr/\n\n"
                        "--\n"
                        "CLARISYS Informatique       http://www.clarisys.fr/\n"
                        "1, Impasse de ratalens      31240 SAINT JEAN\n"
                        "Téléphone: 09 72 11 43 60   Fax: 05 11 11 11 11\n"
                        "\nEmail généré automatiquement par le système de suivi CLARITICK.",
                        settings.DEFAULT_FROM_EMAIL, [to])
                print "Erreur envoyé à ", to
            else:
                print "Impossible de renvoyer une erreur:", mail

class Command(BaseCommand):

    def handle(self, *a, **kw):
        srv = imaplib.IMAP4_SSL(settings.IMAP_SERVER)
        srv.login(settings.IMAP_LOGIN, settings.IMAP_PASSWORD)
        #srv.login_cram_md5(settings.IMAP_LOGIN, settings.IMAP_PASSWORD)
        srv.select('INBOX')
        typ, data = srv.search(None, 'UNSEEN')
        for n in data[0].split():
            typ, content = srv.fetch(n, '(RFC822)')
            content = content[0][1]
            email2ticket(content)


