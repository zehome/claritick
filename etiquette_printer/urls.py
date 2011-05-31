# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url
urlpatterns = patterns('etiquette_printer.views',
    url(r'^print_etiquette/?$', 'ajax_print_etiquette', name="etiquette_printer.print"),
    url(r'^dialog/?$', 'get_dialog', name='etiquette_printer.test')
)
