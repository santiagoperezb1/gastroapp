from django.urls import path

from . import views

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('precios/', views.precios, name='precios'),
    path('software/', views.software, name='software'),
]