# -*- coding: utf-8 -*-

import re
import os
import logging
from django.conf import settings

logger = logging.getLogger("anticachemiddleware")

"""
(c) 2012 Laurent Coustet
Licence: BSD
Anti browser cache media URL transformer.

Will append ?mtime to all your "REPLACE_MEDIA_URL"s.

Set ANTICACHE_MEDIA_ROOT and ANTICACHE_MEDIA_URL in your local settings please.
"""

if hasattr(settings, "ANTICACHE_MEDIA_URL"):
    REPLACE_MEDIA_URL = settings.ANTICACHE_MEDIA_URL
else:
    REPLACE_MEDIA_URL = settings.MEDIA_URL

if hasattr(settings, "ANTICACHE_MEDIA_ROOT"):
    REPLACE_MEDIA_ROOT = settings.ANTICACHE_MEDIA_ROOT
else:
    REPLACE_MEDIA_ROOT = settings.MEDIA_ROOT


MEDIA_REPLACE_RE = re.compile(r"""(%s)([^'"]+)""" % (REPLACE_MEDIA_URL,))
MAX_PAGE_SIZE = 512 * 1024


def _subreplace(m):
    try:
        media_path = os.path.join(REPLACE_MEDIA_ROOT, m.group(2))
        mtime = os.stat(media_path)[8]
    except:
        logger.exception("Unknown error in anticache middleware replace.")
        return m.group(0)
    else:
        return "%s?%s" % (m.group(0), mtime)


class MediaAnticacheMiddleware(object):
    """
    This middleware will read django settings and add modification time
    to media urls.

    Example:
    <html>
        <script src="/media/js/pouetpouet.js"></script>
    </html>

    will replace it with /media/js/pouetpouet.js?1358752135

    where 1358752135 is the mtime.
    """
    def process_response(self, request, response):
        response_content_type = response.get("Content-Type", "")
        # We don't want to parse something else!
        if "text/html" in response_content_type or \
           "text/css" in response_content_type or \
           "javascript" in response_content_type:
            # We don't want to parse/replace on longer pages!
            if len(response.content) <= MAX_PAGE_SIZE:
                response.content = \
                    MEDIA_REPLACE_RE.sub(_subreplace, response.content)

        return response
