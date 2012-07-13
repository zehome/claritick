# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import get_template
from django.template import Context, Template
from rappel.models import Rappel
import datetime

class Command(BaseCommand):
    def handle(self, *args, **options):
        rappels = Rappel.objects.all().filter(date__lte=datetime.datetime.now()).filter(date_email=None)
        for rappel in rappels:
            # Application du template email
            template = get_template("email/rappel.txt")
            context = Context({"ticket": rappel.ticket, 'childs': rappel.ticket.child.order_by('date_open')})
            data = template.render(context)
            
            template = Template("{% autoescape off %}[Rappel ticket {{ ticket.id }} ({{ ticket.state }})]: {{ ticket.title|striptags|truncatewords:64 }}{% endautoescape %}")
            subject = template.render(context)

            # Send the email
            mail = EmailMessage(subject, data, settings.DEFAULT_FROM_EMAIL, (rappel.user.email,))
            mail.send()

            rappel.date_email = datetime.datetime.now()
            rappel.save()
