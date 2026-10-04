__all__ = ("Redirect",)


from django.db import models
from django.utils.translation import gettext_lazy as _

from core.models import UserLinkModel


class RedirectManager(models.Manager):
    def get_by_short_link(self, short_link: str) -> "Redirect | None":
        redirect: Redirect | None = (
            self.get_queryset()
            .filter(short_link=short_link)
            .annotate(clicks_count=models.Count("click"))
            .first()
        )

        if redirect is None:
            return None

        if redirect.is_deactivation_expired():
            redirect.delete()
            return None

        is_expired = redirect.is_expired()
        is_clicks_exceeded = redirect.is_clicks_exceeded(redirect.clicks_count)

        if redirect.is_active and (is_expired or is_clicks_exceeded):
            redirect.deactivate()
            redirect.save()

        return redirect


class Redirect(UserLinkModel):
    long_link = models.URLField(
        _("long_link"),
        help_text=_("resource_to_which_short_link_lead"),
        max_length=2000,
    )
    password = models.CharField(
        _("password"),
        help_text=_("password_that_will_requested_to_redirect"),
        max_length=128,
        blank=True,
        default="",
    )
    ip_address = models.GenericIPAddressField(
        _("ip_address"),
        help_text=_("client_ip_address_who_created_redirect"),
        default=None,
        null=True,
        blank=True,
    )

    objects = RedirectManager()

    class Meta:
        verbose_name = _("redirect")
        verbose_name_plural = _("redirects")

    def __str__(self) -> str:
        return _("redirect").capitalize()
