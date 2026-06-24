from django import template

register = template.Library()


@register.filter
def dinero(value):
    try:
        return '{:,.2f}'.format(value)
    except (TypeError, ValueError):
        return '0.00'
