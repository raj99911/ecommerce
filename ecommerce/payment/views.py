
import stripe
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework import status
from ecommerce.models import Order
from rest_framework.renderers import TemplateHTMLRenderer
from django.shortcuts import render



# class PaymentStatusView(APIView):
#     permission_classes = [IsAuthenticated]
#
#     def get(self, request):
#         stripe.api_key = settings.STRIPE_SECRET_KEY
#         session_id = request.query_params.get("session_id")
#
#         if not session_id:
#             return Response({"error": "Session ID is required"}, status=status.HTTP_400_BAD_REQUEST)
#
#         try:
#             session = stripe.checkout.Session.retrieve(session_id)
#             return Response({"status": session.payment_status}, status=status.HTTP_200_OK)
#
#         except stripe.error.StripeError as e:
#             return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class PaymentStatusView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, session_id):
        try:
            session = stripe.checkout.Session.retrieve(session_id)
            return Response({"payment_status": session.payment_status}, status=200)
        except Exception as e:
            return Response({"error": str(e)}, status=400)