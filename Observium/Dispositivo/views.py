# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from .forms import FormDispositivo
from Usuario.models import Usuario
from .models import Dispositivo
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from ObserviumProblem.settings import BASE_DIR
import rrdtool
import pygeoip
import os.path
import thread
import time
import sys
from pysnmp.hlapi import (getCmd,
                          SnmpEngine,
                          CommunityData,
                          UdpTransportTarget,
                          ContextData,
                          ObjectType,
                          ObjectIdentity,
                          nextCmd)


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
                   ObjectType(ObjectIdentity(oid[1])),
                   ObjectType(ObjectIdentity(oid[2])),
                   ObjectType(ObjectIdentity(oid[3])),
                   ObjectType(ObjectIdentity(oid[4])),
                   ObjectType(ObjectIdentity(oid[5])),
                   ObjectType(ObjectIdentity(oid[6])),
                   ObjectType(ObjectIdentity(oid[7])))
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
                superlista.append([dispositivo.id, numero[1], lista])
    return superlista


def consultaunicaSNMP(dispositivo, oid):
    resultado = 0
    errorIndication, errorStatus, errorIndex, varBinds = next(
        getCmd(SnmpEngine(),
               CommunityData(dispositivo.Comunidad),
               UdpTransportTarget((dispositivo.Ip, 161)),
               ContextData(),
               ObjectType(ObjectIdentity(oid))))
    if errorIndication:
        print(errorIndication)
        resultado = 0
    elif errorStatus:
        print('%s at %s' % (errorStatus.prettyPrint(),
                            errorIndex and varBinds[
                                int(errorIndex) - 1][0] or '?'))
        resultado = 0
    else:
        for varBind in varBinds:
            resultado = int(str(varBind[1]))
    return resultado


def sistemaop(lista):
    tiposistema = []
    for elemento in lista:
        if "Linux" in elemento[1]:
            tiposistema.append([elemento[0], "Linux"])
        elif "Windows" in elemento[1]:
            tiposistema.append([elemento[0], "Windows"])
        else:
            tiposistema.append([elemento[0], "error"])
    return tiposistema


def staff_required(login_url=None):
    return user_passes_test(lambda u: u.is_staff, login_url=login_url)


gloc = pygeoip.GeoIP(BASE_DIR+'/database/GeoLiteCity.dat')


def listar_posiciones(dispositivos):
    lista_posiciones = ()
    for dispositivo in dispositivos:
        addr_info = gloc.record_by_name(dispositivo.Ip_publica)
        longitude = addr_info['longitude']
        latitude = addr_info['latitude']
        data = "{lat:"+str(latitude)+", lng: "+str(longitude)+"}"
        lista_posiciones.append(data)
    return lista_posiciones


def generartabla(listawalk):
    superlista = []
    for dispositivo in listawalk:
        lista = []
        for i in range(int(dispositivo[1])):
            sublista = []
            for j in range(len(dispositivo[2])):
                sublista.append(dispositivo[2][j][i])
            lista.append(sublista)
        superlista.append([dispositivo[0], lista])
    return superlista


def creardb(dispositivo):
    ret = rrdtool.create(str("trafico"+str(dispositivo.id)+".rrd"),
                         str("--start"), str('N'), str("--step"), str('60'),
                         str("DS:inoctets:COUNTER:600:U:U"),
                         str("DS:outoctets:COUNTER:600:U:U"),
                         str("RRA:AVERAGE:0.5:6:700"),
                         str("RRA:AVERAGE:0.5:1:600"))
    if ret:
        print '************'
        print rrdtool.error()
        print '************'


def updatedb(dispositivo):
    total_input_traffic = 0
    total_output_traffic = 0
    while 1:
        total_input_traffic = int(
            consultaunicaSNMP(dispositivo, '1.3.6.1.2.1.2.2.1.10.3'))
        total_output_traffic = int(
            consultaunicaSNMP(dispositivo, '1.3.6.1.2.1.2.2.1.16.3'))
        valor = str("N:" + str(total_input_traffic) + ':' + str(
            total_output_traffic))
        print valor
        cadena1 = str("trafico"+str(dispositivo.id)+".rrd")
        rrdtool.update(cadena1, valor)
        rrdtool.dump(str("trafico"+str(dispositivo.id)+".rrd"),
                     str("trafico"+str(dispositivo.id)+".xml"))
        time.sleep(1)


def imagen(dispositivo):
    tiempo_actual = int(time.time())
    tiempo = tiempo_actual-300
    while 1:
        try:
            ret = rrdtool.graph(
                str("trafico"+str(dispositivo.id)+".png"), str("--start"),
                str(tiempo),
                str("--vertical-label=Bytes/s"),
                str("DEF:inoctets="+str("trafico"+str(dispositivo.id)+""
                                        ".rrd")+":inoctets:AVERAGE"),
                str("DEF:outoctets="+str("trafico"+str(dispositivo.id)+""
                                         ".rrd")+":outoctets:AVERAGE"),
                str("AREA:inoctets#00FF00:In traffic"),
                str("LINE1:outoctets#0000FF:Out traffic\r"))
            print ('**********************'+str(ret))
            time.sleep(30)
            print '***sigo vivo : '+str(dispositivo.Comunidad)
        except ValueError:
            print "Oops!  That was no valid number.  Try again..."


dispositivo = Dispositivo.objects.all()
for elemento in dispositivo:
    if consultaunicaSNMP(elemento, '1.3.6.1.2.1.2.2.1.16.3') != 0:
        if os.path.isfile(str(str(elemento.id)+'.rrd')):
            print '****** si hay'
        else:
            creardb(elemento)
            print '****** no hay'
for elemento in dispositivo:
    if consultaunicaSNMP(elemento, '1.3.6.1.2.1.2.2.1.16.3') != 0:
        thread.start_new_thread(updatedb, (elemento,))
        thread.start_new_thread(imagen, (elemento,))


@staff_required(login_url="/")
@login_required(login_url='/')
def VistaDispositivo(request):
    listanumerointerfaz = []
    listawalk = []
    lista = []
    dias = []
    dispositivo = Dispositivo.objects.all()
    usuario = Usuario.objects.all()
    lista_oid = ['1.3.6.1.2.1.1.1.0',
                 '1.3.6.1.2.1.1.3.0',
                 '1.3.6.1.2.1.1.5.0',
                 '1.3.6.1.2.1.1.4.0',
                 '1.3.6.1.2.1.1.6.0',
                 '1.3.6.1.2.1.2.1.0',
                 '1.3.6.1.2.1.2.2.1.10.3',
                 '1.3.6.1.2.1.2.2.1.16.3']
    respuesta = consultaSNMP(dispositivo, lista_oid)
    for elemento in respuesta:
        if elemento[1][1] != 'error':
            trans = int(elemento[1][1])
            hor = (int(trans/3600))
            minu = int((trans-(hor*3600))/60)
            seg = trans-((hor*3600)+(minu*60))
            dias.append([elemento[0],
                         (str(hor)+"h "+str(minu)+"m "+str(seg)+"s")])
        else:
            dias.append([elemento[0], 'no se puede calcular'])
    for elemento in respuesta:
        lista.append([elemento[0], elemento[1][0]])
    sis = sistemaop(lista)
    for elemento in respuesta:
        if elemento[1][5] != 'error':
            listanumerointerfaz.append([elemento[0], elemento[1][5]])
    listawalk = generartabla(walk(dispositivo,
                                  '1.3.6.1.2.1.2.2.1',
                                  listanumerointerfaz))
    contexto = {'usuarios': usuario,
                'dispositivos': dispositivo,
                'respuesta': respuesta,
                'lista': sis,
                'dias': dias,
                'listawalk': listawalk}
    return render(request,
                  'Dispositivo/dispositivo_vista.html',
                  contexto)


@staff_required(login_url="/")
@login_required(login_url='/')
def IndividualDispositivo(request, Id):
    usuario = Usuario.objects.all()
    dispositivos = Dispositivo.objects.all()
    lista_dispositivo = []
    lista = []
    dias = []
    dispositivo = Dispositivo.objects.get(id=Id)
    lista_dispositivo.append(dispositivo)
    lista_oid = ['1.3.6.1.2.1.1.1.0',
                 '1.3.6.1.2.1.1.3.0',
                 '1.3.6.1.2.1.1.5.0',
                 '1.3.6.1.2.1.1.4.0',
                 '1.3.6.1.2.1.1.6.0',
                 '1.3.6.1.2.1.2.1.0',
                 '1.3.6.1.2.1.2.2.1.10.3',
                 '1.3.6.1.2.1.2.2.1.16.3']
    respuesta = consultaSNMP(lista_dispositivo, lista_oid)
    for elemento in respuesta:
        lista.append([elemento[0], elemento[1][0]])
    sis = sistemaop(lista)
    for elemento in respuesta:
        if elemento[1][1] != 'error':
            trans = int(elemento[1][1])
            hor = (int(trans/3600))
            minu = int((trans-(hor*3600))/60)
            seg = trans-((hor*3600)+(minu*60))
            dias.append([elemento[0],
                         (str(hor)+"h "+str(minu)+"m "+str(seg)+"s")])
        else:
            dias.append([elemento[0], 'no se puede calcular'])
    contexto = {'usuarios': usuario,
                'dispositivos': dispositivos,
                'dispositivo': dispositivo,
                'respuesta': respuesta,
                'lista': sis,
                'dias': dias}
    return render(request,
                  'Dispositivo/dispositivo_individual.html',
                  contexto)


@staff_required(login_url="/")
@login_required(login_url='/')
def AgregarDispositivo(request):
    usuario = Usuario.objects.all()
    dispositivo = Dispositivo.objects.all()
    if request.method == 'POST':
        form = FormDispositivo(request.POST)
        if form.is_valid():
            form.save()
        return redirect('Dispositivo:VistaDispositivo')
    else:
        form = FormDispositivo()
        contexto = {'usuarios': usuario,
                    'dispositivos': dispositivo,
                    'form': form}
    return render(request,
                  'Dispositivo/dispositivo_agregar.html',
                  contexto)


@staff_required(login_url="/")
@login_required(login_url='/')
def EditarDispositivo(request, Id):
    dispositivo = Dispositivo.objects.get(id=Id)
    if request.method == 'GET':
        form = FormDispositivo(instance=dispositivo)
    else:
        form = FormDispositivo(request.POST,
                               request.FILES,
                               instance=dispositivo)
        if form.is_valid():
            form.save()
        return redirect('Dispositivo:VistaDispositivo')
    return render(request,
                  'Dispositivo/dispositivo_form.html',
                  {'form': form,
                   'dispositivo': dispositivo})


@staff_required(login_url="/")
@login_required(login_url='/')
def EliminarDispositivo(request, Id):
    dispositivo = Dispositivo.objects.get(id=Id)
    usuario = Usuario.objects.all()

    if request.method == 'POST':
        dispositivo.delete()
        return redirect('Dispositivo:VistaDispositivo')
    return render(request,
                  'Dispositivo/dispositivo_borrar.html',
                  {'dispositivo': dispositivo,
                   'usuario': usuario})
