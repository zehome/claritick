# -*- coding: utf-8 -*-

from django import template
register = template.Library()


class DiggPaginatorNode(template.Node):
    def __init__(self, page):
        self.page = template.Variable(page)

    def render(self, context):
        query_dict = context["request"].GET.copy()
        if "page" in query_dict:
            del query_dict["page"]
        context.push()
        context["query_string"] = query_dict.urlencode()
        context["page"] = self.page.resolve(context)
        t = template.Template("""
<ol id="pagination-digg">
    {% if page.has_previous %}
        <li class="previous"><a href="?{% if query_string %}{{ query_string|escape }}&{% endif %}page={{ page.previous_page_number }}">«Précédent</a></li>
    {% endif %}
    {% for num in page.page_range %}
        {% if not num %}<li><a href="#">...</a></li>
        {% else %}
            {% ifequal page.number num %}<li class="active">{{ num }}</li>
            {% else %}<li><a href="?{% if query_string %}{{ query_string|escape }}&{% endif %}page={{ num }}">{{ num }}</a></li>
            {% endifequal %}
        {% endif %}
    {% endfor %}
    {% if page.has_next %}
        <li class="next"><a href="?{% if query_string %}{{ query_string|escape }}&{% endif %}page={{ page.next_page_number }}">Suivant»</a></li>
    {% endif %}
</ol>
        """)
        rendered_data = t.render(context)
        context.pop()
        return rendered_data


@register.tag
def diggpaginator(parser, token):
    try:
        # split_contents() knows not to split quoted strings.
        tag_name, page = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires page argument" % \
            token.contents.split()[0]

    return DiggPaginatorNode(page)
