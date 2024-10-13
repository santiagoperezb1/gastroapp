from django.contrib import admin

from .models import Compra, CompraDetalle, CompraDomicilio, CompraDetalleDomicilio

admin.site.register(Compra)
admin.site.register(CompraDetalle)
admin.site.register(CompraDomicilio)
admin.site.register(CompraDetalleDomicilio)