__all__ = ()

from typing import TYPE_CHECKING
from urllib.parse import urlparse

from django.contrib import admin
from django.http import HttpRequest
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from dashboard.models import BlockedDomain
from redirects.models import Redirect
from statistic.models import Click

if TYPE_CHECKING:
    from django.db.models import QuerySet


class ClickInline(admin.TabularInline):
    model = Click
    extra = 0

    readonly_fields = (
        Click.id.field.name,
        Click.country.field.name,
        Click.city.field.name,
        Click.os.field.name,
        Click.browser.field.name,
    )


MIN_DOMAIN_PARTS = 2


@admin.register(Redirect)
class ItemAdmin(admin.ModelAdmin):
    list_display = (
        Redirect.short_link.field.name,
        Redirect.created_at.field.name,
        Redirect.updated_at.field.name,
        Redirect.is_active.field.name,
        Redirect.create_method.field.name,
        Redirect.user.field.name,
    )

    @admin.action(description=_("block_selected_redirects"))
    def block(
        self,
        request: HttpRequest,
        queryset: "QuerySet",
    ) -> None:
        regex_urls = set()

        for url in queryset.values_list(
            Redirect.long_link.field.name,
            flat=True,
        ):
            netloc = urlparse(url).netloc.split(":")[0]
            parts = netloc.split(".")
            if len(parts) >= MIN_DOMAIN_PARTS:
                main_domain = parts[-2]
                regex_urls.add(f"||{main_domain}^")
            elif parts[0]:
                regex_urls.add(f"||{parts[0]}^")

        blocked_domains = [
            BlockedDomain(domain_regex=regex) for regex in regex_urls
        ]
        BlockedDomain.objects.bulk_create(
            blocked_domains,
            ignore_conflicts=True,
        )

        queryset.delete()

        self.message_user(request, _("success_block_selected_redirect"))

    @admin.action(description=_("deactivate_selected_redirects"))
    def deactivate(
        self,
        request: HttpRequest,
        queryset: "QuerySet",
    ) -> None:
        queryset.update(
            is_active=False,
            deactivated_at=timezone.now(),
        )
        self.message_user(request, _("success_deactivate_selected_redirect"))

    @admin.action(description=_("activate_selected_redirects"))
    def activate(
        self,
        request: HttpRequest,
        queryset: "QuerySet",
    ) -> None:
        queryset.update(
            is_active=True,
            deactivated_at=None,
            validity_days=None,
        )
        self.message_user(request, _("success_activate_selected_redirect"))

    inlines = [ClickInline]
    actions = ["block", "deactivate", "activate"]
