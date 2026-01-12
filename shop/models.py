# shop/models.py
from django.db import models


class Product(models.Model):
    # =========== СУЩЕСТВУЮЩИЕ ПОЛЯ ===========
    name = models.CharField("ФИО сотрудника", max_length=100)
    price = models.DecimalField("Оклад", max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField("Стаж (лет)", default=1)
    
    # =========== НОВЫЕ ПОЛЯ ===========
    position = models.CharField(
        "Должность",
        max_length=100,
        blank=True,
        null=True,
        help_text="Например: Разработчик, Менеджер, Аналитик"
    )
    
    EMPLOYEE_TYPES = [
        ('JUNIOR', 'Junior (стаж < 2 лет)'),
        ('MIDDLE', 'Middle (стаж 2-5 лет)'),
        ('SENIOR', 'Senior (стаж > 5 лет)'),
        ('LEAD', 'Team Lead'),
        ('MANAGER', 'Менеджер'),
        ('OTHER', 'Другое'),
    ]
    
    employee_type = models.CharField(
        "Уровень сотрудника",
        max_length=20,
        choices=EMPLOYEE_TYPES,
        blank=True,
        null=True,
        help_text="Выберите уровень или оставьте пустым для автоопределения"
    )
    
    # =========== СВОЙСТВА ДЛЯ ОБРАТНОЙ СОВМЕСТИМОСТИ ===========
    @property
    def employee_name(self):
        """ФИО сотрудника"""
        return self.name
    
    @property
    def base_salary(self):
        """Оклад"""
        return self.price
    
    @property
    def years_of_service(self):
        """Стаж работы"""
        return self.quantity
    
    @property
    def calculated_position(self):
        """Должность: либо заданная, либо генерируемая"""
        if self.position:
            return self.position
        if self.name and ' ' in self.name:
            return f"Специалист {self.name.split()[0]}"
        return "Специалист"
    
    @property
    def calculated_employee_type(self):
        """Тип сотрудника: либо заданный, либо автоопределяемый"""
        if self.employee_type:
            for code, name in self.EMPLOYEE_TYPES:
                if code == self.employee_type:
                    return name.split(' (')[0]
        
        if self.quantity < 2:
            return "Junior"
        elif self.quantity < 5:
            return "Middle"
        else:
            return "Senior"
    
    # =========== МЕТОДЫ ===========
    def save(self, *args, **kwargs):
        """Автозаполнение полей при сохранении"""
        if not self.position:
            self.position = "Специалист"
        
        if not self.employee_type:
            if self.quantity < 2:
                self.employee_type = 'JUNIOR'
            elif self.quantity < 5:
                self.employee_type = 'MIDDLE'
            else:
                self.employee_type = 'SENIOR'
        
        super().save(*args, **kwargs)
    
    def calculate_salary(self, bonus=0, deductions=0):
        """Расчет итоговой зарплаты с премией и удержаниями"""
        return float(self.price) + float(bonus) - float(deductions)
    
    def __str__(self):
        if self.position:
            return f"{self.name} - {self.position}"
        return f"{self.name}"


class Purchase(models.Model):
    # =========== НАСТРОЙКИ ВЫПЛАТ ===========
    PAYMENT_TYPES = [
        ('SALARY', 'Зарплата'),
        ('BONUS', 'Премия'),
        ('ADVANCE', 'Аванс'),
        ('VACATION', 'Отпускные'),
        ('SICK_LEAVE', 'Больничный'),
        ('MATERNITY', 'Декретные'),
        ('OTHER', 'Другое'),
    ]
    
    # =========== ПОЛЯ ===========
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE, 
        verbose_name="Сотрудник"
    )
    person = models.CharField(
        "Сумма премии", 
        max_length=200, 
        help_text="Введите сумму премии в рублях"
    )
    address = models.CharField(
        "Описание выплаты", 
        max_length=200, 
        help_text="Например: Зарплата за январь, Премия за проект"
    )
    date = models.DateTimeField("Дата выплаты", auto_now_add=True)
    
    payment_type = models.CharField(
        "Тип выплаты",
        max_length=20,
        choices=PAYMENT_TYPES,
        default='SALARY',
        blank=True,
        null=True,
    )
    
    # =========== МЕТОДЫ ===========
    def get_bonus(self):
        """Получить сумму премии как число"""
        try:
            return float(self.person)
        except (ValueError, TypeError):
            return 0.0
    
    def get_payment_type_display_name(self):
        """Получить читаемое название типа выплаты"""
        if self.payment_type:
            for code, name in self.PAYMENT_TYPES:
                if code == self.payment_type:
                    return name
        return "Зарплата"
    
    def calculate_final_salary(self):
        """Рассчитать итоговую зарплату с учетом премии"""
        try:
            base = float(self.product.price)
            bonus = self.get_bonus()
            return base + bonus
        except (AttributeError, ValueError):
            return 0.0
    
    # =========== СВОЙСТВА ДЛЯ ОБРАТНОЙ СОВМЕСТИМОСТИ ===========
    @property
    def bonus(self):
        """Свойство для обратной совместимости"""
        return self.get_bonus()
    
    @property
    def description(self):
        """Свойство для обратной совместимости"""
        return self.address
    
    @property
    def calculated_payment_type(self):
        """Свойство для обратной совместимости"""
        return self.get_payment_type_display_name()
    
    @property
    def final_salary(self):
        """Свойство для обратной совместимости"""
        return self.calculate_final_salary()
    
    @property
    def employee(self):
        """Свойство для обратной совместимости"""
        return self.product
    
    def __str__(self):
        """Строковое представление"""
        try:
            payment_type = self.get_payment_type_display_name()
            employee_name = self.product.name
            final_salary = self.calculate_final_salary()
            date_str = self.date.strftime('%d.%m.%Y') if self.date else 'н/д'
            return f"{payment_type}: {employee_name} - {final_salary:.2f} руб. ({date_str})"
        except AttributeError:
            return "Выплата зарплаты"