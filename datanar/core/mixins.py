__all__ = (
    "FormMethodExtender",
    "RedirectToLastPageMixin",
    "StaffUserRequiredMixin",
)

from typing import Any, TYPE_CHECKING

from django.contrib.auth.mixins import AccessMixin
from django.http import (
    Http404,
    HttpRequest,
    HttpResponse,
    HttpResponseBase,
    HttpResponseRedirect,
)
from django.views.generic import View

if TYPE_CHECKING:
    from django.db.models import QuerySet


class RedirectToLastPageMixin:
    class SpecialEmptyPageError(Exception):
        pass

    def paginate_queryset(
        self,
        queryset: "QuerySet",
        page_size: int,
    ) -> tuple:
        try:
            return super().paginate_queryset(queryset, page_size)
        except Http404 as e:
            page = (
                self.kwargs.get(self.page_kwarg)
                or self.request.GET.get(self.page_kwarg)
                or "1"
            )
            if page.isdigit():
                raise self.SpecialEmptyPageError from e
            raise e from e

    def get(
        self,
        request: HttpRequest,
        *args: Any,
        **kwargs: Any,
    ) -> HttpResponse:
        try:
            return super().get(request, *args, **kwargs)
        except self.SpecialEmptyPageError:
            query_params = request.GET.copy()

            queryset = self.get_queryset()
            page_size = self.get_paginate_by(queryset)
            paginator = self.get_paginator(queryset, page_size)

            query_params[self.page_kwarg] = paginator.num_pages

            return HttpResponseRedirect(
                f"{request.path}?{query_params.urlencode()}",
            )


class FormMethodExtender(View):
    def post(
        self,
        request: HttpRequest,
        *args: Any,
        **kwargs: Any,
    ) -> "HttpResponseBase":
        method = request.POST.get("_method", "")
        if method.upper() in ("DELETE", "PATCH", "PUT"):
            request.method = method
            return super().dispatch(request, *args, **kwargs)
        return super().post(request, *args, **kwargs)


class StaffUserRequiredMixin(AccessMixin):
    def dispatch(
        self,
        request: HttpRequest,
        *args: Any,
        **kwargs: Any,
    ) -> "HttpResponseBase":
        if not request.user.is_staff:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)
