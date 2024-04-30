# -*- coding: utf-8 -*-

from django.shortcuts import render
from django.utils import translation


def get_translation_in(language, s):
    with translation.override(language):
        return translation.gettext(s)


def page_not_found_view(request, exception):
    print(get_translation_in('uk', 'Go to home page'))
    return render(
        request=request,
        template_name='errors/base.html',
        context={
            'error_description': get_translation_in('uk', 'Page not found'),
            'move_to_home_page_text': 'Перейти на головну сторінку',
        },
    )

def bad_request_view(request, exception):
    return render(
        request=request,
        template_name='errors/base.html',
        context={
            'error_description': get_translation_in('uk', 'Bad request'),
            'move_to_home_page_text': 'Перейти на головну сторінку',
        },
    )
