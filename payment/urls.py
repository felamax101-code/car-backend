from django.urls import path

from .views import PayView

urlpatterns = [
    path("<int:payment_id>/pay/", PayView.as_view(), name="payment-pay"),
]