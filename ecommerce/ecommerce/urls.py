from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (ProductViewSet, ReviewViewSet,CategoryViewset, SubcategoryViewset,AddToCartView,
                    ViewCartView, UpdateCartView, RemoveFromCartView, ClearCartView,CheckoutAPIView,
                    UserOrdersAPIView,OrderDetailAPIView,CancelOrderAPIView,Wishlist,PaymentCancelAPIView
                    ,CouponViewSet,ApplyCouponView,AvailableCouponsView,ShippingAddressViewSet,ShippingMethodsView,TrackOrderView,
                    UpdateOrderStatusView,PaymentStatusAPIView,ShippingCarrierViewset)

router = DefaultRouter()
router.register(r'products', ProductViewSet,basename="products")
router.register(r'reviews', ReviewViewSet,basename="reviews")
router.register(r'categories', CategoryViewset,basename="categories")
router.register(r'subcategories', SubcategoryViewset,basename="subcategories")
router.register(r'wishlist', Wishlist,basename="Wishlist")
router.register(r'admin/coupons', CouponViewSet, basename='coupon')
router.register(r'shipping-addresses', ShippingAddressViewSet, basename="shipping-address")
router.register(r'shipping-carrier', ShippingCarrierViewset, basename="shipping-carrier")



urlpatterns = [
    path('', include(router.urls)),
    # path('categories/', CategoryListView.as_view(), name='category-list'),
    # path('categories/<int:category_id>/subcategories/', SubcategoryListView.as_view(), name='subcategory-list'),
    #
    # # Admin Endpoints
    # path('admin/categories/', CategoryManagementView.as_view(), name='category-admin'),
    # path('admin/categories/<int:pk>/', CategoryDetailView.as_view(), name='category-detail'),
    # path('admin/subcategories/', SubcategoryManagementView.as_view(), name='subcategory-admin'),
    # path('admin/subcategories/<int:pk>/', SubcategoryDetailView.as_view(), name='subcategory-detail'),
    path('cart/add/', AddToCartView.as_view(), name='add-to-cart'),
    path('cart/', ViewCartView.as_view(), name='view-cart'),
    path('cart/update/<int:item_id>/', UpdateCartView.as_view(), name='update-cart'),
    path('cart/remove/<int:item_id>/', RemoveFromCartView.as_view(), name='remove-from-cart'),
    path('cart/clear/', ClearCartView.as_view(), name='clear-cart'),
    path("checkout/", CheckoutAPIView.as_view(), name="checkout"),
    path("orders/", UserOrdersAPIView.as_view(), name="user-orders"),
    path("orders/<int:pk>/", OrderDetailAPIView.as_view(), name="order-detail"),
    path("orders/<int:pk>/cancel/", CancelOrderAPIView.as_view(), name="cancel-order"),
    path('payment-success/', PaymentStatusAPIView.as_view(), name='payment-success'),
    path('payment-cancel/', PaymentCancelAPIView.as_view(), name='payment-cancel'),
    path('apply-coupon/', ApplyCouponView.as_view(), name="apply_coupon"),
    path('available-discounts/', AvailableCouponsView.as_view(), name="available_discounts"),
    path('shipping-methods/', ShippingMethodsView.as_view(), name='shipping-methods'),
    path('track-order/<int:order_id>/', TrackOrderView.as_view(), name='track-order'),
    path('update-order-status/<int:order_id>/', UpdateOrderStatusView.as_view(), name='update-order-status'),



]


