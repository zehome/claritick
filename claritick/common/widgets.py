# -*- coding: utf-8 -*-

from django import forms
from django.conf import settings
from django.utils.safestring import mark_safe

from dojango import forms as df


class ColorPickerWidget(forms.TextInput):
    class Media:
        css = {
            'all': (
                settings.STATIC_URL + 'colorPicker.css',
            )
        }
        js = (
            settings.STATIC_URL + 'js/jquery-1.5.min.js',
            settings.STATIC_URL + 'js/jquery.colorPicker.js',
        )

    def __init__(self, language=None, attrs=None):
        self.language = language or settings.LANGUAGE_CODE[:2]
        super(ColorPickerWidget, self).__init__(attrs=attrs)

    def render(self, name, value, attrs=None):
        rendered = super(ColorPickerWidget, self).render(name, value, attrs)
        return rendered + mark_safe(u'''<script type="text/javascript">
            $('#id_%s').colorPicker();
            </script>''' % name)


class FilteringSelect(df.FilteringSelect):
    def __init__(self, *args, **kwargs):
        default_attrs = {
            "queryExpr": "*${0}*",
            "autoComplete": "false",
        }
        if "attrs" in kwargs:
            kwargs["attrs"].update(default_attrs)
        else:
            kwargs["attrs"] = default_attrs
        super(FilteringSelect, self).__init__(*args, **kwargs)
