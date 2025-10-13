from django.contrib import admin #importo de django el modulo admin
from django.urls import path, include #path me sirve para definir las rutas, include me sirve para incluir las urls de otras apps
from django.contrib.auth import views as auth_views #importo las vistas de autenticacion y las renombro como auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'), #template_name define la plantilla que se usara para el login, y name es el nombre de la ruta, que se puede invocar en otros lugares usando simplemente el nombre 'login'
    path('logout/', auth_views.LogoutView.as_view(), name='logout'), #en este caso no usa template_name porque por defecto ya esta seteado en registration/logged_out.html
    path('', include('asistencias.urls', namespace='asistencias')), # el '' indica la ruta raiz, y include me permite incluir las urls definidas en la app asistencias
    path('accounts/', include('allauth.urls')),    # registro/login/confirmación email
]

