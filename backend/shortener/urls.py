from django.urls import path

from .views import RedirectView, ShortURLDetailsView, ShortURLListView, QRCodeView

urlpatterns = [
    path("", ShortURLListView.as_view(), name="shorturl-list"),
    path("<int:pk>/", ShortURLDetailsView.as_view(), name="shorturl-detail"),
    path("<int:pk>/qr/", QRCodeView.as_view(), name="shorturl-qr")
]