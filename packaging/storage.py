# -*- coding: utf-8 -*-

from django.core.files.storage import FileSystemStorage
from django.conf import settings

packaging_storage = FileSystemStorage(settings.PACKAGING_ROOT, base_url="/packaging/get/")