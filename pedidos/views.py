from django.shortcuts import render, get_object_or_404, redirect
from .models import Pedido, ItemPedido, PedidoDomicilio, ItemPedidoDomicilio
from .forms import CrearPedidoForm, AgregarPlatoPedidoForm, FinalizarVentaForm,FinalizarVentaDomicilioForm, EditarPlatoForm,EditarPlatoDomicilioForm, EliminarPlatoForm, EliminarPlatoDomicilioForm, CrearPedidoFormDomicilio
from ventas.models import Compra, CompraDetalle, CompraDomicilio, CompraDetalleDomicilio
from django.contrib.auth.decorators import login_required
from mesas.models import Mesa
from platos.models import Plato, Categoria
from datetime import  timedelta
from django.utils.timezone import now
from django.http import HttpResponse
from decimal import Decimal
from django.http import JsonResponse
from django.utils.dateparse import parse_datetime
from django.utils import timezone
from django.urls import reverse
from usuarios.models import Profile, Cliente
from django.core.paginator import Paginator
from inventario.models import PlatoProducto
from decimal import Decimal
import pdfkit
from django.template.loader import render_to_string

def calcular_estado_tiempo(fecha_pedido):
    tiempo_transcurrido = now() - fecha_pedido
    print(tiempo_transcurrido)
    if tiempo_transcurrido < timedelta(minutes=30):  # Puedes ajustar estos valores según sea necesario
        return 'Pendiente'
    elif tiempo_transcurrido < timedelta(hours=1):
        return 'En camino'
    else:
        return 'Entregado'
    
def actualizar_estado(request, pedido_id):
    try:
        pedido = PedidoDomicilio.objects.get(id=pedido_id)
        fecha_pedido = pedido.fecha_pedido
        estado_tiempo = calcular_estado_tiempo(fecha_pedido)
        estado_tiempo = pedido.estado_pedido  # Asegúrate de que esta propiedad existe
        pedido.save()
        print(estado_tiempo)
        return JsonResponse({'estado_pedido': estado_tiempo})
    except Pedido.DoesNotExist:
        return JsonResponse({'error': 'Pedido no encontrado'}, status=404)

@login_required(login_url='/login/')
def pedidos_actualizados(request):
    last_update_time = request.GET.get('last_update', None)
    
    if last_update_time:
        last_update_time = parse_datetime(last_update_time)
        if last_update_time is None:
            # Manejo de errores si el parsing falla
            last_update_time = timezone.make_aware(timezone.datetime.min)
        elif last_update_time.tzinfo is None:
            last_update_time = timezone.make_aware(last_update_time)
    else:
        last_update_time = timezone.make_aware(timezone.datetime.min)

    pedidos = ItemPedido.objects.filter(
        pedido__usuario=request.user,
        estado='En proceso',
        created_at__gt=last_update_time,
        notificado=False
    )

    
    data = list(pedidos.values('id', 'pedido_id', 'plato__nombre', 'producto__nombre', 'cantidad', 'detalle', 'estado', 'created_at'))
    
    pedidos.update(notificado=True)

    return JsonResponse({'pedidos': data})

# Create your views here.
@login_required(login_url='/login/')
def crear_pedido(request):
    if request.method == 'POST':
        # Manejar el formulario de pedido normal (por mesa)
        form_pedido = CrearPedidoForm(request.POST, user=request.user)
        if form_pedido.is_valid():
            mesa = form_pedido.cleaned_data['mesa']
            pedido_existente = Pedido.objects.filter(mesa=mesa, usuario=request.user).first()
            if pedido_existente:
                return redirect('agregar_plato_pedido', pedido_id=pedido_existente.id)

            pedido = Pedido.objects.create(usuario=request.user, mesa=mesa)
            mesa.estado = 'Ocupada'
            mesa.save()

            return redirect('agregar_plato_pedido', pedido_id=pedido.id)
        
        # Manejar el formulario de pedido de domicilio
        form_domicilio = CrearPedidoFormDomicilio(request.POST)
        if form_domicilio.is_valid():
            pedido_domicilio = form_domicilio.save(commit=False)
            pedido_domicilio.usuario = request.user
            pedido_domicilio.save()
            pedido_domicilio_id = pedido_domicilio.id
            return redirect('agregar_plato_pedido_domicilio', pedido_id=pedido_domicilio_id)

    else:
        form_pedido = CrearPedidoForm(user=request.user)
        form_domicilio = CrearPedidoFormDomicilio()

    # Contexto para la plantilla
    pedidos_activos = Pedido.objects.filter(usuario=request.user)
    pedidos_activos_domicilios = PedidoDomicilio.objects.filter(usuario=request.user)
    mesas = Mesa.objects.filter(usuario=request.user, estado='Libre').order_by('numero')
    mesas_ocupada = Mesa.objects.filter(usuario=request.user, estado='Ocupada')
    profile = Profile.objects.get(user=request.user)
    
    # Crear una lista de tuplas para almacenar los items de cada pedido de domicilio
    pedidos_con_items = []
    for pedido in pedidos_activos_domicilios:
        items = ItemPedidoDomicilio.objects.filter(pedido=pedido)
        pedidos_con_items.append((pedido, items))

    actualizar_estado_url = reverse('actualizar_estado', args=[0]).replace('0', '')

    return render(request, 'pedidos/crear_pedido.html', {
        'form_pedido': form_pedido,
        'form_domicilio': form_domicilio,
        'pedidos_activos': pedidos_activos,
        'pedidos_activos_domicilios': pedidos_activos_domicilios,
        'mesas': mesas,
        'mesas_ocupada': mesas_ocupada,
        'profile': profile,
        'actualizar_estado_url': actualizar_estado_url,
        'pedidos_con_items': pedidos_con_items,
    })

@login_required(login_url='/login/')
def crear_pedido_domicilio(request):
    if request.method == 'POST':
        form = CrearPedidoFormDomicilio(request.POST)
        if form.is_valid():
            pedido_domicilio = form.save(commit=False)
            pedido_domicilio.usuario = request.user
            pedido_domicilio.save()
            pedido_domicilio_id = pedido_domicilio.id
            return JsonResponse({'success': True, 'redirect_url': reverse('agregar_plato_pedido_domicilio', args=[pedido_domicilio_id])})
            
        else:
            return JsonResponse({'error': 'Formulario inválido'}, status=400)
    return JsonResponse({'error': 'Método no permitido'}, status=405)

@login_required(login_url='/login/')
def cargar_detalle_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)

    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        action = request.POST.get('action')

        if action == 'editar':
            item = get_object_or_404(ItemPedido, id=item_id)
            nueva_cantidad = request.POST.get('nueva_cantidad')
            item.cantidad = nueva_cantidad
            item.save()
            return JsonResponse({'success': True})

        elif action == 'eliminar':
            item = get_object_or_404(ItemPedido, id=item_id)
            item.delete()
            return JsonResponse({'success': True})

    context = {
        'pedido': pedido,
    }

    # Renderizar el template con los detalles del pedido
    html = render_to_string('pedidos/detalle_pedido_modal.html', context)
    return JsonResponse({'html': html})

def editar_plato(request, item_id, pedido_id):
    if request.method == "POST":
        nueva_cantidad = request.POST.get('cantidad')
        item = ItemPedido.objects.get(id=item_id)
        item.cantidad = nueva_cantidad
        item.save()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False}, status=400)
    
def eliminar_plato(request, item_id, pedido_id):
    if request.method == "POST":
        try:
            item = ItemPedido.objects.get(id=item_id)
            item.delete()
            return JsonResponse({'success': True})
        except ItemPedido.DoesNotExist:
            return JsonResponse({'success': False}, status=404)
    return JsonResponse({'success': False}, status=400)

@login_required(login_url='/login/')
def cargar_detalle_pedido_domicilio(request, pedido_id):
    pedido = get_object_or_404(PedidoDomicilio, id=pedido_id)

    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        action = request.POST.get('action')

        if action == 'editar':
            item = get_object_or_404(ItemPedidoDomicilio, id=item_id)
            nueva_cantidad = request.POST.get('nueva_cantidad')
            item.cantidad = nueva_cantidad
            item.save()
            return JsonResponse({'success': True})

        elif action == 'eliminar':
            item = get_object_or_404(ItemPedidoDomicilio, id=item_id)
            item.delete()
            return JsonResponse({'success': True})

    context = {
        'pedido': pedido,
    }

    # Renderizar el template con los detalles del pedido
    html = render_to_string('pedidos/detalle_pedido_modal_domicilio.html', context)
    return JsonResponse({'html': html})

def editar_plato_domicilio(request, item_id, pedido_id):
    if request.method == "POST":
        nueva_cantidad = request.POST.get('cantidad')
        item = ItemPedidoDomicilio.objects.get(id=item_id)
        item.cantidad = nueva_cantidad
        item.save()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False}, status=400)
    
def eliminar_plato_domicilio(request, item_id, pedido_id):
    if request.method == "POST":
        try:
            item = ItemPedidoDomicilio.objects.get(id=item_id)
            item.delete()
            return JsonResponse({'success': True})
        except ItemPedido.DoesNotExist:
            return JsonResponse({'success': False}, status=404)
    return JsonResponse({'success': False}, status=400)

@login_required(login_url='/login/')
def generar_comanda(request, pedido_id):
    # Obtener el pedido y asegurar que el usuario sea el propietario
    pedido = get_object_or_404(Pedido, id=pedido_id, usuario=request.user)
    items = ItemPedido.objects.filter(pedido=pedido)

    # Renderizar la plantilla HTML
    html_string = render_to_string('pedidos/comanda.html', {'pedido': pedido, 'items': items})

    # Configurar pdfkit para usar wkhtmltopdf
    config = pdfkit.configuration(wkhtmltopdf='/path/to/wkhtmltopdf')  # Asegúrate de que la ruta sea correcta
    
    # Convertir el HTML a PDF
    pdf = pdfkit.from_string(html_string, False, configuration=config)

    # Crear una respuesta HTTP con el PDF
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="comanda_{pedido_id}.pdf"'
    return response

@login_required(login_url='/login/')
def agregar_plato_pedido(request, pedido_id):
    # Obtener el pedido y asegurar que el usuario sea el propietario
    pedido = get_object_or_404(Pedido, id=pedido_id, usuario=request.user)
    
    # Obtener todas las categorías y platos
    categorias = Categoria.objects.filter(usuario=request.user)
    platos_por_categoria = {categoria.nombre: categoria.platos.all() for categoria in categorias}

    # Manejo del término de búsqueda
    search_term = request.GET.get('buscar', '')
    if search_term:
        # Filtrar los platos basados en el término de búsqueda
        platos_por_categoria = {categoria.nombre: categoria.platos.filter(nombre__icontains=search_term) for categoria in categorias}

    # Manejo del formulario
    if request.method == 'POST':
        form = AgregarPlatoPedidoForm(request.POST, user=request.user)
        if form.is_valid():
            plato = form.cleaned_data['plato']
            cantidad = form.cleaned_data['cantidad']
            detalle = form.cleaned_data['detalle']
            if cantidad is None or cantidad <= 0:
                return JsonResponse({'success': False, 'error': 'Cantidad inválida'}, status=400)

            # Verifica si el plato ya existe en el pedido
            item, created = ItemPedido.objects.get_or_create(pedido=pedido, plato=plato, cantidad=cantidad)
            if not created:
                item.cantidad += cantidad
            else:
                item.cantidad = cantidad
            item.detalle = detalle
            item.save()

            return JsonResponse({'success': True})

    form = AgregarPlatoPedidoForm(user=request.user, search_term=search_term)

    # Obtener los items actuales en el pedido
    items = ItemPedido.objects.filter(pedido=pedido, estado='En proceso')

    # Contexto para renderizar la plantilla
    context = {
        'form': form,
        'pedido': pedido,
        'items': items,
        'categorias': categorias,  # Asegúrate de pasar las categorías al contexto
        'platos_por_categoria': platos_por_categoria,  # Platos agrupados por categoría
        'query': search_term,
    }
    return render(request, 'pedidos/agregar_plato_pedido.html', context)

@login_required(login_url='/login/')
def agregar_plato_pedido_domicilio(request, pedido_id):
    # Obtener el pedido y asegurar que el usuario sea el propietario
    pedido = get_object_or_404(PedidoDomicilio, id=pedido_id, usuario=request.user)
    
    # Obtener todas las categorías y platos
    categorias = Categoria.objects.filter(usuario=request.user)
    platos_por_categoria = {categoria.nombre: categoria.platos.all() for categoria in categorias}

    # Manejo del término de búsqueda
    search_term = request.GET.get('buscar', '')
    if search_term:
        # Filtrar los platos basados en el término de búsqueda
        platos_por_categoria = {categoria.nombre: categoria.platos.filter(nombre__icontains=search_term) for categoria in categorias}

    # Manejo del formulario
    if request.method == 'POST':
        form = AgregarPlatoPedidoForm(request.POST, user=request.user)
        if form.is_valid():
            plato = form.cleaned_data['plato']
            cantidad = form.cleaned_data['cantidad']
            detalle = form.cleaned_data['detalle']
            if cantidad is None or cantidad <= 0:
                return JsonResponse({'success': False, 'error': 'Cantidad inválida'}, status=400)

            # Verifica si el plato ya existe en el pedido
            item, created = ItemPedidoDomicilio.objects.get_or_create(pedido=pedido, plato=plato, defaults={'cantidad': cantidad})

            if not created:
                item.cantidad += cantidad
            else:
                item.cantidad = cantidad
            item.detalle = detalle
            item.save()

            return JsonResponse({'success': True})

    form = AgregarPlatoPedidoForm(user=request.user, search_term=search_term)

    # Obtener los items actuales en el pedido
    items = ItemPedidoDomicilio.objects.filter(pedido=pedido)

    # Contexto para renderizar la plantilla
    context = {
        'form': form,
        'pedido': pedido,
        'items': items,
        'categorias': categorias,  # Asegúrate de pasar las categorías al contexto
        'platos_por_categoria': platos_por_categoria,  # Platos agrupados por categoría
        'query': search_term,
    }
    return render(request, 'pedidos/agregar_plato_pedido_domicilio.html', context)


@login_required(login_url='/login/')
def finalizar_venta(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id, usuario=request.user)
    compra_id = 0

    if request.method == 'POST':
        form = FinalizarVentaForm(request.POST)
        if form.is_valid():
            tipo_pago = form.cleaned_data['tipo_pago']
            cedula_cliente = form.cleaned_data['cedula_cliente']
            impuesto = form.cleaned_data['impuesto']
            descuento = form.cleaned_data['descuento']
            propina = form.cleaned_data['propina']
            descuento = Decimal(descuento)
            propina = Decimal(propina)
            
            # Calcular el total del pedido
            total = sum(item.plato.precio * item.cantidad for item in pedido.itempedido_set.all())

            descontar = (descuento*total/100)
            adicionar = (propina*total/100)

            total_sin_descuento = total

            total_sin_impuesto = (total - descontar) + adicionar
            
            # Crear la compra
            compra = Compra.objects.create(
                usuario=pedido.usuario,
                mesa=pedido.mesa,
                total=total_sin_impuesto,
                total_sin_descuento=total_sin_descuento,
                total_descuento = descontar,
                total_propina = adicionar,
                tipo_pago=tipo_pago,
                cedula_cliente=cedula_cliente,
                impuesto=impuesto
                
            )
            compra.total_con_impuesto()
            compra.save()
            compra_id = compra.id

            # Agregar los platos del pedido a la compra
            for item in pedido.itempedido_set.all():
                compra_detalle = CompraDetalle.objects.create(
                    compra=compra,
                    plato=item.plato,
                    cantidad=item.cantidad
                )
                plato = item.plato
                plato_productos = PlatoProducto.objects.filter(plato=plato)
                for plato_producto in plato_productos:
                    producto = plato_producto.producto
                    cantidad_descontar = plato_producto.cantidad_necesaria * item.cantidad
                    if producto.cantidad_disponible >= cantidad_descontar:
                        producto.cantidad_disponible -= cantidad_descontar
                        producto.save()
                    else:
                        mensaje = f'Cantidad insuficiente en {plato.nombre} | {producto.nombre}: {producto.cantidad_disponible} | Cantidad Necesaria: {cantidad_descontar} |. Algunos botones están deshabilitados.'
                        # Volver a la misma página con un mensaje de error
                        return render(request, 'pedidos/finalizar_venta.html', {
                            'form': form,
                            'pedido': pedido,
                            'total': total_sin_impuesto,
                            'compra_id':compra_id,
                            'error': mensaje,
                            'disable_buttons': True  # Añadir este contexto para manejar botones deshabilitados
                        })

            
            mesa = pedido.mesa
            mesa.estado = 'Libre'
            mesa.save()

            # Eliminar el pedido una vez finalizada la compra
            pedido.delete()

            # Redirigir a la vista de impresión de la factura
            return redirect('imprimir_factura', compra_id=compra.id)
    else:
        # Si la solicitud no es POST, inicializamos el formulario y los totales
        form = FinalizarVentaForm()
        total_sin_impuesto = sum(item.plato.precio * item.cantidad for item in pedido.itempedido_set.all())
        total_con_impuesto = total_sin_impuesto

    

    return render(request, 'pedidos/finalizar_venta.html', {
        'form': form,
        'pedido': pedido,
        'total': total_sin_impuesto,
        'total_con_impuesto': total_con_impuesto,
        'compra_id':compra_id
    })

@login_required(login_url='/login/')
def finalizar_venta_domicilio(request, pedido_id):
    pedido = get_object_or_404(PedidoDomicilio, id=pedido_id, usuario=request.user)
    compra_id = 0

    if request.method == 'POST':
        form = FinalizarVentaDomicilioForm(request.POST)
        if form.is_valid():
            tipo_pago = form.cleaned_data['tipo_pago']
            impuesto = form.cleaned_data['impuesto']
            descuento = form.cleaned_data['descuento']
            propina = form.cleaned_data['propina']
            print(type(propina))
            print(propina)
            descuento = Decimal(descuento)
            propina = Decimal(propina)
            guardar_cliente = form.cleaned_data['guardar_cliente']

            if guardar_cliente:
                # Buscar o crear el cliente
                cliente, created = Cliente.objects.get_or_create(
                    usuario=request.user,
                    documento=pedido.doc_cliente,
                    defaults={
                        'nombre': pedido.nombre_cliente,
                        'telefono': pedido.telefono_cliente,
                        'direccion': pedido.direccion_cliente
                    }
                )
                print(f"Cliente guardado: {cliente}")
            else:
                cliente = None

            # Calcular el total del pedido
            total = sum(item.plato.precio * item.cantidad for item in pedido.itempedidodomicilio_set.all())

            descontar = (descuento*total/100)
            adicionar = propina

            total_sin_descuento = total

            total_sin_impuesto = (total - descontar) + adicionar

            # Crear la compra
            compra = CompraDomicilio.objects.create(
                usuario=pedido.usuario,
                cedula_cliente=pedido.doc_cliente,
                nombre_cliente=pedido.nombre_cliente,
                telefono_cliente=pedido.telefono_cliente,
                direccion_cliente=pedido.direccion_cliente,
                total=total_sin_impuesto,
                total_sin_descuento=total_sin_descuento,
                total_descuento = descontar,
                total_propina = adicionar,
                tipo_pago=tipo_pago,
                impuesto=impuesto
            )
            compra.total_con_impuesto()
            compra.save()
            compra_id = compra.id

            # Agregar los platos del pedido a la compra
            for item in pedido.itempedidodomicilio_set.all():
                compra_detalle = CompraDetalleDomicilio.objects.create(
                    compra=compra,
                    plato=item.plato,
                    cantidad=item.cantidad
                )
                plato = item.plato
                plato_productos = PlatoProducto.objects.filter(plato=plato)
                for plato_producto in plato_productos:
                    producto = plato_producto.producto
                    cantidad_descontar = plato_producto.cantidad_necesaria * item.cantidad
                    if producto.cantidad_disponible >= cantidad_descontar:
                        producto.cantidad_disponible -= cantidad_descontar
                        producto.save()
                    else:
                        mensaje = f'Cantidad insuficiente en {plato.nombre} | {producto.nombre}: {producto.cantidad_disponible} | Cantidad Necesaria: {cantidad_descontar} |. Algunos botones están deshabilitados.'
                        # Volver a la misma página con un mensaje de error
                        return render(request, 'pedidos/finalizar_venta_domicilio.html', {
                            'form': form,
                            'pedido': pedido,
                            'total': total_sin_impuesto,
                            'compra_id':compra_id,
                            'error': mensaje,
                            'disable_buttons': True  # Añadir este contexto para manejar botones deshabilitados
                        })
            
            # Eliminar el pedido una vez finalizada la compra
            pedido.delete()

             # Redirigir a la vista de impresión de la factura
            return redirect('imprimir_factura_domicilio', compra_id=compra.id)
    else:
        form = FinalizarVentaDomicilioForm()
        total = sum(item.plato.precio * item.cantidad for item in pedido.itempedidodomicilio_set.all())
        total_sin_impuesto = sum(item.plato.precio * item.cantidad for item in pedido.itempedidodomicilio_set.all())
        total_con_impuesto = total_sin_impuesto
        
    return render(request, 'pedidos/finalizar_venta_domicilio.html', {
        'form': form,
        'pedido': pedido,
        'total': total_sin_impuesto,
        'total_con_impuesto': total_con_impuesto,
        'compra_id':compra_id
    })

@login_required(login_url='/login/')
def listar_pedidos_activos(request):
    pedidos_activos = Pedido.objects.filter(usuario=request.user, itempedido__estado='En proceso').distinct()
    pedidos_domicilio = PedidoDomicilio.objects.filter(
        usuario=request.user,
        itempedidodomicilio__estado='En proceso'
    ).distinct()

    # Dividir los pedidos en grupos de 3
    paginator = Paginator(pedidos_activos, 4)  # 3 pedidos por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    paginator_domicilio = Paginator(pedidos_domicilio, 4)  # 3 pedidos por página
    page_number_domicilio = request.GET.get('page_domicilio')
    page_obj_domicilio = paginator_domicilio.get_page(page_number_domicilio)
    
    mesas = Mesa.objects.filter(usuario=request.user, estado='Ocupada')

    # Crear un contexto para cada página
    slides = [
        page_obj.paginator.page(i).object_list
        for i in page_obj.paginator.page_range
    ]

    slides_domicilio = [
        page_obj_domicilio.paginator.page(i).object_list
        for i in page_obj_domicilio.paginator.page_range
    ]

    context = {
        'pedidos_activos': pedidos_activos,
        'pedidos_domicilio': pedidos_domicilio,
        'page_obj': page_obj,
        'page_obj_domicilio': page_obj_domicilio,
        'mesas': Mesa.objects.filter(usuario=request.user, estado='Ocupada'),
        'slides': slides,  # Pasar los datos de cada slide de pedidos activos
        'slides_domicilio': slides_domicilio,  # Pasar los datos de cada slide de pedidos de domicilio
    }

    return render(request, 'pedidos/listar_pedidos_activos.html', context)

@login_required(login_url='/login/')
def detalle_pedido(request, mesa_id):
    pedido = get_object_or_404(Pedido, mesa_id=mesa_id, usuario=request.user)

    if request.method == 'POST':
        if 'editar_plato' in request.POST:
            item_id = request.POST.get('item_id')
            item = get_object_or_404(ItemPedido, id=item_id)
            form = EditarPlatoForm(request.POST, instance=item)
            if form.is_valid():
                form.save()
            return redirect('detalle_pedido',mesa_id=mesa_id)
        elif 'eliminar_plato' in request.POST:
            item_id = request.POST.get('item_id')
            item = get_object_or_404(ItemPedido, id=item_id)
            item.delete()
            return redirect('detalle_pedido',mesa_id=mesa_id)

    context = {
        'pedido': pedido,
        'editar_plato_form': EditarPlatoForm(),
        'eliminar_plato_form': EliminarPlatoForm(),
    }
    platos = Plato.objects.filter(usuario=request.user)

    return render(request, 'pedidos/detalle_pedido.html', {'pedido': pedido, 'platos':platos})

@login_required(login_url='/login/')
def detalle_pedido_domicilio(request, pedido_id):
    pedido = get_object_or_404(PedidoDomicilio, id=pedido_id, usuario=request.user)

    if request.method == 'POST':
        if 'editar_plato_domicilio' in request.POST:
            item_id = request.POST.get('item_id')
            item = get_object_or_404(ItemPedidoDomicilio, id=item_id)
            form = EditarPlatoDomicilioForm(request.POST, instance=item)
            if form.is_valid():
                form.save()
            return redirect('detalle_pedido_domicilio', pedido_id=pedido_id)
        elif 'eliminar_plato_domicilio' in request.POST:
            item_id = request.POST.get('item_id')
            item = get_object_or_404(ItemPedidoDomicilio, id=item_id)
            item.delete()
            return redirect('detalle_pedido_domicilio', pedido_id=pedido_id)

    context = {
        'pedido': pedido,
        'editar_plato_form': EditarPlatoDomicilioForm(),
        'eliminar_plato_form': EliminarPlatoDomicilioForm(),
        'platos': Plato.objects.filter(usuario=request.user),
    }

    return render(request, 'pedidos/detalle_pedido_domicilio.html', context)

def decimal_to_float(d):
    if isinstance(d, Decimal):
        return float(d)
    return d

@login_required(login_url='/login/')
def cambiar_estado_item(request, item_id):
    if request.method == 'POST':
        item = get_object_or_404(ItemPedido, id=item_id)
        item.estado = 'Entregado'  # O el estado que desees actualizar
        item.save()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False}, status=400)

@login_required(login_url='/login/')
def cambiar_estado_item_domicilio(request, item_id):
    if request.method == 'POST':
        item = get_object_or_404(ItemPedidoDomicilio, id=item_id)
        item.estado = 'Entregado'  # O el estado que desees actualizar
        item.save()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False}, status=400)

@login_required(login_url='/login/')
def imprimir_comanda_pedido(request, pedido_id):
    # Verificar si el usuario tiene permiso para acceder a esta compra
    pedido = get_object_or_404(Pedido, id=pedido_id, usuario=request.user)
    detalles = ItemPedido.objects.filter(pedido=pedido, estado='En proceso')
    profile = Profile.objects.get(user=request.user)
    
    
    redirect_url = reverse('crear_pedido')

    # Renderizar una página HTML que se imprimirá
    return render(request, 'pedidos/imprimir_comanda.html', {
        'pedido': pedido,
        'detalles': detalles,
        'profile': profile,
        'redirect_url': redirect_url,
    })

@login_required(login_url='/login/')
def imprimir_comanda_pedido_domi(request, pedido_id):
    # Verificar si el usuario tiene permiso para acceder a esta compra
    pedido = get_object_or_404(PedidoDomicilio, id=pedido_id, usuario=request.user)
    detalles = ItemPedidoDomicilio.objects.filter(pedido=pedido, estado='En proceso')
    profile = Profile.objects.get(user=request.user)
    
    
    redirect_url = reverse('crear_pedido')

    # Renderizar una página HTML que se imprimirá
    return render(request, 'pedidos/imprimir_comanda_domi.html', {
        'pedido': pedido,
        'detalles': detalles,
        'profile': profile,
        'redirect_url': redirect_url,
    })

