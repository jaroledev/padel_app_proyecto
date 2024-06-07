from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import ModelForm
from .models import Reserva,DetallesClub,Club, Pista

class RegistroForm(UserCreationForm):
    email = forms.EmailField(max_length=100)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

class ReservaForm(ModelForm):
    class Meta:
        model = Reserva
        fields = ['pista', 'hora_inicio', 'usuario']


class DetallesClubForm(forms.ModelForm):
    imagen_principal_file = forms.FileField(required=False, widget=forms.ClearableFileInput(attrs={'class': 'form-control'}))
    imagen_secundaria_file = forms.FileField(required=False, widget=forms.ClearableFileInput(attrs={'class': 'form-control'}))

    class Meta:
        model = DetallesClub
        fields = ['direccion', 'descripcion_larga', 'numero_pistas', 'imagen_principal', 'imagen_secundaria']
        widgets = {
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion_larga': forms.Textarea(attrs={'class': 'form-control'}),
            'numero_pistas': forms.NumberInput(attrs={'class': 'form-control'}),
            'imagen_principal': forms.ClearableFileInput(attrs={'accept': 'image/*'}),
            'imagen_secundaria': forms.ClearableFileInput(attrs={'accept': 'image/*'}),
        }

class ClubForm(forms.ModelForm):
    class Meta:
        model = Club
        fields = ['nombre', 'ciudad']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'ciudad': forms.TextInput(attrs={'class': 'form-control'}),
        }

class PistaForm(forms.ModelForm):
    class Meta:
        model = Pista
        fields = ['numero', 'descripcion']
        widgets = {
            'numero': forms.NumberInput(attrs={'class': 'form-control'}),
            'descripcion': forms.TextInput(attrs={'class': 'form-control'}),
        }
class ClubForm2(forms.ModelForm):
    usuario_admin = forms.ModelChoiceField(
        queryset=User.objects.all(), 
        widget=forms.Select(attrs={'class': 'form-control select2'}),
        required=True,
        label='Usuario administrador'
        )
    class Meta:
        model = Club
        fields = ['nombre', 'ciudad', 'usuario_admin']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'ciudad': forms.TextInput(attrs={'class': 'form-control'}),
        }