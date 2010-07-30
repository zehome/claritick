# -*- coding: utf8 -*-

from developpements.models import Project

def projects(request):
    return {"developpements_projects": Project.objects.all() }
