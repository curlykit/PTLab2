from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt  # ← ДОБАВЬТЕ ЭТУ СТРОКУ
from .models import Product, Purchase

def index(request):
    """Главная страница со списком товаров"""
    products = Product.objects.all()
    return render(request, 'shop/index.html', {'products': products})

@csrf_exempt
def buy_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if product.quantity <= 0:
        return HttpResponse("This product is out of stock", status=403)
    
    # Если GET запрос - показываем форму
    if request.method == 'GET':
        return render(request, 'shop/purchase_form.html', {
            'product': product
        })
    
    # Если POST запрос - обрабатываем покупку
    elif request.method == 'POST':
        person = request.POST.get('person')
        address = request.POST.get('address')
        
        if not person or not address:
            return HttpResponse("Please fill in all fields", status=403)
        
        # Уменьшаем количество товара
        product.quantity -= 1
        product.save()
        
        # Создаем запись о покупке
        Purchase.objects.create(
            product=product,
            person=person,
            address=address
        )
        
        return HttpResponse(f"Thank you for your purchase, {person}! Product '{product.name}' will be shipped to: {address}. Remaining: {product.quantity} pcs.")