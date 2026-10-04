__all__ = ("DownloadStatistic", "LinkDetailView", "MyLinksView")

from io import BytesIO
from typing import Any, TYPE_CHECKING

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import (
    FileResponse,
    HttpRequest,
    HttpResponse,
    HttpResponseRedirect,
)
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
import openpyxl

from core.mixins import FormMethodExtender, RedirectToLastPageMixin
from redirects.models import Redirect
from statistic.models import Click

if TYPE_CHECKING:
    from django.db.models import QuerySet


def get_clicks_by_mode(short_link: str, mode: str) -> "QuerySet":
    by_mode = {
        "year": Click.objects.for_short_link_by_last_year,
        "month": Click.objects.for_short_link_by_last_month,
        "day": Click.objects.for_short_link_by_last_day,
    }
    getter = by_mode.get(mode, Click.objects.for_short_link_by_all_time)
    return getter(short_link)


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
        link = get_object_or_404(Redirect, short_link=self.kwargs["link"])
        if link.user == self.request.user or self.request.user.is_staff:
            return link
        return self.handle_no_permission()

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["link"] = self.kwargs["link"]
        context["period"] = self.kwargs["period"]

        clicks = get_clicks_by_mode(
            context["redirect"].short_link,
            self.kwargs["period"],
        )

        context.update(
            {
                "browser": self._get_statistic(
                    clicks,
                    Click.browser.field.name,
                ),
                "os": self._get_statistic(
                    clicks,
                    Click.os.field.name,
                ),
                "country": self._get_statistic(
                    clicks,
                    Click.country.field.name,
                ),
                "city": self._get_statistic(
                    clicks,
                    Click.city.field.name,
                ),
                "clicks": clicks.count(),
            },
        )

        return context

    @staticmethod
    def _get_statistic(clicks: "QuerySet", field: str) -> dict[str, int]:
        unknown_label = gettext("Unknown")
        res = {}
        for click in clicks:
            field_value = getattr(click, field) or unknown_label
            res[field_value] = res.get(field_value, 0) + 1
        return res


class DownloadStatistic(View):
    def get(
        self,
        request: HttpRequest,
        link: str,
        period: str,
    ) -> HttpResponse:
        wb = openpyxl.Workbook()
        ws = wb.active

        headers = [
            "#",
            _("Created"),
            _("OS"),
            _("Browser"),
            _("Country"),
            _("City"),
        ]
        headers = list(map(str, headers))

        for col_num, header in enumerate(headers, 1):
            ws[f"{openpyxl.utils.get_column_letter(col_num)}1"] = header

        for number, click in enumerate(get_clicks_by_mode(link, period), 1):
            ws.append(
                [
                    number,
                    click.clicked_at.replace(tzinfo=None),
                    click.os,
                    click.browser,
                    click.country,
                    click.city,
                ],
            )

        for column_cells in ws.columns:
            length = max(len(str(cell.value)) for cell in column_cells) + 2
            ws.column_dimensions[
                openpyxl.utils.get_column_letter(column_cells[0].column)
            ].width = length

        virtual_workbook = BytesIO()
        wb.save(virtual_workbook)
        virtual_workbook.seek(0)

        return FileResponse(
            virtual_workbook,
            as_attachment=True,
            filename="statistic.xlsx",
        )
