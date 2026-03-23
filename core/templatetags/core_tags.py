# Custom template tags and filters
# Load in any template with: {% load core_tags %}

from django import template
from django.utils.html import format_html
from ..models import Article, Category

register = template.Library()


@register.filter(name='truncate_words')
def truncate_words(value, count):
    """Usage: {{ article.body|truncate_words:20 }}"""
    words = str(value).split()
    return ' '.join(words[:count]) + ('…' if len(words) > count else '')


@register.filter(name='status_badge')
def status_badge(status):
    """Usage: {{ article.status|status_badge }} → renders a Bootstrap badge"""
    colour = 'success' if status == 'published' else 'secondary'
    return format_html('<span class="badge bg-{}">{}</span>', colour, status.title())


@register.simple_tag
def published_count():
    """Usage: {% published_count %} → integer count of published articles"""
    return Article.objects.filter(status='published').count()


@register.inclusion_tag('core/_category_menu.html')
def category_menu():
    """Usage: {% category_menu %} → renders core/_category_menu.html"""
    return {'categories': Category.objects.all()}

@register.inclusion_tag('core/_category_menu.html', takes_context=True)
def category_menu(context):
    return {
        'categories': Category.objects.all(),
        'active_category': context.get('active_category', ''),
    }