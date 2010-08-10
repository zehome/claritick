# -*- coding: utf8 -*-

from developpements.models import Project

def projects(request):
    if request.user and not request.user.is_anonymous():
        return {
            "developpements_projects" : Project.objects.filter(group__user = request.user),
            }

    return {"developpements_projects": []}

