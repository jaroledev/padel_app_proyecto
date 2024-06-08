from django.urls import path
from . import views



urlpatterns = [
    path('', views.login_app, name='login'),
    path('login/', views.login_app, name='login'),
    path('inicio/', views.inicio, name='inicio'),
    path('registro/', views.registro, name='registro'),
    path('logout/', views.logout_view, name='logout'),
    path('crear_reserva/', views.crear_reserva, name='crear_reserva'),
    path('reserva_pista/<int:pista_id>/', views.reserva_pista, name='reservaPista'),
    path('mis_reservas/', views.misReservas, name='misReservas'),
    path('delete/<int:reserva_id>/', views.delete_reserva, name='delete'),
    path('clubs_disponibles/', views.clubs_disponibles, name='clubsDisponibles'),
    path('usuario/', views.usuario, name='usuario'),
    path('gestionar_detalles_club/<int:club_id>/', views.gestionar_detalles_club, name='gestionar_detalles_club'),
    path('modificar_club/<int:club_id>/', views.modificar_club, name='modificar_club'),
    path('administrar_club/', views.administrar_club, name='administrar_club'),
    path('crear_club/', views.crear_club, name='crearClub'),
    path('buscar_usuarios/', views.buscar_usuarios, name='buscar_usuarios'),
]


