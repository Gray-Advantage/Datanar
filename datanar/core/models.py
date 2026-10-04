__all__ = ("TimeStampedModel", "UserLinkModel", "UserStampedModel")

from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(
        _("Creation time"),
        help_text=_("When the object was created."),
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        _("Update time"),
        help_text=_("When the object was last updated."),
        auto_now=True,
    )

    class Meta:
        abstract = True


class UserStampedModel(TimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name=_("user"),
        help_text=_("user_who_create_bond"),
        null=True,
    )

    class CreateMethod(models.TextChoices):
        API = "API", _("API")
        WEB = "WEB", _("Web")
        WEB_FILE = "WEB+FILE", _("Web (file)")

    create_method = models.CharField(
        _("create_method"),
        help_text=_("method_which_redirect_was_created"),
        max_length=20,
        choices=CreateMethod.choices,
        default=CreateMethod.WEB,
    )

    class Meta:
        abstract = True


class UserLinkModel(UserStampedModel):
    short_link = models.SlugField(
        _("short_link"),
        help_text=_("shorten_link_to_redirect_to_resource"),
        max_length=50,
        unique=True,
        allow_unicode=True,
    )
    validity_days = models.PositiveIntegerField(
        _("valid_day_number"),
        help_text=_("how_many_day_link_will_be_valid"),
        default=90,
        null=True,
        blank=True,
    )
    validity_clicks = models.PositiveIntegerField(
        _("valid_click_number"),
        help_text=_("how_many_click_on_link_will_be_valid"),
        default=None,
        null=True,
        blank=True,
    )
    is_active = models.BooleanField(
        _("active"),
        help_text=_("is_active"),
        default=True,
    )
    deactivated_at = models.DateTimeField(
        _("deactivation_time"),
        help_text=_("when_bond_was_deactivated"),
        default=None,
        null=True,
        blank=True,
    )

    class Meta:
        abstract = True

    def is_clicks_exceeded(self, clicks_count: int) -> bool:
        if not self.validity_clicks:
            return False
        return clicks_count >= self.validity_clicks

    def is_expired(self) -> bool:
        if not self.validity_days:
            return False
        return (
            self.created_at + timedelta(days=self.validity_days)
            < timezone.now()
        )

    def is_deactivation_expired(self) -> bool:
        if self.is_active or self.deactivated_at is None:
            return False
        return (self.deactivated_at + timedelta(days=10)) < timezone.now()

    def reactivate(self) -> None:
        self.is_active = True
        self.deactivated_at = None

    def deactivate(self) -> None:
        self.is_active = False
        self.deactivated_at = timezone.now()
