__all__ = ("RedirectView",)

from http import HTTPStatus
from typing import Any

from celery.result import AsyncResult
from django.contrib import messages
from django.contrib.gis.geoip2 import GeoIP2
from django.http import (
    Http404,
    HttpRequest,
    HttpResponse,
    HttpResponseRedirect,
)
from django.shortcuts import render
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import View
from geoip2.errors import AddressNotFoundError

from datanar.message_levels import SHORT_LINK
from redirects.forms import PasswordForm
from redirects.models import Redirect
from statistic.models import Click

geo_ip = GeoIP2()


class RedirectView(View):
    @staticmethod
    def _get_object(**kwargs: Any) -> Redirect:
        redirect = Redirect.objects.get_by_short_link(
            kwargs[Redirect.short_link.field.name],
        )

        if redirect is None or not redirect.is_active:
            raise Http404
        return redirect

    def get(
        self,
        request: HttpRequest,
        *args: Any,
        **kwargs: Any,
    ) -> HttpResponse:
        redirect = self._get_object(**kwargs)

        if redirect.password:
            form = PasswordForm()
            return render(request, "redirect/redirect.html", {"form": form})

        return self.perform_redirect(redirect)

    def post(
        self,
        request: HttpRequest,
        *args: Any,
        **kwargs: Any,
    ) -> HttpResponse:
        redirect = self._get_object(**kwargs)

        form = PasswordForm(request.POST)
        if form.is_valid():
            form_password = form.cleaned_data[Redirect.password.field.name]
            if form_password == redirect.password:
                return self.perform_redirect(redirect)

        form.add_error(Redirect.password.field.name, _("invalid_password"))
        return render(request, "redirect/redirect.html", {"form": form})

    def perform_redirect(self, redirect: Redirect) -> HttpResponseRedirect:
        ip_address = self.request.META.get("HTTP_X_REAL_IP", "127.0.0.1")

        try:
            country = geo_ip.country_name(ip_address)
        except AddressNotFoundError:
            country = ""

        try:
            city = geo_ip.city(ip_address)["city"]
        except AddressNotFoundError:
            city = ""

        Click.objects.create(
            redirect=redirect,
            os=self.request.user_agent.os.family,
            browser=self.request.user_agent.browser.family,
            country=country,
            city=city,
        )

        return HttpResponseRedirect(redirect.long_link)


class LinksFileStatus(View):
    def get(
        self,
        request: HttpRequest,
        *args: Any,
        **kwargs: Any,
    ) -> HttpResponse:
        task = AsyncResult(self.kwargs["work_id"])

        if not task.ready():
            return HttpResponse(status=HTTPStatus.ACCEPTED)

        for line in task.result:
            messages.add_message(request, SHORT_LINK, line)

        return HttpResponseRedirect(reverse("homepage:home"))
