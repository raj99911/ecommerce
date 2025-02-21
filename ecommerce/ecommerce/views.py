from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework import viewsets, generics
from rest_framework.pagination import PageNumberPagination
from .models import Product, Review,Category,Subcategory,CartItem,Order,OrderItem,Wishlist,Coupon,ShippingAddress,ShippingCarrier
from rest_framework.permissions import IsAuthenticated, AllowAny,IsAdminUser
from .permissions import IsOwnerOrReadOnly
from .serializers import (ProductSerializer, ReviewSerializer, CategorySerializer, SubcategorySerializer,
                          WishlistSerializer,OrderSerializer, CartItemSerializer,CouponSerializer,ShippingAddressSerializer,
                          TrackOrderSerializer,UpdateOrderStatusSerializer,ShippingCarrierSerializer)
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import filters
from django.db import transaction
import stripe
from django.conf import settings
from django.urls import reverse
from decimal import Decimal
from utils.generate_tracking  import generate_custom_id

class ProductPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all().order_by('-created_at')
    serializer_class = ProductSerializer
    filter_backends = [filters.SearchFilter,filters.OrderingFilter]
    search_fields = ['name','category__name']
    ordering_fields = ['price', 'name','stock']
    pagination_class = ProductPagination
    permission_classes = [IsOwnerOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    # def get_permissions(self):
    #     if self.action in ["create", "update", "partial_update", "destroy"]:
    #         return [permissions.IsAdminUser()]
    #     return [permissions.AllowAny()]

# List all categories
class CategoryViewset(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['get'])
    def subcategories(self, request, pk=None):
        """Retrieve subcategories based on the parent category."""
        category = self.get_object()
        subcategories = Subcategory.objects.filter(category=category)
        serializer = SubcategorySerializer(subcategories, many=True)
        return Response(serializer.data)

# Retrieve subcategories for a given category
# class SubcategoryListView(viewsets.ModelViewSet):
#     serializer_class = SubcategorySerializer
#     permission_classes = [IsOwnerOrReadOnly]
#
#     def get_queryset(self):
#         category_id = self.kwargs['category_id']
#         return Subcategory.objects.filter(category_id=category_id)
#
# # Admin Category Management
# class CategoryManagementView(generics.ListCreateAPIView):
#     queryset = Category.objects.all()
#     serializer_class = CategorySerializer
#     permission_classes = [permissions.IsAdminUser]  # Only admin users can modify categories
#
# class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
#     queryset = Category.objects.all()
#     serializer_class = CategorySerializer
#     permission_classes = [permissions.IsAdminUser]
#
# class SubcategoryManagementView(generics.ListCreateAPIView):
#     queryset = Subcategory.objects.all()
#     serializer_class = SubcategorySerializer
#     permission_classes = [permissions.IsAdminUser]

class SubcategoryViewset(viewsets.ModelViewSet):
    queryset = Subcategory.objects.all()
    serializer_class = SubcategorySerializer
    permission_classes = [IsOwnerOrReadOnly]

    def get_queryset(self):
        """Filter subcategories by parent category if category ID is provided."""
        category_id = self.request.query_params.get('category')
        if category_id:
            return self.queryset.filter(category_id=category_id)
        return self.queryset

class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer

    def get_queryset(self):
        return Review.objects.filter(product_id=self.kwargs["product_pk"])

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class AddToCartView(APIView):
    # permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        product_id = request.data.get("product_id")
        quantity = int(request.data.get("quantity",1))

        product = Product.objects.get(id=product_id)

        cart_item, created = CartItem.objects.get_or_create(product_id=product_id,user=user,quantity=quantity)
        if not created:

            cart_item.quantity += quantity
            cart_item.save()

        return Response({"message": "Item added to cart"}, status=status.HTTP_201_CREATED)

class ViewCartView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cart = CartItem.objects.filter(user=request.user)
        serializer = CartItemSerializer(cart,many=True)
        return Response(serializer.data)

class UpdateCartView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, item_id):
        try:
            cart_item = CartItem.objects.get(id=item_id, cart__user=request.user)
            cart_item.quantity = request.data.get("quantity", cart_item.quantity)
            cart_item.save()
            return Response({"message": "Cart updated"}, status=status.HTTP_200_OK)
        except CartItem.DoesNotExist:
            return Response({"error": "Item not found"}, status=status.HTTP_404_NOT_FOUND)

class RemoveFromCartView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, item_id):
        try:
            cart_item = CartItem.objects.get(id=item_id, user=request.user)
            cart_item.delete()
            return Response({"message": "Item removed"}, status=status.HTTP_204_NO_CONTENT)
        except CartItem.DoesNotExist:
            return Response({"error": "Item not found"}, status=status.HTTP_404_NOT_FOUND)

class ClearCartView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        cart = CartItem.objects.filter(user=request.user)
        cart.all().delete()
        return Response({"message": "Cart cleared"}, status=status.HTTP_204_NO_CONTENT)




stripe.api_key = settings.STRIPE_SECRET_KEY  # Ensure this is set in settings.py

class CheckoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        cart_items = CartItem.objects.filter(user=user)

        if not cart_items.exists():
            return Response({"error": "Cart is empty"}, status=400)

        # Get coupon code from request data (if available)
        code = request.data.get("code", None)
        address_id = request.data.get("address_id", None)
        carrier_id = request.data.get("carrier_id", None)
        shipping_carrier = None
        address = None
        discount_applied = Decimal('0.00')
        coupon = None
        if address_id:
            address = get_object_or_404(ShippingAddress,id=address_id)
        else:
            return Response({"error": "Address is invalid"}, status=400)
        if carrier_id:
            shipping_carrier = get_object_or_404(ShippingCarrier,id=carrier_id)
            print(shipping_carrier)
        else:
            return Response({"error": "shipping_carrier is invalid"}, status=400)
        if code:
            # Validate coupon code
            coupon = get_object_or_404(Coupon, code=code, is_active=True)
            if not coupon.is_valid():
                return Response({"error": "Coupon expired or invalid"}, status=400)

            # Calculate the discount
            cart_total = sum(item.product.price * item.quantity for item in cart_items)
            if cart_total < coupon.min_order_value:
                return Response({"error": "Order total is too low for this coupon"}, status=400)

            discount_applied = coupon.discount_value
            if coupon.discount_type == "percent":
                discount_applied = (cart_total * coupon.discount_value) / Decimal('100')
                if coupon.max_discount:
                    discount_applied = min(discount_applied, coupon.max_discount)

            # Apply the discount to the total price
            total_price = cart_total - discount_applied
            print({"After Discount":total_price})
        else:
            total_price = sum(item.product.price * item.quantity for item in cart_items)
            print({"Without Discount": total_price})
        unit_amount = int(total_price*100)
        with transaction.atomic():
            # Create order
            # address = ShippingAddress.objects.filter(user=user).first()
            order = Order.objects.create(
                user=user,
                total_price=total_price,
                discount_applied=discount_applied,
                coupon=coupon if code else None,
                address = address,
                shipping_carrier = shipping_carrier
            )

            line_items = []
            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price=total_price
                )

                line_items.append({
                    "price_data": {
                        "currency": "inr",
                        "product_data": {
                            "name": item.product.name,
                        },
                        "unit_amount": unit_amount ,  # Convert to cents
                    },
                    "quantity": item.quantity,
                })

            # Create Stripe Checkout Session
            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=line_items,
                mode="payment",
                success_url=request.build_absolute_uri(reverse('payment-success')) + "?session_id={CHECKOUT_SESSION_ID}",
                cancel_url=request.build_absolute_uri(reverse('payment-cancel')),
                metadata={"order_id": order.id,"code":code}
            )
            order.session_id = session.id
            order.save()
            cart_items.delete()  # Clear cart after checkout

        return Response({"checkout_url": session.url, "order_id": order.id,"session_id":session.id}, status=201)
from django.shortcuts import render


# class PaymentSuccessAPIView(APIView):
#     permission_classes = [AllowAny]
#     def get(self, request):
#         order_id = request.query_params.get("order_id")
#         try:
#             order = Order.objects.get(id=order_id)
#
#             # Update order status to 'paid'
#             order.status = "paid"
#             order.save()
#
#             # Render the success page
#             return render(request, "success.html", {"order": order})
#
#         except Order.DoesNotExist:
#             return Response({"error": "Order not found"}, status=404)

class PaymentStatusAPIView(generics.UpdateAPIView):
    queryset = OrderItem.objects.all()
    permission_classes = [IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        session_id = request.query_params.get("session_id")
        if not session_id:
            return Response({"error": "Session ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            order = Order.objects.get(session_id=session_id, user=request.user)

        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

        # Retrieve Stripe session details
        session = stripe.checkout.Session.retrieve(session_id)
        order_id = session.metadata.get("order_id")
        if session.payment_status == "paid":
            # print(f"Before saving: {order.payment_status}, {order.status},{self.queryset.get(order_id=order_id)}")

            order.payment_status = "paid"
            order.payment_intent_id = session.payment_intent
            order.status = "processing"
            order_item = OrderItem.objects.filter(order_id=order_id).first()

            if order_item:
                order_item.payment_status = True  # Assuming payment_status is a BooleanField
                order_item.save()
                print("OrderItem updated successfully!")
            else:
                print(f"OrderItem for order_id={order_id} not found!")
            # self.queryset.payment_status = True
            # Ensure the status is in allowed choices
            # valid_statuses = [choice[0] for choice in Order.STATUS_CHOICES]
            # print(f"Valid statuses: {valid_statuses}")
            #
            #
            #
            # if order.status not in list(Order.STATUS_CHOICES):
            #     raise ValueError(f"Invalid status: {order.status}")
            order.save()
            # OrderItem.objects.get_or_create(order_id = order_id,payment_status=True)
            return Response({"message": "Payment successful, order is processing"}, status=status.HTTP_200_OK)

        return Response({"error": "Payment not completed"}, status=status.HTTP_400_BAD_REQUEST)

class PaymentCancelAPIView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        # Render the cancel page
        return render(request, "cancel.html")

class UserOrdersAPIView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('-created_at')

class OrderDetailAPIView(generics.RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

class CancelOrderAPIView(generics.UpdateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def update(self, request, *args, **kwargs):
        order = self.get_object()
        if order.status == "shipped":
            return Response({"message": "Order unable to cancel as it already shipped."}, status=status.HTTP_400_BAD_REQUEST)
        if order.status == "cancelled":
            return Response({"message": "Order was already cancelled."}, status=status.HTTP_400_BAD_REQUEST)
        if order.payment_intent_id:
            try:
                payment_intent = stripe.PaymentIntent.retrieve(order.payment_intent_id)

                if payment_intent.status == "succeeded":
                    stripe.Refund.create(payment_intent=order.payment_intent_id)
                    order.status = "cancelled"
                    order.payment_status = "refunded"
                    order.save()
            except stripe.error.StripeError as e:
                return  Response({'details':f'Stripe error: {str(e)}'},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response({"message": "Order cancelled successfully"}, status=status.HTTP_200_OK)

class Wishlist(viewsets.ModelViewSet):
    queryset = Wishlist.objects.all()
    serializer_class = WishlistSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination



class ApplyCouponView(APIView):
    def post(self, request):
        code = request.data.get("code")
        order_total = request.data.get("order_total")

        try:
            coupon = Coupon.objects.get(code=code, is_active=True)
            if not coupon.is_valid():
                return Response({"error": "Coupon expired or invalid"}, status=status.HTTP_400_BAD_REQUEST)

            if order_total < coupon.min_order_value:
                return Response({"error": "Order total is too low for this coupon"}, status=status.HTTP_400_BAD_REQUEST)

            discount = coupon.discount_value
            if coupon.discount_type == "percent":
                discount = (order_total * coupon.discount_value) / 100
                if coupon.max_discount:
                    discount = min(discount, coupon.max_discount)

            discounted_total = max(order_total - discount, 0)

            return Response(
                {
                    "message": "Coupon applied successfully",
                    "discount": float(discount),
                    "new_total": float(discounted_total),
                },
                status=status.HTTP_200_OK,
            )

        except Coupon.DoesNotExist:
            return Response({"error": "Invalid coupon code"}, status=status.HTTP_400_BAD_REQUEST)


class CouponViewSet(viewsets.ModelViewSet):
    queryset = Coupon.objects.all()
    serializer_class = CouponSerializer
    permission_classes = [IsAdminUser]  # Restrict access to admins

class AvailableCouponsView(generics.ListAPIView):
    queryset = Coupon.objects.filter(is_active=True)
    serializer_class = CouponSerializer

class ShippingAddressViewSet(viewsets.ModelViewSet):
    serializer_class = ShippingAddressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ShippingAddress.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

SHIPPING_METHODS = [
    {"id": 1, "name": "Standard Shipping", "price": 5.00, "delivery_time": "5-7 days"},
    {"id": 2, "name": "Express Shipping", "price": 10.00, "delivery_time": "2-3 days"},
    {"id": 3, "name": "Next-Day Delivery", "price": 20.00, "delivery_time": "1 day"},
]

class ShippingMethodsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(SHIPPING_METHODS)


class TrackOrderView(generics.RetrieveAPIView):
    serializer_class = TrackOrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def get(self, request, order_id):
        try:
            order = self.get_queryset().get(id=order_id)
            if not order.tracking_number:
                return Response({"message": "Tracking details not available yet."}, status=status.HTTP_400_BAD_REQUEST)
            return Response(self.get_serializer(order).data)
        except Order.DoesNotExist:
            return Response({"error": "Order not found."}, status=status.HTTP_404_NOT_FOUND)

class UpdateOrderStatusView(generics.UpdateAPIView):
    serializer_class = UpdateOrderStatusSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        return Order.objects.all()

    def patch(self, request, order_id):
        try:
            order = self.get_queryset().get(id=order_id)
            serializer = self.get_serializer(order, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                if serializer.data['status'] == "shipped":
                    tracking_no = generate_custom_id()
                    print(tracking_no)
                    # tr = self.get_queryset().(tracking_number)
                    order.tracking_number = tracking_no
                    order.save()
                return Response({"message": "Order status updated successfully."})

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Order.DoesNotExist:
            return Response({"error": "Order not found."}, status=status.HTTP_404_NOT_FOUND)

class ShippingCarrierViewset(viewsets.ModelViewSet):
    queryset = ShippingCarrier.objects.all()
    serializer_class = ShippingCarrierSerializer
    permission_classes = [IsAuthenticated]