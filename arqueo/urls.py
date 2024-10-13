from django.urls import path
from . import views

urlpatterns = [
    path('', views.listar_arqueos, name='listar_arqueos'),
    path('<int:arqueo_id>/', views.detalle_arqueo, name='detalle_arqueo'),
    path('iniciar/', views.iniciar_arqueo_caja, name='iniciar_arqueo_caja'),
    path('cerrar/<int:arqueo_id>/', views.cerrar_arqueo_caja, name='cerrar_arqueo_caja'),
    path('eliminar/<int:arqueo_id>/', views.eliminar_arqueo, name='eliminar_arqueo'),
]
