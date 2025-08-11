from django.urls import path

from home.views import *

from .views import *

urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("contactenos", ContactView.as_view(), name="contact"),
    path("precios", PricingView.as_view(), name="pricing"),
]
