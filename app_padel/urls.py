from django.urls import path
from . import views



urlpatterns = [
    path('', views.index, name='index'),
    path('inicio/', views.inicio, name='inicio'),
    path('registro/', views.registro, name='registro'),
    path('logout/', views.logout_view, name='logout'),
    path('obtener_numero_pistas/', views.obtener_numero_pistas, name='obtener_numero_pistas'),
    path('crear_reserva/', views.crear_reserva, name='crear_reserva'),
    path('reserva_pista/<int:pista_id>/', views.reserva_pista, name='reservaPista'),
    path('mis_reservas/', views.misReservas, name='misReservas'),
    path('actualizar_reserva/<int:reserva_id>/', views.actualizarReserva, name='actualizarReserva'),
    path('delete/<int:reserva_id>/', views.delete_reserva, name='delete'),
    path('clubs_disponibles/', views.clubs_disponibles, name='clubsDisponibles'),
    path('usuario/', views.usuario, name='usuario')
]


