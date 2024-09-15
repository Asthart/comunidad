# urls.py

from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('registrar/', views.registrar, name='registrar'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='inicio'), name='logout'),
    path('crear_comunidad/', views.crear_comunidad, name='crear_comunidad'),
    path('comunidad/<int:pk>/', views.detalle_comunidad, name='detalle_comunidad'),
    path('crear_proyecto/', views.crear_proyecto, name='crear_proyecto'),
    path('proyecto/<int:pk>/', views.detalle_proyecto, name='detalle_proyecto'),
    path('crear_desafio/', views.crear_desafio, name='crear_desafio'),
    path('desafio/<int:pk>/', views.detalle_desafio, name='detalle_desafio'),
    path('buscar/', views.buscar, name='buscar'),
    path('chat/<int:receptor_id>/', views.chat, name='chat'),
    path('ranking/', views.ranking_usuarios, name='ranking'),
    path('perfil/<str:username>/', views.perfil_usuario, name='perfil_usuario'),
]