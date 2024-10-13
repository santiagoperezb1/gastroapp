from django.contrib import admin

from .models import Pedido, ItemPedido, PedidoDomicilio, ItemPedidoDomicilio

admin.site.register(Pedido)
admin.site.register(ItemPedido)
admin.site.register(PedidoDomicilio)
admin.site.register(ItemPedidoDomicilio)