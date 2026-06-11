from django import template
from django.utils.safestring import mark_safe

from ..models import Color

register = template.Library()


@register.simple_tag(takes_context=True)
def theme_css_variables(context):
    request = context.get('request')
    variables = ''
    if request and request.user.is_authenticated:
        colors = Color.objects.filter(
            inquilino=request.user.inquilino,
            activo=True,
        )
        lines = [f'    --clr-{c.slug}: {c.hex};' for c in colors]
        if lines:
            variables = '\n'.join(lines)
    return mark_safe(f'<style>\n  :root {{\n{variables}\n  }}\n</style>')
