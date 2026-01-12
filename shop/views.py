from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Product, Purchase

# =========== НОВЫЙ ИМПОРТ ДЛЯ АНАЛИТИКИ ===========
import pandas as pd
import numpy as np
from django.db.models import Sum, Avg, Max, Min

def index(request):
    """Главная страница со списком СОТРУДНИКОВ"""
    employees = Product.objects.all()
    
    # =========== АНАЛИТИКА ЗАРПЛАТ ===========
    salaries = [float(emp.price) for emp in employees]  # Используем price (оклад)
    
    if salaries:
        # Рассчитываем медиану без numpy для надежности
        sorted_salaries = sorted(salaries)
        n = len(sorted_salaries)
        if n % 2 == 0:
            median_salary = (sorted_salaries[n//2 - 1] + sorted_salaries[n//2]) / 2
        else:
            median_salary = sorted_salaries[n//2]
        
        # Подсчёт типов сотрудников ТОЛЬКО по явно заданному полю employee_type
        junior_count = 0
        middle_count = 0
        senior_count = 0
        lead_count = 0
        manager_count = 0
        other_count = 0
        
        for emp in employees:
            # Смотрим ТОЛЬКО явно заданный тип в БД (employee_type)
            emp_type = emp.employee_type  # Это поле: 'JUNIOR', 'MIDDLE', 'SENIOR' и т.д.
            
            if emp_type == 'JUNIOR':
                junior_count += 1
            elif emp_type == 'MIDDLE':
                middle_count += 1
            elif emp_type == 'SENIOR':
                senior_count += 1
            elif emp_type == 'LEAD':
                lead_count += 1
            elif emp_type == 'MANAGER':
                manager_count += 1
            elif emp_type == 'OTHER':
                other_count += 1
            # Если employee_type пустое или None - не считаем!
        
        analytics = {
            'total_salary_fund': sum(salaries),  # Сумма всех окладов
            'average_salary': sum(salaries) / len(salaries),  # Средняя зарплата
            'median_salary': median_salary,  # Медианная зарплата (без numpy)
            'max_salary': max(salaries),  # Максимальная зарплата
            'min_salary': min(salaries),  # Минимальная зарплата
            'employee_count': len(employees),
            'junior_count': junior_count,
            'middle_count': middle_count,  # Добавили middle_count
            'senior_count': senior_count,
            'lead_count': lead_count,
            'manager_count': manager_count,
            'other_count': other_count,
        }
    else:
        analytics = {}
    
    return render(request, 'shop/index.html', {
        'employees': employees,
        'analytics': analytics
    })

@csrf_exempt
def process_payment(request, employee_id):  # Переименовано buy_product → process_payment
    """Обработка выплаты зарплаты сотруднику (было покупки товара)"""
    employee = get_object_or_404(Product, id=employee_id)  # Переименовано product → employee
    
    print(f"=== DEBUG ===")
    print(f"Employee: {employee.name}, Position: {employee.position}")
    print(f"Base Salary: {employee.base_salary}, Years: {employee.years_of_service}")
    print(f"Method: {request.method}")
    
    # Убрали проверку quantity <= 0 (теперь это стаж, он всегда > 0)
    # Было: if product.quantity <= 0:
    # Стало: не нужно
    
    if request.method == 'GET':
        # Показываем форму расчета зарплаты
        return render(request, 'shop/payment_form.html', {  # Изменили шаблон
            'employee': employee  # Было 'product'
        })
    
    elif request.method == 'POST':
        # Получаем данные для расчета зарплаты
        bonus_str = request.POST.get('bonus', '0')  # Было 'person'
        deductions_str = request.POST.get('deductions', '0')  # Было 'address'
        description = request.POST.get('description', '')  # Новое поле
        
        print(f"Bonus: {bonus_str}, Deductions: {deductions_str}")
        
        # Валидация
        try:
            bonus = float(bonus_str)
            deductions = float(deductions_str)
        except ValueError:
            return HttpResponse("Бонус и удержания должны быть числами", status=400)
        
        # Рассчитываем итоговую зарплату
        final_salary = employee.calculate_salary(bonus, deductions)
        
        # СОЗДАЕМ ЗАПИСЬ О ВЫПЛАТЕ (было Purchase, теперь SalaryPayment)
        # Используем person для хранения бонуса (как строку)
        Purchase.objects.create(
            product=employee,  # Все ещё product в БД, но логически это employee
            person=str(bonus),  # Храним бонус как строку в person
            address=description or f"Зарплата за {employee.position}",  # Описание в address
            # date автоматически установится
        )
        
        # Обновляем "стаж" сотрудника (увеличиваем quantity на 1 месяц = 0.083 года)
        # Это символическое увеличение стажа при каждой выплате
        employee.quantity += 1  # quantity теперь символизирует "месяцы работы"
        employee.save()
        
        return HttpResponse(
            f"✅ Зарплата выплачена сотруднику {employee.name}!<br>"
            f"✅ Должность: {employee.position}<br>"
            f"✅ Оклад: {employee.base_salary} руб.<br>"
            f"✅ Бонус: {bonus} руб.<br>"
            f"✅ Удержания: {deductions} руб.<br>"
            f"✅ ИТОГО: {final_salary} руб.<br>"
            f"✅ Стаж обновлен: {employee.years_of_service} лет"
        )

# =========== НОВАЯ ФУНКЦИЯ ДЛЯ АНАЛИТИКИ ===========
def salary_analytics(request):
    """Страница аналитики зарплат (новая функция)"""
    employees = Product.objects.all()
    payments = Purchase.objects.all()
    
    # Аналитика с использованием Pandas (как требуется в задании)
    if employees:
        # Создаем DataFrame для анализа
        data = []
        for emp in employees:
            data.append({
                'name': emp.name,
                'position': emp.position,
                'base_salary': float(emp.base_salary),
                'years_of_service': emp.years_of_service,
                'employee_type': emp.employee_type
            })
        
        df = pd.DataFrame(data)
        
        analytics = {
            'total_employees': len(df),
            'by_position': df.groupby('position')['base_salary'].agg(['count', 'mean', 'sum']).to_dict(),
            'by_type': df.groupby('employee_type')['base_salary'].mean().to_dict(),
            'salary_stats': {
                'mean': df['base_salary'].mean(),
                'median': df['base_salary'].median(),
                'std': df['base_salary'].std(),
                'min': df['base_salary'].min(),
                'max': df['base_salary'].max(),
            },
            'correlation_exp_salary': df['years_of_service'].corr(df['base_salary']),
        }
        
        # Анализ выплат
        if payments.exists():
            payment_data = []
            for p in payments:
                payment_data.append({
                    'employee': p.product.name,
                    'bonus': float(p.person) if p.person.replace('.', '', 1).isdigit() else 0,
                    'date': p.date,
                    'description': p.address
                })
            
            pdf = pd.DataFrame(payment_data)
            if not pdf.empty and 'bonus' in pdf.columns:
                analytics['bonus_stats'] = {
                    'total_bonuses': pdf['bonus'].sum(),
                    'avg_bonus': pdf['bonus'].mean(),
                    'max_bonus': pdf['bonus'].max(),
                }
    else:
        analytics = {}
    
    return render(request, 'shop/analytics.html', {
        'analytics': analytics,
        'employees': employees
    })