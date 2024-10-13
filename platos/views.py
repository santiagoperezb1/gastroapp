# platos/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import PlatoForm, CategoriaForm
from .models import Plato, Categoria
from usuarios.models import Profile
from django.contrib.auth.models import User
import qrcode
from io import BytesIO
import base64

@login_required(login_url='/login/')
def crear_plato(request):
    if request.method == 'POST':
        form = PlatoForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            plato = form.save(commit=False)
            plato.usuario = request.user  # Asignar el usuario actual
            plato.save()
            return redirect('listar_platos')  # Redirige a la lista de platos o donde desees
    else:
        form = PlatoForm(user=request.user)
    return render(request, 'platos/crear_plato.html', {'form': form})

@login_required(login_url='/login/')
def eliminar_plato(request, plato_id):
    plato = get_object_or_404(Plato, pk=plato_id, usuario=request.user)
    if request.method == 'POST':
        plato.delete()
        return redirect('listar_platos')
    return render(request, 'platos/eliminar_plato.html', {'plato': plato})

@login_required(login_url='/login/')
def listar_platos(request):
    categorias = Categoria.objects.filter(usuario=request.user)
    platos_por_categoria = {categoria: categoria.platos.all() for categoria in categorias}
    # URL del menú digital
    url_menu_digital = request.build_absolute_uri(f"/platos/menu_digital/{request.user.id}/")
    
    # Generar el código QR
    qr_img = qrcode.make(url_menu_digital)
    buffered = BytesIO()
    qr_img.save(buffered, format="PNG")
    qr_code_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')

    return render(request, 'platos/listar_platos.html', {
        'platos_por_categoria': platos_por_categoria,
        'qr_code': qr_code_base64,
    })

@login_required(login_url='/login/')
def actualizar_plato(request, plato_id):
    plato = get_object_or_404(Plato, id=plato_id, usuario=request.user)
    if request.method == 'POST':
        form = PlatoForm(request.POST, request.FILES, instance=plato, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('listar_platos')
    else:
        form = PlatoForm(instance=plato, user=request.user)
    return render(request, 'platos/actualizar_plato.html', {'form': form, 'plato': plato})

@login_required(login_url='/login/')
def gestionar_categorias(request):
    usuario = request.user
    categorias = Categoria.objects.filter(usuario=usuario).order_by('nombre')

    if request.method == 'POST':
        if 'create' in request.POST:
            # Manejar la creación de una nueva categoría
            form = CategoriaForm(request.POST)
            if form.is_valid():
                nueva_categoria = form.save(commit=False)  # No guarda inmediatamente
                nueva_categoria.usuario = usuario  # Asigna el usuario actual
                nueva_categoria.save()
                return redirect('gestionar_categorias')
        elif 'update' in request.POST:
            # Manejar la actualización de una categoría existente
            categoria_id = request.POST.get('categoria_id')
            categoria = get_object_or_404(Categoria, id=categoria_id)
            form = CategoriaForm(request.POST, instance=categoria)
            if form.is_valid():
                form.save()
                return redirect('gestionar_categorias')
        elif 'delete' in request.POST:
            # Manejar la eliminación de una categoría
            categoria_id = request.POST.get('categoria_id')
            categoria = get_object_or_404(Categoria, id=categoria_id)
            categoria.delete()
            return redirect('gestionar_categorias')
    else:
        form = CategoriaForm()

    return render(request, 'platos/gestionar_categorias.html', {
        'form': form,
        'categorias': categorias
    })

def menu_digital(request, user_id):
    usuario = get_object_or_404(User, id=user_id)
    platos_por_categoria = {}
    
    # Filtrar los platos que pertenecen a este usuario
    categorias = Plato.objects.filter(usuario=usuario).values('categoria').distinct()

    # Crear un diccionario de categorías con nombre como clave
    for categoria in categorias:
        categoria_obj = Categoria.objects.get(id=categoria['categoria'])  # Suponiendo que tienes un modelo Categoria
        platos = Plato.objects.filter(usuario=usuario, categoria=categoria_obj)
        platos_por_categoria[categoria_obj] = platos
    
    # Obtener el perfil del usuario
    perfil = get_object_or_404(Profile, user=usuario)

    # Ordenar las categorías: las demás alfabéticamente y 'bebidas' al final
    sorted_platos_por_categoria = dict(sorted(
        platos_por_categoria.items(),
        key=lambda x: (x[0].nombre.lower() == 'bebidas', x[0].nombre.lower())
    ))

    # Generar URL del menú digital
    url = request.build_absolute_uri(f'/platos/menu_digital/{user_id}/')
    
    # Generar código QR
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    
    # Guardar el código QR en un buffer
    buffer = BytesIO()
    img.save(buffer)
    buffer.seek(0)
    
    # Convertir la imagen a base64
    qr_code_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

    return render(request, 'platos/menu_digital.html', {'platos_por_categoria': sorted_platos_por_categoria, 'perfil': perfil, 'qr_code': qr_code_base64})
