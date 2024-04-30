from django import template

register = template.Library()

@register.filter
def count_substring_occurrences(value):
    return value.count("MessageMedia")