# -*- coding: utf-8 -*-

from django import template

register = template.Library()


@register.filter(name='has_group') 
def has_group(user, group_name):
    return user.groups.filter(name=group_name).exists() 


@register.filter(name='get_value')
def get_value(queryset, key):
    return queryset.get(key)
