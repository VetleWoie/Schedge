from django import template

register = template.Library()


@register.filter
def placeholder(field, args=None):
    if args == None:
        return field
    field.field.widget.attrs.update({ "placeholder": args })
    return field