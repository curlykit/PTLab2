import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tplab2.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

try:
    # Находим пользователя admin
    admin_user = User.objects.get(username='admin')
    
    # Меняем пароль на новый
    new_password = 'NewAdminPass123!'  # ⚠️ ИЗМЕНИ НА СВОЙ ПАРОЛЬ!
    admin_user.set_password(new_password)
    admin_user.save()
    
    print(f"✅ Пароль пользователя 'admin' изменен на: {new_password}")
    print(f"✅ Вход: admin / {new_password}")
    
except User.DoesNotExist:
    # Если пользователя admin нет, создаем нового
    new_password = '12345678'  # ⚠️ ИЛИ ЗАДАЙ ДРУГОЙ ПАРОЛЬ!
    User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password=new_password  # ⬅️ Используем переменную!
    )
    print(f"✅ Создан новый суперпользователь: admin / {new_password}")  # ⬅️ Правильный вывод!