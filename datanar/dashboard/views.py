__all__ = ("AllLinksView", "BlackListView", "LogView")

from pathlib import Path
from typing import Any, TYPE_CHECKING

from django.conf import settings
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.views.generic import ListView, TemplateView

from core.mixins import (
    FormMethodExtender,
    RedirectToLastPageMixin,
    StaffUserRequiredMixin,
)
from dashboard.models import BlockedDomain
from redirects.models import Redirect

if TYPE_CHECKING:
    from django.db.models import QuerySet


class AllLinksView(
    StaffUserRequiredMixin,
    FormMethodExtender,
    RedirectToLastPageMixin,
    ListView,
):
    template_name = "dashboard/all_links.html"
    context_object_name = "links"
    paginate_by = 6

    def get_queryset(self) -> "QuerySet":
        return Redirect.objects.only(
            Redirect.short_link.field.name,
        ).order_by(
            f"-{Redirect.created_at.field.name}",
        )

    def delete(self, request: HttpRequest) -> HttpResponse:
        Redirect.objects.filter(
            short_link=request.POST.get(Redirect.short_link.field.name),
        ).delete()
        return HttpResponseRedirect(request.get_full_path())


class BlackListView(
    StaffUserRequiredMixin,
    FormMethodExtender,
    RedirectToLastPageMixin,
    ListView,
):
    template_name = "dashboard/black_list.html"
    context_object_name = "domains"
    model = BlockedDomain
    paginate_by = 15

    def delete(self, request: HttpRequest) -> HttpResponse:
        BlockedDomain.objects.filter(id=request.POST.get("id")).delete()
        return HttpResponseRedirect(request.get_full_path())

    def patch(self, request: HttpRequest) -> HttpResponse:
        BlockedDomain.objects.filter(
            id=request.POST.get("id"),
        ).update(
            domain_regex=request.POST.get("new_domain_regex"),
        )
        return HttpResponseRedirect(request.get_full_path())

    def put(self, request: HttpRequest) -> HttpResponse:
        BlockedDomain.objects.create(
            domain_regex=request.POST.get("new_domain_regex"),
        )
        return HttpResponseRedirect(request.get_full_path())


class LogView(StaffUserRequiredMixin, FormMethodExtender, TemplateView):
    template_name = "dashboard/log.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        if settings.LOG_FILE_PATH:
            with Path(settings.LOG_FILE_PATH).open("rt") as log:
                context["log"] = log.read()
        return context

    def delete(self, request: HttpRequest) -> HttpResponse:
        if settings.LOG_FILE_PATH:
            with Path(settings.LOG_FILE_PATH).open("w") as log:
                log.write("")
        return HttpResponseRedirect(request.get_full_path())
