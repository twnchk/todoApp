from django import template

register = template.Library()


@register.filter
def filter_status(tasks, status):
    return tasks.filter(status=status)
