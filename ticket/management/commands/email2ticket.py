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

def email2ticket(string):
    """ Parse un mail et renvoie le ticket crée (ou modifié) """

    ticket = Ticket()

    cur = mail = email.message_from_string(string)

    references = cur.get('In-Reply-To', '')

    if references:
        ticket = Ticket.objects.get(message_id=references)
    else:
        ticket = Ticket()

    import pdb
    pdb.set_trace()


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
        pattern = re.compile('(Le|On)\ .*(a\ écrit|wrote)\ ?:')
        m = pattern.search(content)
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

    if references:
        form = type("", (), {})()
        form.cleaned_data = {'comment': content, 'internal': False }
        form.instance = ticket
        request = type("", (), {})()
        request.user = user
        post_comment(form, request)
    else: # New ticket
        ticket.text = content
        pattern = re.compile('(\d+) (.*)')
        m = pattern.search(cur.get('Subject', None))
        m = m.groups()
        ticket.client = Client.objects.get(pk=m[0])
        ticket.title = " ".join([part[0] for part in email.header.decode_header(m[1])])
        ticket.message_id = cur.get('Message-ID', None)
        ticket.opened_by = user
        ticket.state = State.objects.get(pk=settings.TICKET_STATE_NEW)
        ticket.category = Category.objects.get(label='Ticket')
        ticket.save()
    return ticket

class Command(BaseCommand):

    def handle(self, *a, **kw):
        srv = imaplib.IMAP4_SSL(settings.IMAP_SERVER)
        srv.login(settings.IMAP_LOGIN, settings.IMAP_PASSWORD)
        srv.select('INBOX')
        #typ, data = srv.search(None, 'UNSEEN')
        typ, data = srv.search(None, 'ALL')
        n = data[0].split()[-1]
        if n:
        #for n in data[0].split():
            typ, content = srv.fetch(n, '(RFC822)')
            content = content[0][1]
            ticket = email2ticket(content)
            print "NEW TICKET", ticket.id
