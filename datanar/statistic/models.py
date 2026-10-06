__all__ = ("Click",)

from datetime import timedelta
from typing import TYPE_CHECKING

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from core.models import TimeStampedModel

if TYPE_CHECKING:
    from django.db.models import QuerySet


class ClickManager(models.Manager):
    def count_for_short_link(self, short_link: str) -> int:
        return (
            self.get_queryset()
            .filter(redirect__short_link=short_link)
            .prefetch_related(Click.redirect.field.name)
            .count()
        )

    def for_short_link_by_all_time(self, short_link: str) -> "QuerySet[Click]":
        return (
            self.get_queryset()
            .filter(redirect__short_link=short_link)
            .prefetch_related(Click.redirect.field.name)
            .only(
                Click.browser.field.name,
                Click.city.field.name,
                Click.country.field.name,
                f"{Click.redirect.field.name}_id",
                Click.os.field.name,
            )
        )

    def for_short_link_by_last_year(
        self,
        short_link: str,
    ) -> "QuerySet[Click]":
        return self.for_short_link_by_all_time(short_link).filter(
            clicked_at__gte=timezone.now() - timedelta(days=365),
        )

    def for_short_link_by_last_month(
        self,
        short_link: str,
    ) -> "QuerySet[Click]":
        return self.for_short_link_by_all_time(short_link).filter(
            clicked_at__gte=timezone.now() - timedelta(days=30),
        )

    def for_short_link_by_last_day(self, short_link: str) -> "QuerySet[Click]":
        return self.for_short_link_by_all_time(short_link).filter(
            clicked_at__gte=timezone.now() - timedelta(days=1),
        )


class Click(TimeStampedModel):
    redirect = models.ForeignKey(
        "redirects.Redirect",
        on_delete=models.CASCADE,
    )
    os = models.TextField(
        verbose_name=_("os"),
        help_text=_("operating_system_from_which_redirect_was_made"),
        blank=True,
        default="",
    )
    browser = models.TextField(
        verbose_name=_("browser"),
        help_text=_("browser_from_which_redirect_was_made"),
        blank=True,
        default="",
    )
    country = models.TextField(
        verbose_name=_("country"),
        help_text=_("country_from_which_redirect_was_made"),
        blank=True,
        default="",
    )
    city = models.TextField(
        verbose_name=_("city"),
        help_text=_("city_from_which_redirect_was_made"),
        blank=True,
        default="",
    )

    objects = ClickManager()

    class Meta:
        verbose_name = _("click")
        verbose_name_plural = _("clicks")

    def __str__(self) -> str:
        return str(self.created_at)
