from __future__ import unicode_literals
from django.shortcuts import render, redirect
from .forms import FormUsuario, FormUser
from .models import Usuario
from Dispositivo.models import Dispositivo
from Dispositivo.views import (walk, muchasimagenes, creardb, abortar,
                               monitoreosSNMP, muchosupdatedb, staff_required,
                               listadeso)
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from ObserviumProblem.settings import BASE_DIR
import pygeoip
import threading
import time
import os
from pysnmp.hlapi import (SnmpEngine, CommunityData, UdpTransportTarget,
                          getCmd, ContextData, ObjectType, ObjectIdentity)

gloc = pygeoip.GeoIP(BASE_DIR+'/database/GeoLiteCity.dat')
lista_oid = ['1.3.6.1.2.1.1.1.0', '1.3.6.1.2.1.2.1.0']


def consultaSNMP(dispositivos, oid):
    lista = []
    for dispositivo in dispositivos:
        errorIndication, errorStatus, errorIndex, varBinds = next(
            getCmd(SnmpEngine(),
                   CommunityData(dispositivo.Comunidad),
                   UdpTransportTarget((dispositivo.Ip, 161)),
                   ContextData(),
                   ObjectType(ObjectIdentity(oid[0])),
                   ObjectType(ObjectIdentity(oid[1])))
        )

        if errorIndication:
            resultado = ['error' for elemento in oid]
        elif errorStatus:
            resultado = ['error' for elemento in oid]
        else:
            resultado = [str(varBind[1]) for varBind in varBinds]
        lista.append([dispositivo.id, resultado])
    return lista


def sistemaop(lista):
    enlinea = 0
    fueralinea = 0
    tiposistema = [[elemento[0], tipo]
                   for elemento in lista for tipo in listadeso
                   if tipo in elemento[1][0]]
    for elemento in tiposistema:
        if elemento[1] != 'error':
            enlinea += 1
        else:
            fueralinea += 1
    return tiposistema, [len(lista), enlinea, fueralinea]


def listar_posiciones(dispositivos):
    lista_posiciones = []
    for dispositivo in dispositivos:
        addr_info = gloc.record_by_name(dispositivo.Ip_publica)
        longitude = addr_info['longitude']
        latitude = addr_info['latitude']
        data = "{lat:"+str(latitude)+", lng: "+str(longitude)+"}"
        lista_posiciones.append(data)
    return lista_posiciones


@staff_required(login_url="/")
@login_required(login_url='/')
def VistaUsuario(request):
    abortar.set_x(-1)
    puertos = [0, 0, 0, 0]
    mostrar = [0, 0]
    listanumerointerfaz = []
    listahilos = []
    listaimagenes = []
    listawalk = []
    form = FormUsuario()
    usuario = Usuario.objects.filter(Usuario_id=request.user.id)
    dispositivo = Dispositivo.objects.filter(
        Usuario_Dispositivo_id=request.user.id)
    lista = listar_posiciones(dispositivo)
    respuesta = consultaSNMP(dispositivo, lista_oid)
    for elemento in respuesta:
        if elemento[1][1] != 'error':
            listanumerointerfaz.append([elemento[0], elemento[1][1]])
            for tipomonitoreo in monitoreosSNMP:
                nombrecad = str(str(tipomonitoreo[0])+str(elemento[0])+'.rrd')
                if os.path.isfile(nombrecad) is False:
                    creardb(nombrecad, elemento)
                listahilos.append([elemento[0], tipomonitoreo[0],
                                   tipomonitoreo[1], tipomonitoreo[2]])
                listaimagenes.append([elemento[0], tipomonitoreo[0]])
    time.sleep(5)
    abortar.set_x(0)
    if listahilos != []:
        update = threading.Thread(
            name='hiloupdate',
            target=muchosupdatedb,
            args=(listahilos, ))
        update.daemon = True
        update.start()
    if listaimagenes != []:
        imagen = threading.Thread(
            name='hiloimagen',
            target=muchasimagenes,
            args=(listaimagenes, ))
        imagen.daemon = True
        imagen.start()
    lista2, resumen = sistemaop(respuesta)
    for elemento in lista2:
        if elemento[1] == 'error':
            mostrar[1] = 1
        else:
            mostrar[0] = 1
    listawalk = walk(dispositivo, '1.3.6.1.2.1.2.2.1', listanumerointerfaz)
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
    contexto = {'usuarios': usuario,
                'dispositivos': dispositivo,
                'form': form,
                'listar': lista,
                'lista': lista2,
                'resumen': resumen,
                'mostrar': mostrar,
                'puertos': puertos}
    return render(request,
                  'Usuario/usuario_vista.html',
                  contexto)


@staff_required(login_url="/")
@login_required(login_url='/')
def EditarUsuario(request, Id):
    usuario = Usuario.objects.get(Usuario_id=Id)
    user = User.objects.get(id=Id)
    dispositivo = Dispositivo.objects.filter(
        Usuario_Dispositivo_id=request.user.id)
    if request.method == 'GET':
        form = FormUsuario(instance=usuario)
        formdos = FormUser(instance=user)
    else:
        form = FormUsuario(instance=usuario)
        formdos = FormUser(instance=user)
        action = request.POST.get('action', None)
        if action == 'usuario':
            form = FormUsuario(request.POST, request.FILES,
                               instance=usuario)
            if form.is_valid():
                form.save()
            return redirect('Usuario:VistaUsuario')
        elif action == 'user':
            formdos = FormUser(request.POST, request.FILES,
                               instance=user)
            if formdos.is_valid():
                formdos.save()
            return redirect('Usuario:LoginUsuario')
    return render(request,
                  'Usuario/usuario_form.html',
                  {'form': form,
                   'formdos': formdos,
                   'dispositivos': dispositivo,
                   'usuario': usuario})


def LoginUsuario(request):
    abortar.set_x(0)
    if request.method == 'POST':
        username = request.POST.get('username', None)
        password = request.POST.get('password', None)
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('Usuario:VistaUsuario')
        else:
            return redirect('Usuario:VistaUsuario')
    context = {}
    return render(request, 'Usuario/login.html', context)


def logout_view(request):
    abortar.set_x(-1)
    dispositivos = Dispositivo.objects.filter(
        Usuario_Dispositivo_id=request.user.id)
    for dispositivo in dispositivos:
        for tipomonitoreo in monitoreosSNMP:
            nombrecad = str(str(tipomonitoreo[0])+str(dispositivo.id)+'.rrd')
            if os.path.isfile(nombrecad):
                os.remove(nombrecad)
            nombrexml = str(str(tipomonitoreo[0])+str(dispositivo.id)+'.xml')
            if os.path.isfile(nombrexml):
                os.remove(nombrexml)
            nombreimagen = str(
                "media/"+str(tipomonitoreo[0])+str(dispositivo.id)+'.png')
            if os.path.isfile(nombreimagen):
                os.remove(nombreimagen)
    logout(request)
    return redirect('Usuario:LoginUsuario')
