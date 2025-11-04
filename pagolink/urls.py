from django.contrib import admin
from django.urls import path, include
from dashboard.views import LinkPaymentView, LinkPaymentCardView, LinkPaymentProcess
from pagolink import settings

urlpatterns = [
    path("", include("home.urls")),
    path("admin/", include("dashboard.urls")),
    path("pagoseguro/<int:pk>", LinkPaymentView.as_view(), name="link_pay"),
    path(
        "pagoseguro/pagar/<int:pk>", LinkPaymentCardView.as_view(), name="link_pay_card"
    ),
    path(
        "pagoseguro/procesar/<int:pk>",
        LinkPaymentProcess.as_view(),
        name="link_pay_process",
    ),
    path("core/", admin.site.urls),
]

if settings.DEBUG:
    from django.conf.urls.static import static

    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
