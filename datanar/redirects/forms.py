__all__ = ("PasswordForm", "RedirectForm", "RedirectFormExtended")

from typing import Any

from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.text import capfirst
from django.utils.translation import gettext_lazy as _

from core.forms import BootstrapFormMixin
from core.widgets import DatePickerInput
from dashboard.models import BlockedDomain
from redirects.models import Redirect
from redirects.utils import generate_short_link


class RedirectForm(BootstrapFormMixin, forms.ModelForm):
    short_link = forms.SlugField(
        label=_("custom_url"),
        help_text=_("custom_url_that_would_like_have_instead_generated_one"),
        max_length=50,
        allow_unicode=True,
        required=False,
    )

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.fields[Redirect.short_link.field.name].required = False

        for i, field in enumerate(self.fields.values()):
            if field.help_text:
                field.widget.attrs["placeholder"] = field.help_text
            if i > 0:
                field.widget.attrs["class"] += " mb-2"

    class Meta:
        model = Redirect

        fields = [
            Redirect.long_link.field.name,
        ]

    def clean(self) -> dict[str, Any]:
        cleaned_data = super().clean()
        if self.errors:
            return cleaned_data

        long_link_value: str | None = cleaned_data.get(
            Redirect.long_link.field.name,
        )
        custom_url_value: str | None = cleaned_data.get(
            Redirect.short_link.field.name,
        )
        if not custom_url_value and long_link_value:
            cleaned_data[Redirect.short_link.field.name] = (
                generate_short_link()
            )
        else:
            if "/" in custom_url_value:
                self.add_error(
                    Redirect.short_link.field.name,
                    ValidationError(_("custom_url_should_not_have_slash")),
                )
            if Redirect.objects.get_by_short_link(custom_url_value):
                self.add_error(
                    Redirect.short_link.field.name,
                    ValidationError(_("custom_url_already_use")),
                )

        if long_link_value and BlockedDomain.objects.is_blocked(
            long_link_value,
        ):
            self.add_error(
                Redirect.long_link.field.name,
                ValidationError(_("this_url_is_blocked")),
            )
        return cleaned_data


class RedirectFormExtended(RedirectForm):
    links_file = forms.FileField(required=False)

    validity_days = forms.DateField(
        label=capfirst(Redirect.validity_days.field.verbose_name),
        help_text=Redirect.validity_days.field.help_text,
        widget=DatePickerInput(),
        required=False,
    )

    field_order = [
        Redirect.long_link.field.name,
        Redirect.short_link.field.name,
        Redirect.password.field.name,
        Redirect.validity_days.field.name,
        Redirect.validity_clicks.field.name,
        "links_file",
    ]

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        self.fields["links_file"].widget.attrs["class"] = "d-none"
        self.fields["links_file"].widget.attrs["accept"] = ".txt, .xlsx"

    def clean(self) -> dict[str, Any]:
        cleaned_data = super().clean()
        if self.errors:
            return cleaned_data

        date = cleaned_data.get(Redirect.validity_days.field.name)
        if date is None:
            cleaned_data[Redirect.validity_days.field.name] = None
            return cleaned_data

        delta = (
            cleaned_data[Redirect.validity_days.field.name]
            - timezone.now().date()
        )

        if delta.days < 0:
            self.add_error(
                Redirect.validity_days.field.name,
                _("date_validity_invalid"),
            )
        else:
            cleaned_data[Redirect.validity_days.field.name] = delta.days

        return cleaned_data

    class Meta(RedirectForm.Meta):
        fields = [
            Redirect.long_link.field.name,
            Redirect.password.field.name,
            Redirect.validity_clicks.field.name,
        ]


class PasswordForm(BootstrapFormMixin, forms.Form):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs.update({"placeholder": field.help_text})

    password = forms.CharField(
        label=_("Password"),
        help_text=_("password_before_redirect"),
    )
