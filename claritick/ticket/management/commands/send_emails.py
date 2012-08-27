# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand

from ticket.ticketmailaction import send_emails


class Command(BaseCommand):
    def handle(self, *args, **options):
        send_emails()
