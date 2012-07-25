# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand, CommandError
from lock.models import Lock

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        Lock.expired.all().delete()
