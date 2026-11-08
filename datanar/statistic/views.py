__all__ = ("DownloadStatistic", "LinkDetailView", "MyLinksView")

from collections.abc import Iterable
from io import BytesIO
from typing import Any, TYPE_CHECKING

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Count
from django.http import (
    FileResponse,
    HttpRequest,
    HttpResponse,
    HttpResponseRedirect,
)
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext as _
from django.views import View
from django.views.generic import DetailView, ListView
import openpyxl

from core.mixins import FormMethodExtender, RedirectToLastPageMixin
from redirects.models import Redirect
from statistic.converters import Period
from statistic.models import Click

if TYPE_CHECKING:
    from django.db.models import QuerySet


class MyLinksView(
    LoginRequiredMixin,
    FormMethodExtender,
    RedirectToLastPageMixin,
    ListView,
):
    template_name = "statistic/my_links.html"
    context_object_name = "links"
    paginate_by = 7

    def get_queryset(self) -> "QuerySet":
        return (
            Redirect.objects.filter(user=self.request.user)
            .only(Redirect.short_link.field.name)
            .order_by(f"-{Redirect.created_at.field.name}")
        )

    def delete(self, request: HttpRequest) -> HttpResponse:
        Redirect.objects.filter(
            short_link=request.POST.get(Redirect.short_link.field.name),
            user=request.user,
        ).delete()
        return HttpResponseRedirect(request.get_full_path())


class LinkDetailView(LoginRequiredMixin, DetailView):
    template_name = "statistic/link_detail.html"
    context_object_name = "redirect"

    def get_object(self, queryset: "QuerySet | None" = None) -> Redirect:
        redirect = get_object_or_404(Redirect, short_link=self.kwargs["link"])
        if redirect.user == self.request.user or self.request.user.is_staff:
            return redirect
        return self.handle_no_permission()

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        period: Period = self.kwargs["period"]

        context = super().get_context_data(**kwargs)
        context["link"] = self.kwargs["link"]
        context["period"] = period

        clicks = Click.objects.by_period(
            context["redirect"].short_link,
            period,
        )

        statistics = self._get_statistics(
            clicks,
            (
                Click.browser.field.name,
                Click.os.field.name,
                Click.country.field.name,
                Click.city.field.name,
            ),
        )

        context.update({**statistics, "clicks": clicks.count()})
        return context

    @staticmethod
    def _get_statistics(
        clicks: "QuerySet",
        fields: Iterable[str],
    ) -> dict[str, dict[str, int]]:
        unknown_label = _("Unknown")
        res = {}

        for field in fields:
            data = dict(
                clicks.values(field)
                .annotate(n=Count("id"))
                .order_by("-n")
                .values_list(field, "n"),
            )
            if "" in data:
                data[unknown_label] = data.pop("")
            res.update({field: data})
        return res


class DownloadStatistic(LoginRequiredMixin, View):
    def get(
        self,
        request: HttpRequest,
        link: str,
        period: Period,
    ) -> FileResponse:
        redirect = get_object_or_404(Redirect, short_link=link)

        if redirect.user != request.user and not request.user.is_staff:
            raise PermissionDenied

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.append(
            (
                _("Created"),
                _("OS"),
                _("Browser"),
                _("Country"),
                _("City"),
            ),
        )

        clicks = Click.objects.by_period(link, period).iterator()
        for click in clicks:
            ws.append(
                [
                    click.created_at.replace(tzinfo=None),
                    click.os,
                    click.browser,
                    click.country,
                    click.city,
                ],
            )

        for column_cells in ws.columns:
            length = max(len(str(cell.value)) for cell in column_cells) + 2
            ws.column_dimensions[column_cells[0].column_letter].width = length

        virtual_workbook = BytesIO()
        wb.save(virtual_workbook)
        virtual_workbook.seek(0)

        return FileResponse(
            virtual_workbook,
            as_attachment=True,
            filename=f"statistic-{link}-{period}.xlsx",
        )
