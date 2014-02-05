# -*- coding: utf-8 -*-

from django import template
from django.template.base import TemplateSyntaxError

import textwrap

register = template.Library()


@register.filter
def wordwrap(value, length):
    """
    Returns a list of string wordwrapped for length.
    """
    if not value:
        return value
    try:
        length = int(length)
    except ValueError:
        raise TemplateSyntaxError("length %s is not an integer" % (length,))

    output = []
    # First split on LF
    for line in value.split("\n"):
        output.extend( [ wrappedline for wrappedline in textwrap.wrap(line, length) ] )

    return output


@register.filter
def multiply(value, arguments):
    """
    Multiply value by multiplicator
    """
    if not arguments:
        raise TemplateSyntaxError("This tag requires an argument (multiplicator)")

    argument_list = arguments.split()
    multiplicator = argument_list[0]

    if len(argument_list) >= 2:
        start = argument_list[1]
    else:
        start = 0

    try:
        value = int(value)
    except ValueError:
        raise TemplateSyntaxError("value %s is not an integer" % (value,))

    try:
        multiplicator = int(multiplicator)
    except ValueError:
        raise TemplateSyntaxError("multiplicator %s is not an integer" % (multiplicator,))
    try:
        start = int(start)
    except ValueError:
        raise TemplateSyntaxError("start %s is not an integer" % (start,))

    return (value * multiplicator) + start
