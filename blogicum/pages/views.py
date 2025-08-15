from django.shortcuts import render
from django.views.generic import TemplateView
from http import HTTPStatus


def handle_forbidden(request, reason=''):
    return render(request, 'pages/403csrf.html', status=HTTPStatus.FORBIDDEN)


def handle_not_found(request, exception=None):
    return render(request, 'pages/404.html', status=HTTPStatus.NOT_FOUND)


def handle_internal_server_error(request):
    return render(request, 'pages/500.html',
                  status=HTTPStatus.INTERNAL_SERVER_ERROR)


class AboutPage(TemplateView):
    template_name = 'pages/about.html'


class RulesPage(TemplateView):
    template_name = 'pages/rules.html'
