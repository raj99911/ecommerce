# from django.urls import path
# from .views import InitiatePaymentView, PaymentStatusView, stripe_webhook,home, create_checkout_session, success, cancel

# urlpatterns = [
#     path('payment/initiate/', InitiatePaymentView.as_view(), name='initiate-payment'),
#     path('payment/status/', PaymentStatusView.as_view(), name='payment-status'),
#     path('payment/webhook/', stripe_webhook, name='stripe-webhook'),
#     path('', home, name="home"),
#     path('create-checkout-session/', create_checkout_session, name="create_checkout_session"),
#     path('success/', success, name="success"),
#     path('cancel/', cancel, name="cancel"),
# ]
from django.urls import path
# from .views import (initiate_payment,payment_success, payment_cancel)
# from .views import (payment_status)

# urlpatterns = [
#     # path('initiate/', initiate_payment, name='initiate_payment'),
#     #  path('status/<str:session_id>/', payment_status, name='payment_status'),
#     # path('success/', payment_success, name='payment_success'),
#     # path('cancel/', payment_cancel, name='payment_cancel'),
#
#
# ]
# from django.urls import path
# from .views import InitiatePaymentAPIView, PaymentStatusAPIView,ConfirmPaymentAPIView,ChargePaymentAPIView
#
# urlpatterns = [
#     path('initiate-payment/<int:order_id>/', InitiatePaymentAPIView.as_view(), name='initiate-payment'),
#     path('status/<str:session_id>/', PaymentStatusAPIView.as_view(), name='payment-status'),
#     path('confirm-payment/<int:payment_id>/', ConfirmPaymentAPIView.as_view(), name='ConfirmPaymentAPIView'),
#     path('charge-payment/<int:order_id>/', ChargePaymentAPIView.as_view(), name='ChargePaymentAPIView'),
# ]
