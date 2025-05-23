from django.views.generic import TemplateView
from django.shortcuts import render


class AboutTemplateView(TemplateView):
    template_name = "pages/about.html"


class RulesTemplateView(TemplateView):
    template_name = 'pages/rules.html'


def csrf_failure(request, reason='', exception=None):
    return render(request, 'pages/403csrf.html', {
        'reason': reason,
        'exception': str(exception) if exception else None,
    }, status=403)


def page_not_found(request, exception):
    return render(request, 'pages/404.html', status=404)


def server_error(request):
    return render(request, 'pages/500.html', status=500)
