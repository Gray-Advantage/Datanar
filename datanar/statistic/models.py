__all__ = ("Click",)

from datetime import timedelta
from typing import TYPE_CHECKING

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from core.models import TimeStampedModel
from statistic.converters import Period

if TYPE_CHECKING:
    from collections.abc import Callable

    from django.db.models import QuerySet


class ClickManager(models.Manager):
    def count_for_link(self, short_link: str) -> int:
        return (
            self.get_queryset().filter(redirect__short_link=short_link).count()
        )

    def for_link(self, short_link: str) -> "QuerySet[Click]":
        return (
            self.get_queryset()
            .filter(redirect__short_link=short_link)
            .only(
                Click.os.field.name,
                Click.browser.field.name,
                Click.city.field.name,
                Click.country.field.name,
                Click.created_at.field.name,
            )
        )

    def for_link_last_year(self, short_link: str) -> "QuerySet[Click]":
        return self.for_link(short_link).filter(
            created_at__gte=timezone.now() - timedelta(days=365),
        )

    def for_link_last_month(self, short_link: str) -> "QuerySet[Click]":
        return self.for_link(short_link).filter(
            created_at__gte=timezone.now() - timedelta(days=30),
        )

    def for_link_last_day(self, short_link: str) -> "QuerySet[Click]":
        return self.for_link(short_link).filter(
            created_at__gte=timezone.now() - timedelta(days=1),
        )

    def by_period(self, short_link: str, period: Period) -> "QuerySet[Click]":
        periods: dict[str, Callable] = {
            Period.YEAR: self.for_link_last_year,
            Period.MONTH: self.for_link_last_month,
            Period.DAY: self.for_link_last_day,
        }
        return periods.get(period, self.for_link)(short_link)


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
