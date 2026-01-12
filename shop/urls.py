from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('buy/<int:employee_id>/', views.process_payment, name='process_payment'),
    path('analytics/', views.salary_analytics, name='salary_analytics'),
]