__all__ = ("AboutView", "HomeView", "ServiceRulesView")

from typing import Any
from urllib.parse import urlparse

from django.contrib import messages
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import FormView
from django.views.generic.base import TemplateView

from core.mixins import FormMethodExtender
from datanar.message_levels import LOADING_LINKS, SHORT_LINK
from redirects.forms import RedirectForm, RedirectFormExtended
from redirects.models import Redirect
from redirects.tasks import create_redirects


class HomeView(FormMethodExtender, FormView):
    template_name = "homepage/main.html"
    success_url = reverse_lazy("homepage:home")

    def get_form_class(self) -> type[RedirectForm]:
        if self.request.user.is_authenticated:
            return RedirectFormExtended
        return RedirectForm

    def get_client_ip(self) -> str | None:
        ip_address = self.request.META.get("HTTP_X_REAL_IP")
        if ip_address is None:
            return self.request.META.get("REMOTE_ADDR")
        return ip_address

    def form_valid(self, form: RedirectForm) -> HttpResponse:
        links_file_field = "links_file"

        ip_address = self.get_client_ip()
        user = self.request.user
        if not user.is_authenticated:
            user = None

        if user is not None and links_file_field in self.request.FILES:
            data = form.cleaned_data

            links_file = data[links_file_field]

            file_path = default_storage.save(
                "link-files/" + links_file.name,
                ContentFile(links_file.read()),
            )

            data[links_file_field] = file_path

            task = create_redirects.delay(
                data,
                user.id,
                self.request.get_host(),
                ip_address,
            )

            messages.add_message(
                self.request,
                LOADING_LINKS,
                task.id,
            )

            return super().form_valid(form)

        if links_file_field in form.cleaned_data:
            del form.cleaned_data[links_file_field]

        long_link = form.cleaned_data[Redirect.long_link.field.name]
        url_long_link = urlparse(long_link)

        if url_long_link.netloc != self.request.get_host():
            redirect = Redirect.objects.create(
                **form.cleaned_data,
                create_method=Redirect.CreateMethod.WEB,
                ip_address=ip_address,
                user=user,
            )
            short_link = redirect.short_link
        else:
            short_link = url_long_link.path

        messages.add_message(
            self.request,
            SHORT_LINK,
            short_link,
        )

        return super().form_valid(form)

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["SHORT_LINK"] = SHORT_LINK
        context["LOADING_LINKS"] = LOADING_LINKS
        return context

    def delete(
        self,
        request: HttpRequest,
        *args: Any,
        **kwargs: Any,
    ) -> HttpResponseRedirect:
        short_link = request.POST.get(Redirect.short_link.field.name)
        if request.user.is_authenticated and short_link:
            Redirect.objects.filter(
                short_link=short_link,
                user=request.user,
            ).delete()
        return HttpResponseRedirect(request.get_full_path())


class ServiceRulesView(TemplateView):
    template_name = "homepage/service_rules.html"


class AboutView(TemplateView):
    template_name = "homepage/about.html"
