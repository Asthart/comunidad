# urls.py

from django.urls import path
from django.contrib.auth import views as auth_views
from comunidad import settings
from . import views
from django.conf.urls.static import static

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('crear_comunidad/', views.crear_comunidad, name='crear_comunidad'),
    path('comunidad/<int:pk>/', views.detalle_comunidad, name='detalle_comunidad'),
    path('comunidades/', views.lista_comunidades, name='lista_comunidades'),
    path('comunidad/<int:pk>/crear_proyecto/', views.crear_proyecto, name='crear_proyecto'),
    path('proyecto/<int:pk>/', views.detalle_proyecto, name='detalle_proyecto'),
    path('comunidad/<int:pk>/crear_desafio/', views.crear_desafio, name='crear_desafio'),
    path('desafio/<int:pk>/', views.detalle_desafio, name='detalle_desafio'),
    path('buscar/', views.buscar, name='buscar'),
    path('chat/<int:receptor_id>/', views.chat, name='chat'),
    path('ranking/', views.ranking_usuarios, name='ranking'),
    path('perfil/<str:username>/', views.perfil_usuario, name='perfil_usuario'),
    path('publicaciones/', views.obtener_publicaciones_no_vistas, name='publicaciones'),
    path('publicaciones/<int:publicacion_id>/vista/', views.registrar_publicacion_vista, name='registrar_publicacion_vista'),
    path('crear-publicacion/', views.crear_publicacion, name='crear_publicacion'),
    path('ws/chat/<int:receptor_id>/', views.ChatWS.as_asgi(), name='chat_ws'),
    path('aceptar-terminos/', views.aceptar_terminos, name='aceptar_terminos'),
    path('seguir/<pk>/', views.seguir_usuario, name='seguir_usuario'),
    path('dejar_de_seguir/<pk>/', views.dejar_de_seguir_usuario, name='dejar_de_seguir_usuario'),
    path('buscar_usuarios/', views.buscar_usuarios, name='buscar_usuarios'),
    path('actions/<int:action_id>/', views.update_user_points, name='action'),
    path('crear_concurso/', views.crear_concurso, name='crear_concurso'),
    path('concurso_resultados/', views.concurso_resultados, name='concurso_resultados'),
    path('campaign/<int:pk>/', views.detalle_campaign, name='detalle_campaign'),
    path('campaigns/', views.lista_campaigns, name='lista_campaigns'),
    path('puntuar/<int:pk>/<int:estrellas>/', views.puntuar_respuesta, name='puntuar_respuesta'),
    path('dar-like/<pk>/', views.dar_like, name='dar_like'),
    path('comentar/<pk>/', views.crear_comentario, name='crear_comentario'),
    path('publicacion/<int:pk>/like/', views.like, name='like_publicacion'),
    path('comentario/<int:pk>/like/', views.like_comentario, name='like_comentario'),
    path('guardar-donacion/', views.guardar_donacion, name='guardar_donacion'),
    path('chat-comunidad/<int:comunidad_id>/', views.chat_comunidad, name='chat_comunidad'),
    path('desafio/<int:pk>/guardar-donacion/', views.guardar_donacion, name='guardar_donacion'),
    path('editar-perfil/', views.editar_perfil, name='editar_perfil'),
    path('puntuar-desafio/<int:desafio_id>/<int:punto>/', views.puntuar_desafio, name='puntuar_desafio'),
    path('comunidades/<pk>/unirse/', views.unirse_comunidad, name='unirse_comunidad'),
    path('comunidad/<int:comunidad_id>/solicitar/', views.solicitar_membresia, name='solicitar_membresia'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)