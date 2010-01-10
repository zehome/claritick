# -*- coding: utf-8 -*-

from django import forms
from django.forms.forms import BoundField
from django.utils.html import conditional_escape
from django.utils.encoding import StrAndUnicode, smart_unicode, force_unicode

from claritick.ticket.models import *
from claritick.ticket.models import Client
from claritick.common.widgets import *
from dojango import forms as df

class TelephoneField(forms.Field):
    def clean(self, value):
        if not value:
            return
        
        try:
            cleaned_value = value.replace(" ", "").replace(".", "")
        except:
            raise ValidationError("Numero de telephone invalide.")
        
        if len(cleaned_value) != 10:
            raise forms.ValidationError("Le numero de telephone doit comporter 10 chiffres.")

        return cleaned_value

class PartialNewTicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ("category",)

class NewTicketForm(df.ModelForm):
    title = df.CharField(widget=df.TextInput(attrs={'size':'64'}))
    text = df.CharField(widget=df.Textarea(attrs={'cols':'90', 'rows': '20'}))
    
    client = df.ModelChoiceField(queryset = Client.objects.all(),
       widget=df.FilteringSelect(attrs={'queryExpr': '*${0}*'}), empty_label='')
    class Meta:
        model = Ticket
        exclude = ("opened_by",)

class SearchTicketForm(df.ModelForm):
    title = df.CharField(widget=df.TextInput(attrs={'size':'64'}), required=False)
    client = df.ModelChoiceField(queryset = Client.objects.all(),
        widget=df.FilteringSelect(attrs={'queryExpr': '*${0}*'}), empty_label='', required=False)
    category = df.ModelChoiceField(queryset = Category.objects.all(), 
        widget=df.FilteringSelect(), empty_label='', required=False)
    text = df.CharField(required=False)
    opened_by = df.ModelChoiceField(queryset = User.objects.all(), 
        widget=df.FilteringSelect(), required=False)
    
    class Meta:
        fields = ('category', 'project', 'priority', 'state',
                  'client', 'contact', 'opened_by', 'assigned_to', 
                  'title', 'text', 'keywords')
        model = Ticket
    
    def my_html_output(self, normal_row, error_row, row_ender, help_text_html, errors_on_separate_row, cols):
        "Helper function for outputting HTML. Used by as_table(), as_ul(), as_p()."
        top_errors = self.non_field_errors() # Errors that should be displayed above all fields.
        output, hidden_fields = [], []
        idx=1
        
        for name, field in self.fields.items():
            bf = BoundField(self, field, name)
            bf_errors = self.error_class([conditional_escape(error) for error in bf.errors]) # Escape and cache in local variable.
            if bf.is_hidden:
                if bf_errors:
                    top_errors.extend([u'(Hidden field %s) %s' % (name, force_unicode(e)) for e in bf_errors])
                hidden_fields.append(unicode(bf))
            else:
                if errors_on_separate_row and bf_errors:
                    output.append(error_row % force_unicode(bf_errors))
                if bf.label:
                    label = conditional_escape(force_unicode(bf.label))
                    # Only add the suffix if the label does not end in
                    # punctuation.
                    if self.label_suffix:
                        if label[-1] not in ':?.!':
                            label += self.label_suffix
                    label = bf.label_tag(label) or ''
                else:
                    label = ''
                if field.help_text:
                    help_text = help_text_html % force_unicode(field.help_text)
                else:
                    help_text = u''
                
                normal_row2 = normal_row
                if idx == 1:
                    normal_row2 = "<tr>%s" % (normal_row,)
                elif idx >= cols:
                    idx = 1
                    normal_row2 = "%s</tr>" % (normal_row,)
                
                idx += 1
                output.append(normal_row2 % {'errors': force_unicode(bf_errors), 'label': force_unicode(label), 'field': unicode(bf), 'help_text': help_text})
        
        if idx < cols:
            output.append("<td></td>" * (cols-idx) + "</tr>")
        
        if top_errors:
            output.insert(0, error_row % force_unicode(top_errors))
        if hidden_fields: # Insert any hidden fields in the last row.
            str_hidden = u''.join(hidden_fields)
            if output:
                last_row = output[-1]
                # Chop off the trailing row_ender (e.g. '</td></tr>') and
                # insert the hidden fields.
                if not last_row.endswith(row_ender):
                    # This can happen in the as_p() case (and possibly others
                    # that users write): if there are only top errors, we may
                    # not be able to conscript the last row for our purposes,
                    # so insert a new, empty row.
                    last_row = normal_row % {'errors': '', 'label': '', 'field': '', 'help_text': ''}
                    output.append(last_row)
                output[-1] = last_row[:-len(row_ender)] + str_hidden + row_ender
            else:
                # If there aren't any rows in the output, just append the
                # hidden fields.
                output.append(str_hidden)
        return mark_safe(u'\n'.join(output))

    
    def as_table(self, cols=5):
        "Returns this form rendered as HTML <tr>s -- excluding the <table></table>."
        return self.my_html_output(u'<th>%(label)s</th><td>%(errors)s%(field)s%(help_text)s</td>', u'<td colspan="2">%s</td>', '</td></tr>', u'<br />%s', False, cols=cols)
