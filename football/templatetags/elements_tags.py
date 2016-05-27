from django import template

register = template.Library()


@register.inclusion_tag('form_element.html')
def form_element(tag, _type):
    return {'tag': tag,
            'type': _type}
