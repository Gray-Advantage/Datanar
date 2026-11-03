__all__ = ()

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("", include("homepage.urls")),
    path("admin/", admin.site.urls),
    path("api/", include("api.urls")),
    path("auth/", include("users.urls")),
    path("auth/", include("allauth.urls")),
    path("dashboard/", include("dashboard.urls")),
    path("i18n/", include("django.conf.urls.i18n")),
    path("qr_code/", include("qr_codes.urls")),
    path("statistics/", include("statistic.urls")),
    path("tz_detect/", include("tz_detect.urls")),
    path("", include("redirects.urls")),
]

handler500 = "core.views.server_error"

if settings.DEBUG and not settings.TEST:
    import debug_toolbar

    urlpatterns.append(path("__debug__/", include(debug_toolbar.urls)))
    urlpatterns.append(
        *static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT),
    )
