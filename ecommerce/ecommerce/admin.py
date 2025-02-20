from django.contrib import admin
from .models import Category,Subcategory,Product,Review,Order,OrderItem

# Register your models here.
admin.site.register(Category)
admin.site.register(Subcategory)
admin.site.register(Product)
admin.site.register(Review)
admin.site.register(Order)
admin.site.register(OrderItem)