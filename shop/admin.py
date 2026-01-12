# shop/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import Product, Purchase


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    # Отображение в списке
    list_display = (
        'name',
        'position',
        'employee_type_display',
        'salary_display',
        'experience_display',
        'employee_status',
    )
    
    list_filter = ('employee_type',)
    search_fields = ('name', 'position')
    list_editable = ('position',)  # Позицию можно редактировать прямо в списке
    
    # Группировка полей в форме редактирования
    fieldsets = (
        ('Личная информация', {
            'fields': ('name', 'position'),
            'description': 'Основные данные сотрудника'
        }),
        ('Классификация', {
            'fields': ('employee_type',),
            'description': 'Уровень сотрудника'
        }),
        ('Финансовая информация', {
            'fields': ('price', 'quantity'),
            'description': 'Оклад и стаж работы'
        }),
        ('Автоматические расчеты', {
            'fields': (),
            'description': format_html(
                '<span style="color: #666; font-style: italic;">'
                'Автоматически рассчитывается:<br>'
                '- Должность: если не указана, будет "Специалист"<br>'
                '- Уровень: если не выбран, определяется по стажу'
                '</span>'
            ),
            'classes': ('collapse',),
        }),
    )
    
    # Кастомизация полей
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Подсказки для полей
        form.base_fields['name'].help_text = 'Введите ФИО сотрудника полностью'
        form.base_fields['price'].help_text = 'Основной оклад в рублях'
        form.base_fields['quantity'].help_text = 'Стаж работы в годах'
        form.base_fields['position'].help_text = 'Например: Разработчик, Менеджер, Аналитик'
        form.base_fields['employee_type'].help_text = 'Если не выбран, определится по стажу автоматически'
        return form
    
    # Методы для красивого отображения
    def employee_type_display(self, obj):
        return obj.calculated_employee_type
    employee_type_display.short_description = 'Уровень'
    employee_type_display.admin_order_field = 'employee_type'
    
    def salary_display(self, obj):
        return f"{obj.price:.2f} руб."
    salary_display.short_description = 'Оклад'
    salary_display.admin_order_field = 'price'
    
    def experience_display(self, obj):
        years = obj.quantity
        if years == 1:
            return f"{years} год"
        elif 2 <= years <= 4:
            return f"{years} года"
        else:
            return f"{years} лет"
    experience_display.short_description = 'Стаж'
    experience_display.admin_order_field = 'quantity'
    
    def employee_status(self, obj):
        if obj.quantity < 1:
            return format_html('<span style="color: orange;">🟡 Новый</span>')
        elif obj.quantity < 3:
            return format_html('<span style="color: green;">🟢 Опытный</span>')
        else:
            return format_html('<span style="color: blue;">🔵 Ветеран</span>')
    employee_status.short_description = 'Статус'
    
    # Действия в админке
    actions = ['set_as_junior', 'set_as_middle', 'set_as_senior']
    
    def set_as_junior(self, request, queryset):
        updated = queryset.update(employee_type='JUNIOR')
        self.message_user(request, f"{updated} сотрудников установлены как Junior")
    set_as_junior.short_description = "Установить уровень: Junior"
    
    def set_as_middle(self, request, queryset):
        updated = queryset.update(employee_type='MIDDLE')
        self.message_user(request, f"{updated} сотрудников установлены как Middle")
    set_as_middle.short_description = "Установить уровень: Middle"
    
    def set_as_senior(self, request, queryset):
        updated = queryset.update(employee_type='SENIOR')
        self.message_user(request, f"{updated} сотрудников установлены как Senior")
    set_as_senior.short_description = "Установить уровень: Senior"


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = (
        'employee_display',
        'payment_type_display',
        'bonus_display',
        'total_salary_display',
        'date_display',
        'description_display',
    )
    
    list_filter = ('payment_type', 'date')
    search_fields = ('product__name', 'address')
    date_hierarchy = 'date'
    list_per_page = 20
    
    # Группировка полей в форме
    fieldsets = (
        ('Основная информация', {
            'fields': ('product', 'payment_type'),
            'description': 'Выберите сотрудника и тип выплаты'
        }),
        ('Финансовая информация', {
            'fields': ('person',),
            'description': 'Сумма премии (если есть)'
        }),
        ('Дополнительно', {
            'fields': ('address',),
            'description': 'Комментарий к выплате'
        }),
    )
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Переименовываем метки
        form.base_fields['person'].label = 'Премия (руб.)'
        form.base_fields['person'].help_text = 'Введите сумму премии. Если только зарплата - оставьте 0'
        form.base_fields['address'].label = 'Комментарий'
        form.base_fields['address'].help_text = 'Например: Зарплата за январь 2024, Премия за проект'
        form.base_fields['payment_type'].help_text = 'Выберите тип выплаты'
        return form
    
    # Методы отображения
    def employee_display(self, obj):
        return obj.product.name
    employee_display.short_description = 'Сотрудник'
    employee_display.admin_order_field = 'product__name'
    
    def payment_type_display(self, obj):
        return obj.calculated_payment_type
    payment_type_display.short_description = 'Тип выплаты'
    payment_type_display.admin_order_field = 'payment_type'
    
    def bonus_display(self, obj):
        bonus = obj.bonus
        if bonus > 0:
            return format_html(f'<span style="color: green; font-weight: bold;">+{bonus:.2f} руб.</span>')
        elif bonus == 0:
            return format_html('<span style="color: #666;">0.00 руб.</span>')
        else:
            return format_html(f'<span style="color: red;">{bonus:.2f} руб.</span>')
    bonus_display.short_description = 'Премия'
    
    def total_salary_display(self, obj):
        total = obj.final_salary
        return format_html(f'<b>{total:.2f} руб.</b>')
    total_salary_display.short_description = 'Итого'
    total_salary_display.admin_order_field = 'person'
    
    def date_display(self, obj):
        return obj.date.strftime('%d.%m.%Y %H:%M')
    date_display.short_description = 'Дата выплаты'
    date_display.admin_order_field = 'date'
    
    def description_display(self, obj):
        description = obj.address or "Без описания"
        if len(description) > 50:
            return f"{description[:50]}..."
        return description
    description_display.short_description = 'Комментарий'
    
    # Фильтр по сотрудникам
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Предзагружаем связанные объекты для оптимизации
        return qs.select_related('product')
    
    # Экспорт данных
    actions = ['export_as_csv']
    
    def export_as_csv(self, request, queryset):
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="payments.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Сотрудник', 'Тип выплаты', 'Премия', 'Итого', 'Дата', 'Комментарий'])
        
        for payment in queryset:
            writer.writerow([
                payment.product.name,
                payment.calculated_payment_type,
                payment.bonus,
                payment.final_salary,
                payment.date.strftime('%d.%m.%Y %H:%M'),
                payment.address or ""
            ])
        
        return response
    export_as_csv.short_description = "Экспортировать выбранные в CSV"