from django.contrib import admin
from .models import Reserva, Club, Pista, DetallesClub, Dimensiones

class DimensionesAdmin(admin.ModelAdmin):
    list_display = ('horas_disponibles')
# Register your models here.

admin.site.register(Reserva)
admin.site.register(Club)
admin.site.register(Pista)
admin.site.register(DetallesClub)
admin.site.register(Dimensiones, DimensionesAdmin)