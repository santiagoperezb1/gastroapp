from django.urls import path
from .views import lista_productos, actualizar_producto, eliminar_producto, crear_producto, asociar_producto

urlpatterns = [
    path('productos/', lista_productos, name='lista_productos'),
    path('productos/crear-producto/', crear_producto, name='crear_producto'),
    path('productos/actualizar/<int:producto_id>/', actualizar_producto, name='actualizar_producto'),
    path('productos/eliminar/<int:producto_id>/', eliminar_producto, name='eliminar_producto'),
    path('asociar-producto/<int:plato_id>/', asociar_producto, name='asociar_producto'),
]
