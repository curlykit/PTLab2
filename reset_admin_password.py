# create_first_admin.py
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tplab2.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

print("=== CREATING FIRST ADMIN ===")

# 1. Проверим сколько пользователей в базе
user_count = User.objects.count()
print(f"📊 Всего пользователей в базе: {user_count}")

if user_count == 0:
    print("❌ База ПУСТАЯ! Никто не создавал админа!")
else:
    print("📋 Существующие пользователи:")
    for user in User.objects.all():
        print(f"  - {user.username} (id: {user.id})")

# 2. УДАЛИМ всё что есть (если что-то есть)
print("\n🗑️ Очищаем таблицу пользователей...")
deleted = User.objects.all().delete()
print(f"  Удалено записей: {deleted[0]}")

# 3. СОЗДАДИМ ПЕРВОГО и ЕДИНСТВЕННОГО админа
print("\n👑 Создаем ПЕРВОГО суперпользователя...")

# ОЧЕНЬ ПРОСТОЙ пароль который точно введешь
SUPER_SIMPLE_PASSWORD = "123"  # ⚠️ Самый простой пароль!

try:
    # Создаем через стандартный метод Django
    admin = User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password=SUPER_SIMPLE_PASSWORD
    )
    print(f"✅ УСПЕХ! Создан первый админ!")
    print(f"✅ Логин: admin")
    print(f"✅ Пароль: {SUPER_SIMPLE_PASSWORD}")
    print(f"✅ Email: admin@example.com")
    
    # Дополнительная проверка
    admin.refresh_from_db()
    print(f"✅ ID пользователя: {admin.id}")
    print(f"✅ is_superuser: {admin.is_superuser}")
    print(f"✅ is_active: {admin.is_active}")
    
except Exception as e:
    print(f"❌ ОШИБКА при создании: {e}")
    
    # Попробуем вручную
    print("\n🛠️ Пробуем создать вручную...")
    admin = User(
        username='admin',
        email='admin@example.com',
        is_staff=True,
        is_superuser=True,
        is_active=True
    )
    admin.set_password(SUPER_SIMPLE_PASSWORD)
    admin.save()
    print(f"✅ Ручное создание УСПЕШНО!")
    print(f"   Логин: admin")
    print(f"   Пароль: {SUPER_SIMPLE_PASSWORD}")

print("\n🎯 ПОПРОБУЙТЕ ВОЙТИ СЕЙЧАС!")
print("   URL: https://ptlab2-v0xa.onrender.com/admin")
print("   Login: admin")
print("   Password: 123")
print("\n⚠️ После входа ОБЯЗАТЕЛЬНО смените пароль на сложный!")