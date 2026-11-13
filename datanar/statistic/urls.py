from django.urls import path, register_converter

from statistic import views
from statistic.converters import PeriodConverter

register_converter(PeriodConverter, "period_enum")

app_name = "statistic"

urlpatterns = [
    path(
        "download/<link>/<period_enum:period>/",
        views.DownloadStatistic.as_view(),
        name="download",
    ),
    path("my_links/", views.MyLinksView.as_view(), name="my_links"),
    path(
        "links/<link>/<period_enum:period>/",
        views.LinkDetailView.as_view(),
        name="link_detail",
    ),
]
