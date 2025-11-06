from django.contrib import admin
from .models import Product, Purchase  # Импортируем модель Product

# Регистрируем модель Product в админке
admin.site.register(Product)
admin.site.register(Purchase)