from django.shortcuts import render, get_object_or_404  # ← ДОБАВИТЬ ЭТО
from django.http import HttpResponse
from django.views.generic.edit import CreateView

from .models import Product, Purchase


# Create your views here.
def index(request):
    products = Product.objects.all()
    context = {'products': products}
    return render(request, 'shop/index.html', context)


class PurchaseCreate(CreateView):
    model = Purchase
    fields = ['product', 'person', 'address']

    def form_valid(self, form):
        self.object = form.save()
        return HttpResponse(f'Спасибо за покупку, {self.object.person}!')

def buy_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    # Проверяем наличие товара
    if product.quantity <= 0:
        return HttpResponse("Этот товар закончился!", status=400)
    
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
            return HttpResponse("Заполните все поля!", status=400)
        
        # Уменьшаем количество товара
        product.quantity -= 1
        product.save()
        
        # Создаем запись о покупке
        Purchase.objects.create(
            product=product,
            person=person,
            address=address
        )
        
        return HttpResponse(f"Спасибо за покупку, {person}! Товар '{product.name}' отправлен по адресу: {address}. Осталось: {product.quantity} шт.")