from django import template

register = template.Library()


@register.filter
def dinero(value):
    try:
        return '{:,.2f}'.format(float(value))
    except (TypeError, ValueError):
        return '0.00'
