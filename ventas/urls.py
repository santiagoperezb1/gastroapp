from django.urls import path
from .views import (
    obtener_registros_venta,
    editar_venta,
    editar_venta_domicilio,
    eliminar_venta_mesa,
    eliminar_venta_domicilio,
    imprimir_factura,
    imprimir_factura_domicilio,
    imprimir_factura_venta,
    imprimir_factura_venta_domicilio,
    enviar_factura_por_email,
    enviar_factura_por_email_domicilio,
    estadisticas,
    buscar_cliente_por_documento,
    buscar_clientes,
)

urlpatterns = [
    path('', obtener_registros_venta, name='obtener_registros_venta'),
    path('eliminar-venta/<int:venta_id>/', eliminar_venta_mesa, name='eliminar_venta_mesa'),
    path('eliminar-venta-domicilio/<int:venta_id>/', eliminar_venta_domicilio, name='eliminar_venta_domicilio'),
    path('editar_venta/<int:id>/', editar_venta, name='editar_venta'),
    path('editar_venta_domicilio/<int:id>/', editar_venta_domicilio, name='editar_venta_domicilio'),
    path('factura/imprimir/<int:compra_id>/', imprimir_factura, name='imprimir_factura'),
    path('factura/imprimir_domicilio/<int:compra_id>/', imprimir_factura_domicilio, name='imprimir_factura_domicilio'),
    path('factura/imprimir_venta/<int:compra_id>/', imprimir_factura_venta, name='imprimir_factura_venta'),
    path('factura/imprimir_venta_domicilio/<int:compra_id>/', imprimir_factura_venta_domicilio, name='imprimir_factura_venta_domicilio'),
    path('enviar_factura_por_email/<int:compra_id>/', enviar_factura_por_email, name='enviar_factura_por_email'),
    path('enviar_factura_por_email_domicilio/<int:compra_id>/', enviar_factura_por_email_domicilio, name='enviar_factura_por_email_domicilio'),
    path('estadisticas/', estadisticas, name='estadisticas'),
    path('buscar-cliente/', buscar_cliente_por_documento, name='buscar_cliente'),
    path('buscar_clientes/', buscar_clientes, name='buscar_clientes'),
]       