from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (ProductViewSet, ReviewViewSet,CategoryViewset, SubcategoryViewset,AddToCartView,
                    ViewCartView, UpdateCartView, RemoveFromCartView, ClearCartView,CheckoutAPIView,
                    UserOrdersAPIView,OrderDetailAPIView,CancelOrderAPIView)

router = DefaultRouter()
router.register(r'products', ProductViewSet,basename="products")
router.register(r'reviews', ReviewViewSet,basename="reviews")
router.register(r'categories', CategoryViewset,basename="categories")
router.register(r'subcategories', SubcategoryViewset,basename="subcategories")



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
]


