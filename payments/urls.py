from django.urls import path

from payments.views import PromotionPurchaseView, PaymentSystemWebHookView

urlpatterns = [
    path("pay/", PromotionPurchaseView.as_view(), name="purchase-promotion"),
    path("hook/", PaymentSystemWebHookView.as_view(), name="payment-webhook"),
]
