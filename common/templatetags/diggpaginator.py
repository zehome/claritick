# -*- coding: utf-8 -*-

from django import template
from common.diggpaginator import DiggPage
register = template.Library()

class DiggPaginatorNode(template.Node):
    def __init__(self, page):
        self.page = template.Variable(page)
    
    def render(self, context):
        context.push()
        context["page"] = self.page.resolve(context)
        t = template.Template("""
<ol id="pagination-digg">
    {% if page.has_previous %}
        <li class="previous"><a href="?page={{ page.previous_page_number }}">«Précédent</a></li>
    {% endif %}
    {% for num in page.page_range %}
        {% if not num %}<li><a href="#">...</a></li>
        {% else %}
            {% ifequal page.number num %}<li class="active">{{ num }}</li>
            {% else %}<li><a href="?page={{ num }}">{{ num }}</a></li>
            {% endifequal %}
        {% endif %}
    {% endfor %}
    {% if page.has_next %}
        <li class="next"><a href="?page={{ page.next_page_number }}">Suivant»</a></li>
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
        raise template.TemplateSyntaxError, "%r tag requires page argument" % token.contents.split()[0]
    
    return DiggPaginatorNode(page)
