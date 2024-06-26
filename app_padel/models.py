from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.
class Club(models.Model):
    nombre = models.CharField(max_length=100)
    ciudad = models.CharField(max_length=200)
    activo = models.BooleanField(default=1)
    usuario_admin = models.ForeignKey(User,on_delete=models.CASCADE)
    
    def __str__(self):
        return self.nombre


class Pista(models.Model):
    club_admin = models.ForeignKey(Club,related_name='pistas', on_delete=models.CASCADE)
    numero = models.IntegerField()
    descripcion = models.CharField(max_length=100, default="")
    activa = models.BooleanField(default=1)

    def __str__(self):
        return f"Pista {self.numero} - {self.descripcion} - {self.club_admin.nombre}"


class Reserva(models.Model):
    pista = models.ForeignKey(Pista, on_delete=models.CASCADE)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    hora_inicio = models.DateTimeField()
    hora_fin = models.DateTimeField()
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    activa = models.BooleanField(default=1)

    def __str__(self):
        return f"Reserva de {self.usuario.username} en {self.pista} de {self.hora_inicio} a {self.hora_fin}"


class Dimensiones(models.Model):
    horas_disponibles = models.CharField(max_length=50)

    class Meta:
        verbose_name = "Hora Disponible"
        verbose_name_plural = "Horas Disponibles"
        
    def __str__(self):
        return self.horas_disponibles

class DetallesClub(models.Model):
    club = models.OneToOneField(Club, on_delete=models.CASCADE, primary_key=True,related_name='detalles')
    direccion = models.CharField(max_length=255)
    descripcion_larga = models.TextField()
    numero_pistas = models.IntegerField()
    imagen_principal = models.TextField()
    imagen_secundaria = models.TextField()

    def __str__(self):
        return self.club.nombre