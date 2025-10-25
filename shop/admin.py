from django.contrib import admin
from .models import Product  # Импортируем модель Product

# Регистрируем модель Product в админке
admin.site.register(Product)