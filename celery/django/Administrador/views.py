from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth.models import User

from Agente.views import staff_required
from Agente.models import Agente

from Observium.functions import (sistemaop, listar_posiciones, get_SNMP,
                                 walk_SNMP, listaWalk)

from .forms import FormAdministrador, FormUser
from .models import Administrador

listaGet = ['1.3.6.1.2.1.1.1.0']


@staff_required(login_url="/")
@login_required(login_url='/')
def VistaAdministrador(request):
    puertos = [0, 0, 0, 0]
    mostrar = [0, 0]
    administrador = Administrador.objects.filter(
        Administrador_id=request.user.id)
    agentes = Agente.objects.filter(
        Administrador_Agente_id=request.user.id)
    lista = listar_posiciones(agentes)
    respuesta = get_SNMP(agentes, listaGet)
    lista2, resumen = sistemaop(respuesta)
    for elemento in lista2:
        if elemento[1] == 'error':
            mostrar[1] = 1
        else:
            mostrar[0] = 1
    listawalk = walk_SNMP(agentes, listaWalk, 0)
    for elemento in listawalk:
        for puerto in elemento[2][7]:
            if puerto == '1':
                puertos[0] += 1
                puertos[1] += 1
            if puerto == '2':
                puertos[0] += 1
                puertos[2] += 1
            if puerto == '3':
                puertos[0] += 1
                puertos[3] += 1

    contexto = {'administradores': administrador,
                'agentes': agentes,
                'listar': lista,
                'lista': lista2,
                'resumen': resumen,
                'mostrar': mostrar,
                'puertos': puertos}

    return render(request,
                  'Administrador/administrador_vista.html',
                  contexto)


@staff_required(login_url="/")
@login_required(login_url='/')
def EditarAdministrador(request, Id):
    administrador = Administrador.objects.get(Administrador_id=Id)
    user = User.objects.get(id=Id)
    agente = Agente.objects.filter(
        Administrador_Agente_id=request.user.id)
    if request.method == 'GET':
        form = FormAdministrador(instance=administrador)
        formdos = FormUser(instance=user)
    else:
        form = FormAdministrador(instance=administrador)
        formdos = FormUser(instance=user)
        action = request.POST.get('action', None)
        if action == 'administrador':
            form = FormAdministrador(request.POST, request.FILES,
                                     instance=administrador)
            if form.is_valid():
                form.save()
            return redirect('VistaAdministrador')
        elif action == 'user':
            formdos = FormUser(request.POST, request.FILES,
                               instance=user)
            if formdos.is_valid():
                formdos.save()
            return redirect('LoginAdministrador')
    return render(request,
                  'Administrador/administrador_form.html',
                  {'form': form,
                   'formdos': formdos,
                   'agentes': agente,
                   'administrador': administrador})


def LoginAdministrador(request):
    if request.method == 'POST':
        username = request.POST.get('username', None)
        password = request.POST.get('password', None)
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            id = user.id
            administrador = Administrador.objects.filter(Administrador_id=id)
            for elemento in administrador:
                return redirect('VistaAdministrador')
            return redirect('MasDatos')
        else:
            return redirect('LoginAdministrador')
    context = {}
    return render(request, 'Administrador/login.html', context)


@login_required(login_url='/')
def logout_view(request):
    logout(request)
    return redirect('LoginAdministrador')


def Registrar(request):
        if request.method == 'POST':
            username = request.POST.get('Administrador', None)
            password = request.POST.get('password', None)
            first_name = request.POST.get('Nombre', None)
            last_name = request.POST.get('Apellido', None)
            email = request.POST.get('Email', None)
            is_staff = True
            user = authenticate(username=username, password=password)
            user = User.objects.create_user(
                username=username,
                password=password,
                first_name=first_name,
                last_name=last_name,
                email=email,
                is_staff=is_staff)
            user.save()
            login(request, user)
            return redirect('MasDatos')
        else:
            form = FormUser()
            contexto = {'form': form}
        return render(request,
                      'Administrador/administrador_registro.html',
                      contexto)


@login_required(login_url='/')
def MasDatos(request):
        if request.method == 'POST':
            form = FormAdministrador(request.POST, request.FILES)
            if form.is_valid():
                form.save()
            return redirect('VistaAdministrador')
        else:
            form = FormAdministrador()
            contexto = {'form': form}
        return render(request,
                      'Administrador/registrar_masdatos.html',
                      contexto)


def Contrato(request):
        return render(request,
                      'Administrador/contrato.html',
                      {})
