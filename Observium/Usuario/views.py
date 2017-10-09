# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, redirect
from .forms import FormUsuario, FormUser
from .models import Usuario
from Dispositivo.models import Dispositivo
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from ObserviumProblem.settings import BASE_DIR
import rrdtool
import pygeoip
from pysnmp.hlapi import (getCmd,
                          SnmpEngine,
                          CommunityData,
                          UdpTransportTarget,
                          ContextData,
                          ObjectType,
                          ObjectIdentity,
                          nextCmd)

gloc = pygeoip.GeoIP(BASE_DIR+'/database/GeoLiteCity.dat')


def staff_required(login_url=None):
    return user_passes_test(lambda u: u.is_staff, login_url=login_url)


def walk(dispositivos, oid, numerointerfaz):
    superlista = []
    for numero in numerointerfaz:
        for dispositivo in dispositivos:
            if numero[0] == dispositivo.id:
                lista = []
                sublista = []
                for (errorIndication,
                     errorStatus,
                     errorIndex,
                     varBinds) in nextCmd(
                         SnmpEngine(),
                         CommunityData(dispositivo.Comunidad),
                         UdpTransportTarget((dispositivo.Ip, 161)),
                         ContextData(),
                         ObjectType(ObjectIdentity(oid))):
                            if errorIndication:
                                print(errorIndication)
                                break
                            elif errorStatus:
                                print('%s at %s' % (errorStatus.prettyPrint(),
                                                    errorIndex and varBinds[
                                                        int(errorIndex) - 1]
                                                    [0] or '?'))
                                break
                            else:
                                for dato in varBinds:
                                    if oid == str(dato[0])[:len(oid)]:
                                        sublista.append(str(dato[1]))
                                        if len(sublista) == int(numero[1]):
                                            lista.append(sublista)
                                            sublista = []
                                    else:
                                        varBinds = -1
                                        break
                                if varBinds == -1:
                                    break
                superlista.append([dispositivo.id, lista])
    return superlista


def consultaSNMP(dispositivos, oid):
    lista = []
    for dispositivo in dispositivos:
        resultado = []
        errorIndication, errorStatus, errorIndex, varBinds = next(
            getCmd(SnmpEngine(),
                   CommunityData(dispositivo.Comunidad),
                   UdpTransportTarget((dispositivo.Ip, 161)),
                   ContextData(),
                   ObjectType(ObjectIdentity(oid[0])),
                   ObjectType(ObjectIdentity(oid[1])))
        )

        if errorIndication:
            print(errorIndication)
            for elemento in oid:
                resultado.append('error')
        elif errorStatus:
            print('%s at %s' % (errorStatus.prettyPrint(),
                                errorIndex and varBinds[
                                    int(errorIndex) - 1][0] or '?'))
            for elemento in oid:
                resultado.append('error')
        else:
            for varBind in varBinds:
                resultado.append(str(varBind[1]))
        lista.append([dispositivo.id, resultado])
    return lista


def sistemaop(lista):
    enlinea = 0
    fueralinea = 0
    tiposistema = []
    for elemento in lista:
        if "Linux" in elemento[1][0]:
            tiposistema.append([elemento[0], "Linux"])
            enlinea += 1
        elif "Windows" in elemento[1][0]:
            tiposistema.append([elemento[0], "Windows"])
            enlinea += 1
        elif "error" == elemento[1][0]:
            fueralinea += 1
            tiposistema.append([elemento[0], "error"])
        elif "otrosis" == elemento[1][0]:
            enlinea += 1
            tiposistema.append([elemento[0], "otrosis"])
    resumen = [len(lista), enlinea, fueralinea]
    return tiposistema, resumen


def listar_posiciones(dispositivos):
    lista_posiciones = []
    for dispositivo in dispositivos:
        addr_info = gloc.record_by_name(dispositivo.Ip_publica)
        longitude = addr_info['longitude']
        latitude = addr_info['latitude']
        data = "{lat:"+str(latitude)+", lng: "+str(longitude)+"}"
        lista_posiciones.append(data)
    return lista_posiciones


def creardb(dispositivo):
    ret = rrdtool.create(str(str(dispositivo.id)+".rrd"), str("--start"),
                         str('N'), str("--step"), str('60'),
                         str("DS:inoctets:COUNTER:600:U:U"),
                         str("DS:outoctets:COUNTER:600:U:U"),
                         str("RRA:AVERAGE:0.5:6:700"),
                         str("RRA:AVERAGE:0.5:1:600"))
    if ret:
        print '************'
        print rrdtool.error()
        print '************'


@staff_required(login_url="/")
@login_required(login_url='/')
def VistaUsuario(request):
        mostrar = [0, 0]
        listanumerointerfaz = []
        listawalk = []
        puertos = [0, 0, 0, 0]
        form = FormUsuario()
        usuario = Usuario.objects.all()
        dispositivo = Dispositivo.objects.all()
        lista = listar_posiciones(dispositivo)
        lista_oid = ['1.3.6.1.2.1.1.1.0',
                     '1.3.6.1.2.1.2.1.0']
        respuesta = consultaSNMP(dispositivo, lista_oid)
        for elemento in respuesta:
            if elemento[1][1] != 'error':
                listanumerointerfaz.append([elemento[0], elemento[1][1]])
        lista2, resumen = sistemaop(respuesta)
        for elemento in lista2:
            if elemento[1] == 'error':
                mostrar[1] = 1
            else:
                mostrar[0] = 1
        listawalk = walk(dispositivo, '1.3.6.1.2.1.2.2.1', listanumerointerfaz)
        for elemento in listawalk:
            for puerto in elemento[1][7]:
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
    dispositivo = Dispositivo.objects.all()
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
            return redirect('Usuario:VistaUsuario')
    return render(request,
                  'Usuario/usuario_form.html',
                  {'form': form,
                   'formdos': formdos,
                   'dispositivos': dispositivo,
                   'usuario': usuario})


def LoginUsuario(request):
    if request.method == 'POST':
        username = request.POST.get('username', None)
        password = request.POST.get('password', None)
        user = authenticate(username=username, password=password)
        login(request, user)
        return redirect('Usuario:VistaUsuario')
    context = {}
    return render(request, 'Usuario/login.html', context)
