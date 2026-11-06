__all__ = ()

from django.test import Client, TestCase
from django.urls import reverse
from rest_framework import status

from redirects.models import Redirect


class ApiCorrectTest(TestCase):
    fixtures = ["fixtures/for_test_data.json"]

    def setUp(self) -> None:
        self.username = "TestUser"
        self.password = "qscdewazx"
        self.client = Client()
        self.client.login(username=self.username, password=self.password)
        self.short_links = [
            "short_AAA",
            "short_BBB",
            "short_CCC",
            "short_DDD",
            "short_EEE",
            "short_FFF",
        ]
        self.full_redirect_fields = {
            Redirect.id.field.name,
            Redirect.long_link.field.name,
            Redirect.short_link.field.name,
            Redirect.password.field.name,
            Redirect.validity_days.field.name,
            Redirect.validity_clicks.field.name,
            Redirect.created_at.field.name,
            Redirect.updated_at.field.name,
            Redirect.create_method.field.name,
            Redirect.is_active.field.name,
            Redirect.deactivated_at.field.name,
        }
        self.simple_redirect_fields = {
            Redirect.long_link.field.name,
            Redirect.short_link.field.name,
            Redirect.password.field.name,
            Redirect.validity_days.field.name,
            Redirect.validity_clicks.field.name,
            Redirect.created_at.field.name,
            Redirect.updated_at.field.name,
        }

    def test_create_new_token_context(self) -> None:
        client = Client()

        response1 = client.post(
            reverse("api:create_new_token"),
            data={"username": self.username, "password": self.password},
        )
        self.assertEqual(response1.status_code, status.HTTP_200_OK)

        response2 = client.post(
            reverse("api:create_new_token"),
            data={"username": self.username, "password": self.password},
        )
        self.assertEqual(response2.status_code, status.HTTP_200_OK)

        self.assertNotEqual(
            response1.json()["token"],
            response2.json()["token"],
        )

    def test_get_token_context(self) -> None:
        response1 = Client().post(
            reverse("api:get_token"),
            data={"username": self.username, "password": self.password},
        )
        self.assertEqual(response1.status_code, status.HTTP_200_OK)

        response2 = Client().post(
            reverse("api:get_token"),
            data={"username": self.username, "password": self.password},
        )
        self.assertEqual(response2.status_code, status.HTTP_200_OK)

        self.assertEqual(response1.json()["token"], response2.json()["token"])

    def test_get_redirects_list(self) -> None:
        response = self.client.get(reverse("api:redirect-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(
            [
                redirect[Redirect.short_link.field.name]
                for redirect in response.json()
            ],
            self.short_links,
        )

    def test_get_redirects_list_context(self) -> None:
        response = self.client.get(reverse("api:redirect-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        for redirect in response.json():
            self.assertEqual(
                redirect.keys(),
                self.full_redirect_fields,
                "Отсутствует обязательное для авторизированного клиента поле",
            )

    def test_redirect_id(self) -> None:
        for i in range(1, len(self.short_links) + 1):
            response = self.client.get(
                reverse("api:redirect-detail", args=[i]),
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(
                response.json()[Redirect.short_link.field.name],
                self.short_links[i - 1],
            )

    def test_redirect_id_context(self) -> None:
        for i in range(1, len(self.short_links) + 1):
            response = self.client.get(
                reverse("api:redirect-detail", args=[i]),
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(
                response.json().keys(),
                self.full_redirect_fields,
                "Отсутствует обязательное для авторизированного клиента поле",
            )

    def test_create_redirect(self) -> None:
        redirect_count = Redirect.objects.count()

        response = self.client.post(
            reverse("api:redirect-list"),
            data={Redirect.long_link.field.name: "https://python.org/"},
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )
        self.assertEqual(
            response.json()[Redirect.long_link.field.name],
            "https://python.org/",
        )

        self.assertEqual(
            Redirect.objects.count(),
            redirect_count + 1,
            "Redirect не создан",
        )

        self.assertEqual(
            Redirect.objects.last().create_method,
            Redirect.CreateMethod.API,
            "Метод создания для `redirect` неправильный",
        )

        response = self.client.get(
            reverse(
                "redirects:redirect",
                args=[response.json()[Redirect.short_link.field.name]],
            ),
            follow=True,
        )
        self.assertRedirects(response, "https://python.org/")

    def test_create_redirect_context(self) -> None:
        response = Client().post(
            reverse("api:redirect-list"),
            data={Redirect.long_link.field.name: "https://python.org/"},
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            response.json().keys(),
            self.simple_redirect_fields,
            "Присутствуют лишние поля для не авторизированного пользователя",
        )

        token = (
            Client()
            .post(
                reverse("api:get_token"),
                data={"username": self.username, "password": self.password},
            )
            .json()["token"]
        )
        response = self.client.post(
            reverse("api:redirect-list"),
            data={
                "token": token,
                Redirect.long_link.field.name: "https://python.org/",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            response.json().keys(),
            self.full_redirect_fields,
            "Отсутствует обязательное для авторизированного пользователя поле",
        )

    def test_create_redirect_with_short_link(self) -> None:
        response = self.client.post(
            reverse("api:redirect-list"),
            data={
                Redirect.long_link.field.name: "https://python.org/",
                Redirect.short_link.field.name: "test_short",
            },
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )
        self.assertEqual(
            response.json()[Redirect.long_link.field.name],
            "https://python.org/",
        )
        self.assertEqual(
            response.json()[Redirect.short_link.field.name],
            "test_short",
        )

    def test_delete_redirect(self) -> None:
        redirect_count = Redirect.objects.count()

        response = self.client.delete(reverse("api:redirect-detail", args=[1]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertEqual(
            Redirect.objects.count(),
            redirect_count - 1,
            "Redirect не удалён",
        )
