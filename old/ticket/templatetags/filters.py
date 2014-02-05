# -*- coding: utf8 -*-

from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


# Interprete une chaine avec des arguments
# "foo%s", "bar" -> "foobar"
@stringfilter
def interpret(value, arg):
    return value % arg


register.filter('interpret', interpret)
