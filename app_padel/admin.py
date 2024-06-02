from django.contrib import admin
from .models import Reserva, Club, Pista, DetallesClub, Dimensiones
# Register your models here.

admin.site.register(Reserva)
admin.site.register(Club)
admin.site.register(Pista)
admin.site.register(DetallesClub)
admin.site.register(Dimensiones)