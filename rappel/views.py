# -*- coding: utf-8 -*-

from django.contrib.auth.decorators import permission_required
from rappel.models import Rappel
import datetime

@permission_required("rappel.can_use_rappel")
def list_rappel(request):
    list_of_rappel = Rappel.objects.filter(date__lte=datetime.datetime.now()).filter(user=request.user)
    return list_of_rappel.order_by("date")
