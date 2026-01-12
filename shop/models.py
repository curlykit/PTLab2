from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    
    # =========== СТАРЫЕ МЕТОДЫ (магазин) ===========
    def is_available(self):
        return self.quantity > 0
    
    def __str__(self):
        return f"{self.name} ({self.quantity} шт.)"
    
    # =========== НОВЫЕ СВОЙСТВА (сотрудники) ===========
    @property
    def position(self):
        """Должность сотрудника (используем поле name)"""
        return self.name  # name → должность
    
    @property
    def base_salary(self):
        """Оклад сотрудника (используем поле price)"""
        return self.price  # price → оклад
    
    @property
    def years_of_service(self):
        """Стаж работы (используем quantity)"""
        return self.quantity  # quantity → стаж
    
    @property
    def employee_type(self):
        """Тип сотрудника на основе стажа"""
        if self.years_of_service < 2:
            return "Junior"
        elif self.years_of_service < 5:
            return "Middle"
        else:
            return "Senior"
    
    # =========== АНАЛИТИКА ===========
    def calculate_salary(self, bonus=0, deductions=0):
        """Расчет итоговой зарплаты с премией и удержаниями"""
        return float(self.base_salary) + float(bonus) - float(deductions)
    
    def __str__(self):
        # Два варианта отображения
        return f"{self.name} ({self.position}) - {self.base_salary} руб."


class Purchase(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    person = models.CharField(max_length=200)
    address = models.CharField(max_length=200)
    date = models.DateTimeField(auto_now_add=True)
    
    # =========== СТАРЫЕ МЕТОДЫ (покупки) ===========
    def __str__(self):
        return f"{self.person} купил {self.product.name}"
    
    # =========== НОВЫЕ СВОЙСТВА (выплаты) ===========
    @property
    def employee(self):
        """Сотрудник (бывший product)"""
        return self.product  # product → employee
    
    @property
    def month(self):
        """Месяц выплаты (используем date)"""
        return self.date
    
    @property
    def bonus(self):
        """Премия (используем person - храним как строку)"""
        try:
            return float(self.person)  # Если person это число (премия)
        except:
            return 0.0  # Если не число, значит это имя получателя
    
    @property
    def final_salary(self):
        """Итоговая зарплата"""
        base = float(self.employee.base_salary)
        bonus = float(self.bonus)
        return base + bonus
    
    @property
    def payment_date(self):
        """Дата выплаты"""
        return self.date
    
    def __str__(self):
        # Два варианта отображения
        return f"Выплата {self.employee.name}: {self.final_salary} руб. ({self.date})"