__all__ = ("BlockedDomain",)

import re

from antispam_link_shorteners import is_link_shortener
from django.db import models
from django.utils.translation import gettext_lazy as _

from core.models import TimeStampedModel


class BlockedDomainManager(models.Manager):
    def upgrade_regex(self, domain_regex: str) -> str:
        if domain_regex.startswith("|||"):
            domain_regex = r"http[s]?://(#\.)+" + domain_regex[3:]

        if domain_regex.startswith("||"):
            domain_regex = r"http[s]?://(#\.)?" + domain_regex[2:]

        if domain_regex.startswith("|"):
            domain_regex = r"http[s]?://" + domain_regex[1:]

        if "^" in domain_regex:
            domain_regex = domain_regex.replace("^", r"\.#")

        if "#" in domain_regex:
            domain_regex = domain_regex.replace("#", r".*")

        return domain_regex

    def is_blocked(self, url: str) -> bool:
        if is_link_shortener(url):
            return True
        for domain in self.all():
            if re.fullmatch(self.upgrade_regex(domain.domain_regex), url):
                return True
        return False


class BlockedDomain(TimeStampedModel):
    domain_regex = models.CharField(
        _("domain_regex"),
        help_text=_("domain_regex_that_will_be_prohibited_from_shortening"),
        max_length=255,
    )

    objects = BlockedDomainManager()

    class Meta:
        verbose_name = _("domain_regex")
        verbose_name_plural = _("domains_regex")

    def __str__(self) -> str:
        return _("domain_regex").capitalize()
