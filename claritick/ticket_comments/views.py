#-*- coding: utf8 -*-

from django.contrib.comments import signals
from django.contrib.comments.views.comments import CommentPostBadRequest
from django.contrib.sites.models import Site
from datetime import datetime
from ticket_comments.models import TicketComment

# Custom post_comment,
# form doit être un formulaire de Ticket
# avec deux champs 'comment' et 'internal'
def post_comment(form, request):
    if "comment" in form.cleaned_data and form.cleaned_data['comment']:
        comment = TicketComment(
                content_object=form.instance,
                site=Site.objects.get_current(),
                user=request.user,
                user_name=request.user.username,
                user_email=request.user.email,
                comment=form.cleaned_data['comment'],
                submit_date=datetime.now(),
                is_public=True,
                is_removed=False,
                internal=form.cleaned_data['internal']
                )
        responses = signals.comment_will_be_posted.send(
                sender = comment.__class__,
                comment = comment,
                request = request
                )
        for (receiver, response) in responses:
            if response == False:
                return CommentPostBadRequest(
                    "comment_will_be_posted receiver %r killed the comment" % receiver.__name__)

        # Save the comment and signal that it was saved
        comment.save()
        signals.comment_was_posted.send(
            sender  = comment.__class__,
            comment = comment,
            request = request
        )

