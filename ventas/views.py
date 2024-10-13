from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from .models import Compra, CompraDomicilio, CompraDetalle, CompraDetalleDomicilio
from .forms import CompraForm, CompraDomicilioForm
from datetime import datetime
from django.contrib import messages
from django.urls import reverse
from usuarios.models import Profile, Cliente
from django.conf import settings
from django.template.loader import render_to_string
from django.http import JsonResponse
from io import BytesIO 
from django.core.mail import EmailMessage
from xhtml2pdf import pisa
from django.utils.dateparse import parse_date
from django.db.models import Sum
from django.db.models.functions import ExtractMonth
import json
import calendar

@login_required(login_url='/login/')
def obtener_registros_venta(request):
    cedula = request.GET.get('cedula')
    id = request.GET.get('id')
    fecha = request.GET.get('fecha')
    user_profile = request.user.profile
    compras = Compra.objects.filter(usuario=request.user).order_by('-fecha_compra')
    compras_domicilios = CompraDomicilio.objects.filter(usuario=request.user).order_by('-fecha_compra')

    if id:
        compras = compras.filter(id=id)
        compras_domicilios = compras_domicilios.filter(id=id)
    elif cedula:
        compras = compras.filter(cedula_cliente__icontains=cedula)
        compras_domicilios = compras_domicilios.filter(cedula_cliente__icontains=cedula)
    
    if fecha:
        try:
            fecha = datetime.strptime(fecha, '%Y-%m-%d')
            compras = compras.filter(fecha_compra__date=fecha.date())
            compras_domicilios = compras_domicilios.filter(fecha_compra__date=fecha.date())
        except ValueError:
            # Manejar error de formato de fecha si es necesario
            pass

    # Paginación
    paginator_compras = Paginator(compras, 10)  # Muestra 10 compras por página
    paginator_compras_domicilios = Paginator(compras_domicilios, 10)  # Muestra 10 domicilios por página

    page_compras = request.GET.get('page_compras')
    page_compras_domicilios = request.GET.get('page_compras_domicilios')

    try:
        compras_paginated = paginator_compras.page(page_compras)
    except PageNotAnInteger:
        compras_paginated = paginator_compras.page(1)
    except EmptyPage:
        compras_paginated = paginator_compras.page(paginator_compras.num_pages)

    try:
        compras_domicilios_paginated = paginator_compras_domicilios.page(page_compras_domicilios)
    except PageNotAnInteger:
        compras_domicilios_paginated = paginator_compras_domicilios.page(1)
    except EmptyPage:
        compras_domicilios_paginated = paginator_compras_domicilios.page(paginator_compras_domicilios.num_pages)

    return render(request, 'ventas/obtener_registros_venta.html', {
        'compras': compras_paginated,
        'compras_domicilios': compras_domicilios_paginated,
        'pin': user_profile.pin,
    })

@login_required(login_url='/login/')
def editar_venta(request, id):
    compra = get_object_or_404(Compra, id=id)
    user_profile = request.user.profile
    if request.method == 'POST':
        form = CompraForm(request.POST, instance=compra)
        if form.is_valid():
            form.save()
            compra.total_con_impuesto()
            compra.save()
            return redirect('obtener_registros_venta')  # Redirige a la lista de compras después de guardar
    else:
        form = CompraForm(instance=compra)
    return render(request, 'ventas/editar_venta.html', {'form': form,'compra':compra, 'pin': user_profile.pin})

@login_required(login_url='/login/')
def editar_venta_domicilio(request, id):
    compra = get_object_or_404(CompraDomicilio, id=id)
    user_profile = request.user.profile
    if request.method == 'POST':
        form = CompraDomicilioForm(request.POST, instance=compra)
        if form.is_valid():
            form.save()
            compra.total_con_impuesto()
            compra.save()
            return redirect('obtener_registros_venta')  # Redirige a la lista de compras después de guardar
    else:
        form = CompraDomicilioForm(instance=compra)
    return render(request, 'ventas/editar_venta_domicilio.html', {'form': form,'compra':compra,'pin': user_profile.pin})

@login_required(login_url='/login/')
def eliminar_venta_mesa(request, venta_id):
    if request.method == 'POST':
        # Lógica para eliminar el pago
        venta = get_object_or_404(Compra, id=venta_id, usuario=request.user)
        venta.delete()
        messages.success(request, 'Registro eliminado exitosamente.')
        return redirect('obtener_registros_venta')
    
    # Si no es POST, podrías retornar un error o algo
    return redirect('obtener_registros_venta')

@login_required(login_url='/login/')
def eliminar_venta_domicilio(request, venta_id):
    if request.method == 'POST':
        venta = get_object_or_404(CompraDomicilio, id=venta_id, usuario=request.user)
        venta.delete()
        messages.success(request, 'Registro eliminado exitosamente.')
        return redirect('obtener_registros_venta')
    
    # Si no es POST, podrías retornar un error o algo
    return redirect('obtener_registros_venta')

@login_required(login_url='/login/')
def imprimir_factura(request, compra_id):
    # Verificar si el usuario tiene permiso para acceder a esta compra
    compra = get_object_or_404(Compra, id=compra_id, usuario=request.user)
    detalles = CompraDetalle.objects.filter(compra=compra)
    profile = Profile.objects.get(user=request.user)
    
    # Calcular totales
    total_sin_impuesto = sum(detalle.plato.precio * detalle.cantidad for detalle in detalles)
    total_impuesto = compra.total_impuesto
    total_con_impuesto = total_sin_impuesto + total_impuesto

    # Calcular el total por cada detalle
    detalles_con_totales = [
        {
            'plato': detalle.plato,
            'cantidad': detalle.cantidad,
            'precio_unitario': detalle.plato.precio,
            'total_detalle': detalle.plato.precio * detalle.cantidad
        }
        for detalle in detalles
    ]
    
    redirect_url = reverse('crear_pedido')

    # Renderizar una página HTML que se imprimirá
    return render(request, 'ventas/imprimir_factura.html', {
        'compra': compra,
        'detalles': detalles_con_totales,
        'total_sin_impuesto': total_sin_impuesto,
        'total_impuesto': total_impuesto,
        'total_con_impuesto': total_con_impuesto,
        'profile': profile,
        'redirect_url': redirect_url,
    })

@login_required(login_url='/login/')
def imprimir_factura_domicilio(request, compra_id):
    # Verificar si el usuario tiene permiso para acceder a esta compra
    compra = get_object_or_404(CompraDomicilio, id=compra_id, usuario=request.user)
    detalles = CompraDetalleDomicilio.objects.filter(compra=compra)
    profile = Profile.objects.get(user=request.user)
    
    # Calcular totales
    total_sin_impuesto = sum(detalle.plato.precio * detalle.cantidad for detalle in detalles)
    total_impuesto = compra.total_impuesto
    total_con_impuesto = total_sin_impuesto + total_impuesto

    # Calcular el total por cada detalle
    detalles_con_totales = [
        {
            'plato': detalle.plato,
            'cantidad': detalle.cantidad,
            'precio_unitario': detalle.plato.precio,
            'total_detalle': detalle.plato.precio * detalle.cantidad
        }
        for detalle in detalles
    ]

    redirect_url = reverse('crear_pedido')

    # Renderizar una página HTML que se imprimirá
    return render(request, 'ventas/imprimir_factura_domicilio.html', {
        'compra': compra,
        'detalles': detalles_con_totales,
        'total_sin_impuesto': total_sin_impuesto,
        'total_impuesto': total_impuesto,
        'total_con_impuesto': total_con_impuesto,
        'profile': profile,
        'redirect_url': redirect_url,
    })

@login_required(login_url='/login/')
def imprimir_factura_venta(request, compra_id):
    # Verificar si el usuario tiene permiso para acceder a esta compra
    compra = get_object_or_404(Compra, id=compra_id, usuario=request.user)
    detalles = CompraDetalle.objects.filter(compra=compra)
    profile = Profile.objects.get(user=request.user)
    
    # Calcular totales
    total_sin_impuesto = sum(detalle.plato.precio * detalle.cantidad for detalle in detalles)
    total_impuesto = compra.total_impuesto
    total_con_impuesto = total_sin_impuesto + total_impuesto

    # Calcular el total por cada detalle
    detalles_con_totales = [
        {
            'plato': detalle.plato,
            'cantidad': detalle.cantidad,
            'precio_unitario': detalle.plato.precio,
            'total_detalle': detalle.plato.precio * detalle.cantidad
        }
        for detalle in detalles
    ]
    
    redirect_url = reverse('obtener_registros_venta')

    # Renderizar una página HTML que se imprimirá
    return render(request, 'ventas/imprimir_factura.html', {
        'compra': compra,
        'detalles': detalles_con_totales,
        'total_sin_impuesto': total_sin_impuesto,
        'total_impuesto': total_impuesto,
        'total_con_impuesto': total_con_impuesto,
        'profile': profile,
        'redirect_url': redirect_url,
    })

@login_required(login_url='/login/')
def imprimir_factura_venta_domicilio(request, compra_id):
    # Verificar si el usuario tiene permiso para acceder a esta compra
    compra = get_object_or_404(CompraDomicilio, id=compra_id, usuario=request.user)
    detalles = CompraDetalleDomicilio.objects.filter(compra=compra)
    profile = Profile.objects.get(user=request.user)
    
    # Calcular totales
    total_sin_impuesto = sum(detalle.plato.precio * detalle.cantidad for detalle in detalles)
    total_impuesto = compra.total_impuesto
    total_con_impuesto = total_sin_impuesto + total_impuesto

    # Calcular el total por cada detalle
    detalles_con_totales = [
        {
            'plato': detalle.plato,
            'cantidad': detalle.cantidad,
            'precio_unitario': detalle.plato.precio,
            'total_detalle': detalle.plato.precio * detalle.cantidad
        }
        for detalle in detalles
    ]
    
    redirect_url = reverse('obtener_registros_venta')

    # Renderizar una página HTML que se imprimirá
    return render(request, 'ventas/imprimir_factura_domicilio.html', {
        'compra': compra,
        'detalles': detalles_con_totales,
        'total_sin_impuesto': total_sin_impuesto,
        'total_impuesto': total_impuesto,
        'total_con_impuesto': total_con_impuesto,
        'profile': profile,
        'redirect_url': redirect_url,
    })

@login_required(login_url='/login/')
def enviar_factura_por_email(request, compra_id):
    compra = get_object_or_404(Compra, id=compra_id, usuario=request.user)
    detalles = CompraDetalle.objects.filter(compra=compra)
    
    destinatario = request.GET.get('email', 'direccion@example.com')
    profile = Profile.objects.get(user=request.user)

    # Calcular totales
    total_sin_impuesto = sum(detalle.plato.precio * detalle.cantidad for detalle in detalles)
    total_impuesto = compra.total_impuesto
    total_con_impuesto = total_sin_impuesto + total_impuesto

    # Calcular el total por cada detalle
    detalles_con_totales = [
        {
            'plato': detalle.plato,
            'cantidad': detalle.cantidad,
            'precio_unitario': detalle.plato.precio,
            'total_detalle': detalle.plato.precio * detalle.cantidad
        }
        for detalle in detalles
    ]

    # Renderizar el HTML de la factura
    html_content = render_to_string('ventas/imprimir_factura.html', {
        'compra': compra,
        'detalles': detalles_con_totales,
        'total_sin_impuesto': total_sin_impuesto,
        'total_impuesto': total_impuesto,
        'total_con_impuesto': total_con_impuesto,
        'profile': request.user.profile,
    })
    
    pdf_file = BytesIO()
    pisa.CreatePDF(BytesIO(html_content.encode('utf-8')), dest=pdf_file)
    pdf_file.seek(0)

    # Configurar el email
    email = EmailMessage(
        f'Factura de Venta - { profile.company }',
        'Apreciado cliente, Adjunto encontrarás la factura PDF.',
        settings.DEFAULT_FROM_EMAIL,
        [destinatario]
    )
    email.attach('factura.pdf', pdf_file.read(), 'application/pdf')
    email.send()
    messages.success(request, '¡Operación realizada con éxito!')
    return redirect('obtener_registros_venta')

@login_required(login_url='/login/')
def enviar_factura_por_email_domicilio(request, compra_id):
    compra = get_object_or_404(CompraDomicilio, id=compra_id, usuario=request.user)
    detalles = CompraDetalleDomicilio.objects.filter(compra=compra)
    
    destinatario = request.GET.get('email', 'direccion@example.com')

    # Calcular totales
    total_sin_impuesto = sum(detalle.plato.precio * detalle.cantidad for detalle in detalles)
    total_impuesto = compra.total_impuesto
    total_con_impuesto = total_sin_impuesto + total_impuesto

    # Calcular el total por cada detalle
    detalles_con_totales = [
        {
            'plato': detalle.plato,
            'cantidad': detalle.cantidad,
            'precio_unitario': detalle.plato.precio,
            'total_detalle': detalle.plato.precio * detalle.cantidad
        }
        for detalle in detalles
    ]

    # Renderizar el HTML de la factura
    html_content = render_to_string('ventas/imprimir_factura_domicilio.html', {
        'compra': compra,
        'detalles': detalles_con_totales,
        'total_sin_impuesto': total_sin_impuesto,
        'total_impuesto': total_impuesto,
        'total_con_impuesto': total_con_impuesto,
        'profile': request.user.profile,
    })
    
    pdf_file = BytesIO()
    pisa.CreatePDF(BytesIO(html_content.encode('utf-8')), dest=pdf_file)
    pdf_file.seek(0)

    # Configurar el email
    email = EmailMessage(
        'Factura de Compra',
        'Adjunto encontrarás la factura en formato PDF.',
        settings.DEFAULT_FROM_EMAIL,
        [destinatario]
    )
    email.attach('factura.pdf', pdf_file.read(), 'application/pdf')
    email.send()
    messages.success(request, '¡Operación realizada con éxito!')
    return redirect('obtener_registros_venta')

@login_required(login_url='/login/')
def estadisticas(request):
    usuario = request.user
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # Filtrar por fechas si se proporcionan
    if start_date and end_date:
        start_date = parse_date(start_date)
        end_date = parse_date(end_date)
        compra_filter = Compra.objects.filter(usuario=usuario, fecha_compra__range=[start_date, end_date])
        compra_detalle_filter = CompraDetalle.objects.filter(compra__usuario=usuario, compra__fecha_compra__range=[start_date, end_date])

        compra_filter_domicilio = CompraDomicilio.objects.filter(usuario=usuario, fecha_compra__range=[start_date, end_date])
        compra_detalle_filter_domicilio = CompraDetalleDomicilio.objects.filter(compra__usuario=usuario, compra__fecha_compra__range=[start_date, end_date])

    else:
        compra_filter = Compra.objects.filter(usuario=usuario)
        compra_detalle_filter = CompraDetalle.objects.filter(compra__usuario=usuario)
        compra_filter_domicilio = CompraDomicilio.objects.filter(usuario=usuario)
        compra_detalle_filter_domicilio = CompraDetalleDomicilio.objects.filter(compra__usuario=usuario)


    # Total de ventas
    total_ventas = compra_filter.aggregate(total=Sum('total'))['total'] or 0
    total_ventas_domicilio = compra_filter_domicilio.aggregate(total=Sum('total'))['total'] or 0

    # Ventas por tipo de pago
    ventas_por_tipo_pago = compra_filter.values('tipo_pago').annotate(total=Sum('total'))
    ventas_por_tipo_pago_dict = {compra['tipo_pago']: float(compra['total']) for compra in ventas_por_tipo_pago}
    ventas_por_tipo_pago_domicilio = compra_filter_domicilio.values('tipo_pago').annotate(total=Sum('total'))
    ventas_por_tipo_pago_dict_domicilio = {compra['tipo_pago']: float(compra['total']) for compra in ventas_por_tipo_pago_domicilio}

    # Platos más vendidos
    platos_vendidos = compra_detalle_filter.values('plato__nombre').annotate(cantidad_vendida=Sum('cantidad')).order_by('-cantidad_vendida')
    platos_mas_vendidos = {plato['plato__nombre']: plato['cantidad_vendida'] for plato in platos_vendidos}
    platos_vendidos_domicilio = compra_detalle_filter_domicilio.values('plato__nombre').annotate(cantidad_vendida=Sum('cantidad')).order_by('-cantidad_vendida')
    platos_mas_vendidos_domicilio = {plato['plato__nombre']: plato['cantidad_vendida'] for plato in platos_vendidos_domicilio}

    # Total de platos vendidos
    total_platos_vendidos = compra_detalle_filter.aggregate(total=Sum('cantidad'))['total'] or 0
    total_platos_vendidos_domicilio = compra_detalle_filter_domicilio.aggregate(total=Sum('cantidad'))['total'] or 0

    # Ventas por mes
    ventas_por_mes = compra_filter.annotate(month=ExtractMonth('fecha_compra')).values('month').annotate(total=Sum('total'))
    ventas_por_mes_dict = {}
    for compra in ventas_por_mes:
        month = compra['month']
        if 1 <= month <= 12:  # Verificar que el mes esté en el rango válido
            ventas_por_mes_dict[calendar.month_name[month]] = float(compra['total'])

    ventas_por_mes_domicilio = compra_filter_domicilio.annotate(month=ExtractMonth('fecha_compra')).values('month').annotate(total=Sum('total'))
    ventas_por_mes_dict_domicilio = {}
    for compra in ventas_por_mes_domicilio:
        month = compra['month']
        if 1 <= month <= 12:  # Verificar que el mes esté en el rango válido
            ventas_por_mes_dict_domicilio[calendar.month_name[month]] = float(compra['total'])

    context = {
        'total_ventas': total_ventas,
        'ventas_por_tipo_pago': ventas_por_tipo_pago_dict,
        'platos_mas_vendidos': platos_mas_vendidos,
        'total_platos_vendidos': total_platos_vendidos,
        'ventas_por_mes': ventas_por_mes_dict,
        'platos_nombres': json.dumps(list(platos_mas_vendidos.keys())),  # Serializar a JSON
        'platos_cantidades': json.dumps(list(platos_mas_vendidos.values())), # Serializar a JSON
        'tipos_pago': json.dumps(list(ventas_por_tipo_pago_dict.keys())),  # Serializar a JSON
        'ventas_tipos_pago': json.dumps(list(ventas_por_tipo_pago_dict.values())),
        'meses': json.dumps(list(ventas_por_mes_dict.keys())),
        'ventas_meses': json.dumps(list(ventas_por_mes_dict.values())),
        'total_ventas_domicilio': total_ventas_domicilio,                   # DESDE AQUI COMIENZAN LOS CONTEXT DE DOMICILIOS
        'ventas_por_tipo_pago_domicilio': ventas_por_tipo_pago_dict_domicilio,
        'platos_mas_vendidos_domicilio': platos_mas_vendidos_domicilio,
        'total_platos_vendidos_domicilio': total_platos_vendidos_domicilio,
        'ventas_por_mes_domicilio': ventas_por_mes_dict_domicilio,
        'platos_nombres_domicilio': json.dumps(list(platos_mas_vendidos_domicilio.keys())),  # Serializar a JSON
        'platos_cantidades_domicilio': json.dumps(list(platos_mas_vendidos_domicilio.values())), # Serializar a JSON
        'tipos_pago_domicilio_domicilio': json.dumps(list(ventas_por_tipo_pago_dict_domicilio.keys())),  # Serializar a JSON
        'ventas_tipos_pago_domicilio': json.dumps(list(ventas_por_tipo_pago_dict_domicilio.values())),
        'meses_domicilio': json.dumps(list(ventas_por_mes_dict_domicilio.keys())),
        'ventas_meses_domicilio': json.dumps(list(ventas_por_mes_dict_domicilio.values())),
    }

    return render(request, 'ventas/estadisticas.html', context)

def buscar_cliente_por_documento(request):
    documento = request.GET.get('documento', None)
    if documento:
        cliente = Cliente.objects.filter(documento=documento).first()
        if cliente:
            data = {
                'doc_cliente': cliente.documento,
                'nombre_cliente': cliente.nombre,
                'telefono_cliente': cliente.telefono,
                'direccion_cliente': cliente.direccion,
            }
            return JsonResponse(data)
    return JsonResponse({'error': 'Cliente no encontrado'}, status=404)

@login_required(login_url='/login/')
def buscar_clientes(request):
    term = request.GET.get('term', '')
    user = request.user  # Obtener el usuario actual desde el request

    # Filtro por documento o nombre
    clientes = Cliente.objects.filter(
        usuario=user,
        documento__icontains=term
    ) | Cliente.objects.filter(
        usuario=user,
        nombre__icontains=term
    )

    # Eliminar duplicados y ordenar resultados si es necesario
    clientes = clientes.distinct()

    results = [{'id': cliente.id, 'nombre': cliente.nombre, 'telefono': cliente.telefono, 'direccion': cliente.direccion, 'documento': cliente.documento} for cliente in clientes]
    return JsonResponse(results, safe=False)