from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', include('pages.urls')),
    path('mesas/', include('mesas.urls')),
    path('pagos/', include('pagos.urls')),
    path('arqueos/', include('arqueo.urls')),
    path('platos/', include('platos.urls')),
    path('ventas/', include('ventas.urls')),
    path('usuarios/', include('usuarios.urls')),
    path('pedidos/', include('pedidos.urls')),
    path('inventario/', include('inventario.urls')),
    path('admin/', admin.site.urls),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page='inicio'), name='logout'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
