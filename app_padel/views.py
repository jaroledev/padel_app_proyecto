from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from .forms import RegistroForm, ReservaForm,DetallesClubForm, ClubForm, ClubForm2, PistaForm
from .models import Club, Pista, Reserva , DetallesClub , Dimensiones
from django.http import JsonResponse,HttpResponse
from .funciones import convert_base64_to_image,convert_image_to_base64
from django.utils import timezone
from datetime import datetime, timedelta

def superuser_required(view_func):
    return user_passes_test(lambda u: u.is_superuser, login_url='inicio')(view_func)

def home(request):
    return render(request, 'app_padel/home.html')


def login_app(request):
    if request.method == 'POST':
        # Verifica si el campo 'username' está presente en el formulario
        if 'username' in request.POST:
            # Resto del código para autenticar al usuario, etc.
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                # Redirige al usuario a una página de inicio o a donde quieras después del inicio de sesión
                return redirect('inicio')
            else:
                # Si las credenciales son inválidas, muestra un mensaje de error
                messages.error(request, 'Nombre de usuario o contraseña incorrectos.')
                return render(request, 'app_padel/login.html', {'error': "Usuario o Contraseña incorrectos"})
    return render(request, 'app_padel/login.html')


@login_required
def inicio(request):
    vars = {}
    user = request.user
    if request.method == 'POST':
        form = ReservaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('inicio')
    if 'username' in request.POST:
        if request.POST['username']:
            vars['username'] = request.POST['username']
        else:
            return login_app
    vars['user'] = user
    clubs = Club.objects.all()
    club = Club.objects.filter(usuario_admin_id = user.id)
    if club.exists():
        vars['club'] = club[0]
    else:
        vars['club'] = False
    vars['clubs'] = clubs
    form = ReservaForm()
    vars['form'] = form
    return render(request, 'app_padel/inicio.html', vars)

@login_required
def usuario(request):
    usuario_actual = request.user
    context = {
        'usuario': usuario_actual,
    }
    return render(request, 'app_padel/usuario.html', context)


def registro(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '¡Registro exitoso! Por favor, inicia sesión.')
            return redirect('login')
    else:
        form = RegistroForm()
    return render(request, 'app_padel/registro.html', {'form': form})


def logout_view(request):
    # Cierra la sesión del usuario
    logout(request)
    # Redirige a la página de inicio o a donde desees después del cierre de sesión
    return redirect('login')


@login_required
def crear_reserva(request):
    horas_dim = Dimensiones.objects.all()
    horas_list = horas_dim.values_list('horas_disponibles', flat=True).order_by('horas_disponibles')
    horas = []
    for h in horas_list:
        horas.append(h)
    horas.sort()
    ciudades = Club.objects.values('ciudad').distinct()
    hoy = timezone.now().date().isoformat()
    ahora = timezone.now()

    if request.method == "POST":
        fecha = request.POST.get('fecha')
        hora = request.POST.get('hora')
        ciudad = request.POST.get('ciudad', '')

        if not fecha or not hora:
            return render(request, 'app_padel/nuevaReserva.html', {'horas': horas, 'ciudades': ciudades, 'hoy': hoy, 'error': 'Debe seleccionar una fecha y una hora'})
        
        # Verificación del lado del servidor para fecha en el pasado
        if fecha and timezone.datetime.strptime(fecha, '%Y-%m-%d').date() < timezone.now().date():
            return render(request, 'app_padel/nuevaReserva.html', {'horas': horas, 'ciudades': ciudades, 'hoy': hoy, 'error': 'Debe seleccionar una fecha igual o superior al día de hoy'})

        # Verificación del lado del servidor para hora en el pasado
        fecha_hora = f"{fecha} {hora}"
        fecha_hora_dt = timezone.datetime.strptime(fecha_hora, '%Y-%m-%d %H:%M')
        fecha_hora_dt_aware = timezone.make_aware(fecha_hora_dt, timezone.get_current_timezone())

        if fecha_hora_dt_aware < ahora:
            return render(request, 'app_padel/nuevaReserva.html', {'horas': horas, 'ciudades': ciudades, 'hoy': hoy, 'error': 'Debe seleccionar una hora igual o superior a la hora actual'})

        fecha_hora_dt_aware_inicio = fecha_hora_dt_aware - timedelta(minutes=90)
        fecha_hora_dt_aware_fin = fecha_hora_dt_aware + timedelta(minutes=90)

        # Filtrar reservas activas para la fecha y hora seleccionadas
        reservas = Reserva.objects.filter(hora_inicio__gt=fecha_hora_dt_aware_inicio, hora_inicio__lt=fecha_hora_dt_aware_fin, activa=True)
        
        # Obtener pistas no reservadas
        pistas_reservadas = reservas.values_list('pista_id', flat=True)
        pistas_disponibles = Pista.objects.exclude(id__in=pistas_reservadas)

        pistas_ocupadas = []
        for pista in pistas_reservadas:
            pistas_ocupadas.append(pista)

        if ciudad != '-1':
            clubs = Club.objects.filter(ciudad__icontains=ciudad, pistas__in=pistas_disponibles).distinct()
        else:
            clubs = Club.objects.filter(pistas__in=pistas_disponibles).distinct()

        return render(request, 'app_padel/nuevaReserva.html', {
            'horas': horas,
            'clubs': clubs,
            'fecha': fecha,
            'hora': hora,
            'ciudad': ciudad,
            'ciudades': ciudades, 
            'hoy': hoy
        })

    return render(request, 'app_padel/nuevaReserva.html', {'horas': horas, 'ciudades': ciudades, 'hoy': hoy})


def reserva_pista(request, pista_id):
    pista = get_object_or_404(Pista, id=pista_id)

    if request.method == 'POST':
        fecha = request.POST.get('fecha')
        hora = request.POST.get('hora')
        fecha_hora = f"{fecha} {hora}"
        fecha_hora_dt = timezone.datetime.strptime(fecha_hora, '%Y-%m-%d %H:%M')
        hora_fin =  fecha_hora_dt + timedelta(minutes=90)
        # Crear la reserva
        Reserva.objects.create(
            pista=pista,
            usuario=request.user,
            hora_inicio=fecha_hora_dt,
            hora_fin = hora_fin,
            created = datetime.now(),
            activa=True
        )
        return redirect('misReservas')
    fecha = request.GET.get('fecha')
    hora = request.GET.get('hora')
    return render(request, 'app_padel/reservaPista.html', {'pista': pista ,'fecha': fecha, 'hora': hora })

def obtener_numero_pistas(request):
    if request.method == 'GET' and 'club_id' in request.GET:
        club_id = request.GET['club_id']
        club_id_n = int(club_id)
        if club_id_n > 0:
            numero_pistas = Pista.objects.filter(club_id=club_id).count()
            return JsonResponse({'numero_pistas': numero_pistas})
    else:
        return JsonResponse({'error': 'No se proporcionó el ID del club'})


def misReservas(request):
    # Obtener todas las reservas del usuario actual
    fecha_actual = datetime.now()
    reservas_activas = Reserva.objects.filter(usuario=request.user).filter(activa=True).filter(hora_inicio__gt=fecha_actual)
    reservas_historico = Reserva.objects.filter(usuario=request.user).filter(activa=True).filter(hora_inicio__lt=fecha_actual)
    return render(request, 'app_padel/misReservas.html', {'reservas_activas': reservas_activas,'reservas_historico': reservas_historico})

def delete_reserva(request, reserva_id):
    # Obtener la reserva a eliminar
    reserva = get_object_or_404(Reserva, pk=reserva_id)

    # Cambiar el valor de 'activa' a False
    reserva.activa = False
    reserva.save()
    return misReservas(request)

def gestionar_detalles_club(request, club_id):
    club = get_object_or_404(Club, id=club_id)
    detalles_club, created = DetallesClub.objects.get_or_create(club=club)

    if request.method == 'POST':
        form = DetallesClubForm(request.POST, request.FILES, instance=detalles_club)
        if form.is_valid():
            if 'imagen_principal_file' in request.FILES:
                detalles_club.imagen_principal = convert_image_to_base64(request.FILES['imagen_principal_file'])
            if 'imagen_secundaria_file' in request.FILES:
                detalles_club.imagen_secundaria = convert_image_to_base64(request.FILES['imagen_secundaria_file'])
            form.save()
            return redirect('administrar_club')
    else:
        form = DetallesClubForm(instance=detalles_club)
    
    context = {
        'club': club,
        'form': form,
        'detalles_club': detalles_club
    }
    return render(request, 'app_padel/detallesClub.html', context)

def clubs_disponibles(request):
    clubs = Club.objects.all()
    ciudades = {}

    for club in clubs:
        ciudad = club.ciudad.split(',')[-1].strip()
        if ciudad not in ciudades:
            ciudades[ciudad] = []
        ciudades[ciudad].append(club)

    context = {
        'ciudades': ciudades,
        'clubs': clubs
    }
    return render(request, 'app_padel/clubsDisponibles.html', context)

@login_required
def administrar_club(request):
    usuario = request.user
    try:
        club = Club.objects.get(usuario_admin=usuario.id)
    except Club.DoesNotExist:
        # Manejar el caso donde el usuario no es administrador de ningún club
        return render(request, 'administrarClub.html', {'error': 'No administras ningún club.'})

    fecha_seleccionada = request.GET.get('fecha')
    reservas_agrupadas = {}

    if fecha_seleccionada:
        fecha = timezone.datetime.strptime(fecha_seleccionada, '%Y-%m-%d').date()
        reservas = Reserva.objects.filter(pista__club=club, hora_inicio__date=fecha, activa=True).order_by('pista')

        # Agrupar reservas por pista
        for reserva in reservas:
            pista = reserva.pista
            if pista not in reservas_agrupadas:
                reservas_agrupadas[pista] = []
            reservas_agrupadas[pista].append(reserva)

    context = {
        'fecha_seleccionada': fecha_seleccionada,
        'reservas_agrupadas': reservas_agrupadas,
        'club':club
    }
    return render(request, 'app_padel/administrarClub.html', context)

@login_required
def modificar_club(request, club_id):
    club_admin = get_object_or_404(Club, id=club_id)

    if request.method == 'POST':
        if 'guardar_club' in request.POST:
            club_form = ClubForm(request.POST, instance=club_admin)
            if club_form.is_valid():
                club_form.save()
                return redirect('modificar_club', club_id=club_id)
        elif 'agregar_pista' in request.POST:
            pista_form = PistaForm(request.POST)
            if pista_form.is_valid():
                nueva_pista = pista_form.save(commit=False)
                nueva_pista.club_admin = club_admin
                nueva_pista.save()
                return redirect('modificar_club', club_id=club_id)
        elif 'eliminar_pista' in request.POST:
            pista_id = request.POST.get('pista_id')
            Pista.objects.filter(id=pista_id).delete()
            return redirect('modificar_club', club_id=club_id)
    else:
        club_form = ClubForm(instance=club_admin)
        pista_form = PistaForm()

    pistas = Pista.objects.filter(club_admin=club_admin)

    context = {
        'club_form': club_form,
        'pista_form': pista_form,
        'club_admin': club_admin,
        'pistas': pistas,
    }
    return render(request, 'app_padel/modificarClub.html', context)

@login_required(login_url='login')
@superuser_required
def crear_club(request):
    if request.method == 'POST':
        form = ClubForm2(request.POST)
        if form.is_valid():
            club = form.save(commit=False)
            club.save()
            return redirect('clubsDisponibles')  # Redirige a la vista que lista los clubes
    else:
        form = ClubForm2()
    return render(request, 'app_padel/crearClub.html', {'form': form})

def buscar_usuarios(request):
    query = request.GET.get('q', '')
    usuarios = User.objects.filter(username__icontains=query).exclude(id__in=Club.objects.values_list('usuario_admin', flat=True))
    results = [{'id': user.id, 'username': user.username} for user in usuarios]
    return JsonResponse(results, safe=False)