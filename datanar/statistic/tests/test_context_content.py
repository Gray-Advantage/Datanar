__all__ = ()

from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse

from redirects.models import Redirect


class ContextContentTest(TestCase):
    fixtures = ["fixtures/for_test_data.json"]

    def test_my_links_context(self) -> None:
        client = Client()
        client.login(username="TestUser", password="qscdewazx")

        url = reverse("statistic:my_links")
        response = client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

        response_links = response.context["links"].values_list(
            Redirect.short_link.field.name,
            flat=True,
        )
        self.assertQuerySetEqual(
            response_links,
            [
                "short_FFF",
                "short_EEE",
                "short_DDD",
                "short_CCC",
                "short_BBB",
                "short_AAA",
            ],
        )
