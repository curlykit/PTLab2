from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Product, Purchase

class ProductModelTest(TestCase):
    def setUp(self):
        self.product = Product.objects.create(
            name="Test Product",
            price=1000,
            quantity=5
        )
    
    def test_product_creation(self):
        """Тест создания продукта"""
        self.assertEqual(self.product.name, "Test Product")
        self.assertEqual(self.product.price, 1000)
        self.assertEqual(self.product.quantity, 5)
    
    def test_product_str_method(self):
        """Тест строкового представления продукта"""
        expected_str = "Test Product (5 шт.)"
        self.assertEqual(str(self.product), expected_str)
    
    def test_is_available_method(self):
        """Тест метода проверки доступности"""
        # Товар доступен
        self.assertTrue(self.product.is_available())
        
        # Товар недоступен
        self.product.quantity = 0
        self.assertFalse(self.product.is_available())

class PurchaseModelTest(TestCase):
    def setUp(self):
        self.product = Product.objects.create(
            name="Test Product",
            price=1000,
            quantity=3
        )
        self.purchase = Purchase.objects.create(
            product=self.product,
            person="John Doe",
            address="Test Address 123"
        )
    
    def test_purchase_creation(self):
        """Тест создания покупки"""
        self.assertEqual(self.purchase.person, "John Doe")
        self.assertEqual(self.purchase.address, "Test Address 123")
        self.assertEqual(self.purchase.product, self.product)
    
    def test_purchase_auto_date(self):
        """Тест автоматического добавления даты покупки"""
        self.assertIsNotNone(self.purchase.date)

class ViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.product = Product.objects.create(
            name="Test Product",
            price=1500,
            quantity=2
        )
        self.product_out_of_stock = Product.objects.create(
            name="Out of Stock Product",
            price=2000,
            quantity=0
        )
    
    def test_index_view(self):
        """Тест главной страницы"""
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shop/index.html')
        self.assertContains(response, "Test Product")
        self.assertContains(response, "1500")
    
    def test_buy_product_view_get(self):
        """Тест GET запроса к странице покупки"""
        response = self.client.get(reverse('buy', args=[self.product.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shop/purchase_form.html')
        self.assertContains(response, self.product.name)
    
    def test_buy_product_view_post_success(self):
        """Тест успешной покупки через POST"""
        initial_quantity = self.product.quantity
        
        response = self.client.post(reverse('buy', args=[self.product.id]), {
            'person': 'Test User',
            'address': 'Test Address'
        })
        
        # Обновляем продукт из базы
        self.product.refresh_from_db()
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Thank you for your purchase")
        self.assertEqual(self.product.quantity, initial_quantity - 1)
    
    def test_buy_product_view_out_of_stock(self):
        """Тест попытки купить недоступный товар"""
        response = self.client.post(reverse('buy', args=[self.product_out_of_stock.id]), {
            'person': 'Test User',
            'address': 'Test Address'
        })
        
        self.assertEqual(response.status_code, 403)
        self.assertIn(b"This product is out of stock", response.content)
    
    def test_buy_product_view_missing_fields(self):
        """Тест покупки с незаполненными полями"""
        response = self.client.post(reverse('buy', args=[self.product.id]), {
            'person': '',  # Пустое поле
            'address': 'Test Address'
        })
        
        self.assertEqual(response.status_code, 403)
        self.assertIn(b"Please fill in all fields", response.content)
    
    def test_buy_product_view_invalid_product(self):
        """Тест покупки несуществующего товара"""
        response = self.client.get(reverse('buy', args=[999]))  # Несуществующий ID
        self.assertEqual(response.status_code, 404)

class IntegrationTest(TestCase):
    """Интеграционные тесты"""
    
    def setUp(self):
        self.client = Client()
        self.product = Product.objects.create(
            name="Integration Test Product",
            price=1000,
            quantity=3
        )
    
    def test_full_purchase_flow(self):
        """Полный тест потока покупки"""
        # 1. Проверяем главную страницу
        response = self.client.get(reverse('index'))
        self.assertContains(response, "Integration Test Product")
        self.assertContains(response, "3 шт.")
        
        # 2. Переходим на страницу покупки
        response = self.client.get(reverse('buy', args=[self.product.id]))
        self.assertEqual(response.status_code, 200)
        
        # 3. Совершаем покупку
        response = self.client.post(reverse('buy', args=[self.product.id]), {
            'person': 'Integration Test User',
            'address': 'Integration Test Address'
        })
        
        # 4. Проверяем результат
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Thank you for your purchase")
        
        # 5. Проверяем что количество уменьшилось
        self.product.refresh_from_db()
        self.assertEqual(self.product.quantity, 2)
        
        # 6. Проверяем что покупка создалась в базе
        purchase = Purchase.objects.filter(product=self.product).first()
        self.assertIsNotNone(purchase)
        self.assertEqual(purchase.person, "Integration Test User")
    
    def test_multiple_purchases(self):
        """Тест нескольких покупок одного товара"""
        # Первая покупка
        self.client.post(reverse('buy', args=[self.product.id]), {
            'person': 'User 1',
            'address': 'Address 1'
        })
        self.product.refresh_from_db()
        self.assertEqual(self.product.quantity, 2)
        
        # Вторая покупка
        self.client.post(reverse('buy', args=[self.product.id]), {
            'person': 'User 2',
            'address': 'Address 2'
        })
        self.product.refresh_from_db()
        self.assertEqual(self.product.quantity, 1)
        
        # Третья покупка
        self.client.post(reverse('buy', args=[self.product.id]), {
            'person': 'User 3',
            'address': 'Address 3'
        })
        self.product.refresh_from_db()
        self.assertEqual(self.product.quantity, 0)
        
        # Четвертая покупка (должна fail)
        response = self.client.post(reverse('buy', args=[self.product.id]), {
            'person': 'User 4',
            'address': 'Address 4'
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"This product is out of stock", response.content)