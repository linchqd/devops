from django.shortcuts import render

# Create your views here.
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.utils.http import urlunquote_plus


class IndexView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/index.html'

class SuccessView(LoginRequiredMixin, TemplateView):
    template_name = "public/success.html"
    def get_context_data(self, **kwargs):
        context = super(SuccessView, self).get_context_data(**kwargs)
        next_url = self.kwargs.get("next", "")
        try:
            next_url = reverse(next_url)
        except Exception as e:
            next_url = urlunquote_plus(next_url)
        context["next_url"] = next_url
        return context
class ErrorView(LoginRequiredMixin, TemplateView):
    template_name = "public/error.html"
    def get_context_data(self, **kwargs):
        context = super(ErrorView, self).get_context_data(**kwargs)
        next_url = self.kwargs.get("next", "")
        msgs = self.kwargs.get("msgs", "")
        try:
            next_url = reverse(next_url)
        except Exception as e:
            next_url = urlunquote_plus(next_url)
        context["next_url"] = next_url
        context["msgs"] = msgs
        return context