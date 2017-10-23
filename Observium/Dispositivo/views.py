# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from .forms import FormDispositivo
from Usuario.models import Usuario
from .models import Dispositivo
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from rrdtool import ProgrammingError, OperationalError
import rrdtool
import logging
import time
import os
import threading
from pysnmp.hlapi import (getCmd, SnmpEngine, CommunityData, nextCmd,
                          UdpTransportTarget, ContextData, ObjectType,
                          ObjectIdentity)

monitoreosSNMP = [['trafico',
                   '1.3.6.1.2.1.2.2.1.10.3',
                   '1.3.6.1.2.1.2.2.1.16.3',
                   "Tráfico de interfaz"],
                  ['segmentostcp',
                   '1.3.6.1.2.1.6.10.0',
                   '1.3.6.1.2.1.6.11.0',
                   "Segmentos TCP"],
                  ['datagramaUDP',
                   '1.3.6.1.2.1.7.1.0',
                   '1.3.6.1.2.1.7.4.0',
                   "Datagramas UDP"],
                  ['paquetes',
                   '1.3.6.1.2.1.11.1.0',
                   '1.3.6.1.2.1.11.2.0',
                   "Paquetes SNMP"]]

lista_oid = ['1.3.6.1.2.1.1.1.0',
             '1.3.6.1.2.1.1.3.0',
             '1.3.6.1.2.1.1.5.0',
             '1.3.6.1.2.1.1.4.0',
             '1.3.6.1.2.1.1.6.0',
             '1.3.6.1.2.1.2.1.0',
             '1.3.6.1.2.1.2.2.1.10.3',
             '1.3.6.1.2.1.2.2.1.16.3']

listadeso = ["Linux", "Windows", "error"]
logging.basicConfig(level=logging.INFO,
                    format='[%(levelname)s] (%(threadName)-s) %(message)s')


class Matarhilo:

    def __init__(self, x):
        self.__x = x

    def get_x(self):
        return self.__x

    def set_x(self, x):
        self.__x = x


abortar = Matarhilo(0)


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
                                break
                            elif errorStatus:
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


def consultaSNMP(dispositivos, oid):
    lista = []
    for dispositivo in dispositivos:
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
            resultado = ['error' for elemento in oid]
        elif errorStatus:
            resultado = ['error' for elemento in oid]
        else:
            resultado = [str(varBind[1]) for varBind in varBinds]
        lista.append([dispositivo.id, resultado])
    return lista


def consultaunicaSNMP(dispositivo, oid):
    errorIndication, errorStatus, errorIndex, varBinds = next(
        getCmd(SnmpEngine(),
               CommunityData(dispositivo.Comunidad),
               UdpTransportTarget((dispositivo.Ip, 161)),
               ContextData(), ObjectType(ObjectIdentity(oid))))
    if errorIndication:
        resultado = 0
    elif errorStatus:
        resultado = 0
    else:
        for varBind in varBinds:
            resultado = int(str(varBind[1]))
    return resultado


def creardb(nombrecad, dispositivo):
        ret = rrdtool.create(
            str(nombrecad), str("--start"),
            str('N'), str("--step"), str('60'),
            str("DS:inoctets:COUNTER:600:U:U"),
            str("DS:outoctets:COUNTER:600:U:U"),
            str("RRA:AVERAGE:0.5:1:600"))
        if ret:
            logging.warning(
                'Error al Crear la BD: '+nombrecad + ''
                '\t Dispositivo: '+dispositivo)


def muchosupdatedb(listahilos):
    total_input_traffic = 0
    total_output_traffic = 0
    while 1:
        for hilos in listahilos:
            dispositivo = Dispositivo.objects.get(id=hilos[0])
            total_input_traffic = int(
                consultaunicaSNMP(dispositivo, str(hilos[2])))
            total_output_traffic = int(
                consultaunicaSNMP(dispositivo, str(hilos[3])))
            valor = str("N:" + str(total_input_traffic) + ':' + str(
                total_output_traffic))
            cadena = str(str(hilos[1])+str(dispositivo.id))
            logging.info('Actualizando BD: '+cadena + '\tValor: '+valor)
            cadena1 = str(str(hilos[1])+str(dispositivo.id)+".rrd")
            try:
                rrdtool.update(cadena1, valor)
                rrdtool.dump(str(str(hilos[1])+str(dispositivo.id)+".rrd"),
                             str(str(hilos[1])+str(dispositivo.id)+".xml"))
            except (Exception, ProgrammingError, OperationalError):
                logging.warning(
                    'Error al Actualizando BD: '+cadena + '\tValor: '+valor)
                abortar.set_x(-1)
            if abortar.get_x() == -1:
                break
            time.sleep(1)
        if abortar.get_x() == -1:
            break


def muchasimagenes(listaimagenes):
    while 1:
        for imagenalv in listaimagenes:
            dispositivo = Dispositivo.objects.get(id=imagenalv[0])
            cad = str(imagenalv[1])+str(dispositivo.id)
            fichero = open(str(str(cad)+".xml"), 'r')
            texto = fichero.readlines()
            fichero.close()
            for oracion in texto:
                if '<row>' in oracion:
                    if 'NaN' not in oracion:
                        lista = oracion.split()
                        tiempo = lista[5]
                        break
            try:
                ret = rrdtool.graph(
                    str("media/"+str(cad)+".png"),
                    str("--start"), str(tiempo),
                    str("--vertical-label=Bytes/s"),
                    str("DEF:inoctets="+str(
                        str(cad)+".rrd")+":inoctets:AVERAGE"),
                    str("DEF:outoctets="+str(
                        str(cad)+".rrd")+":outoctets:AVERAGE"),
                    str("AREA:inoctets#00FF00:In "+str(imagenalv[1])),
                    str("LINE1:outoctets#0000FF:Out "+str(imagenalv[1])+"\r"))
                logging.info('Generando imagen : '+cad+str(ret))
            except (Exception, ProgrammingError, OperationalError):
                logging.warning(
                    "Error al generar la imagen : "+cad)
                abortar.set_x(-1)
            if abortar.get_x() == -1:
                break
        if abortar.get_x() == -1:
            break
        else:
            for i in range(30):
                time.sleep(1)
                if abortar.get_x() == -1:
                    break


def sistemaop(lista):
    tiposistema = [[elemento[0], tipo]
                   for elemento in lista for tipo in listadeso
                   if tipo in elemento[1]]
    return tiposistema


def generartabla(listawalk):
    superlista = [[dispositivo[0], [[dispositivo[2][j][i]
                                     for j in range(len(dispositivo[2]))]
                                    for i in range(int(dispositivo[1]))]]
                  for dispositivo in listawalk]
    return superlista


@staff_required(login_url="/")
@login_required(login_url='/')
def VistaDispositivo(request):
    abortar.set_x(-1)
    listahilos = []
    listaimagenes = []
    dias = []
    usuario = Usuario.objects.filter(Usuario_id=request.user.id)
    dispositivo = Dispositivo.objects.filter(
        Usuario_Dispositivo_id=request.user.id)
    respuesta = consultaSNMP(dispositivo, lista_oid)
    for elemento in respuesta:
        if elemento[1][1] == 'error':
            dias.append([elemento[0], 'no se puede calcular'])
        else:
            trans = int(elemento[1][1])
            hor = (int(trans/3600))
            minu = int((trans-(hor*3600))/60)
            seg = trans-((hor*3600)+(minu*60))
            dias.append([elemento[0],
                         (str(hor)+"h "+str(minu)+"m "+str(seg)+"s")])
            for tipomonitoreo in monitoreosSNMP:
                nombrecad = str(str(tipomonitoreo[0])+str(elemento[0])+'.rrd')
                if not os.path.isfile(nombrecad):
                    creardb(nombrecad, elemento)
                listahilos.append([elemento[0],
                                   tipomonitoreo[0],
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
    lista = [[elemento[0], elemento[1][0]] for elemento in respuesta]
    sis = sistemaop(lista)
    listanumerointerfaz = [[elemento[0], elemento[1][5]]
                           for elemento in respuesta
                           if elemento[1][5] != 'error']
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
    abortar.set_x(-1)
    usuario = Usuario.objects.filter(Usuario_id=request.user.id)
    dispositivos = Dispositivo.objects.filter(
        Usuario_Dispositivo_id=request.user.id)
    listahilos = []
    listaimagenes = []
    dias = []
    dispositivo = Dispositivo.objects.get(id=Id)
    respuesta = consultaSNMP([dispositivo], lista_oid)
    lista = [[elemento[0], elemento[1][0]] for elemento in respuesta]
    sis = sistemaop(lista)
    for elemento in respuesta:
        if elemento[1][1] == 'error':
            dias.append([elemento[0], 'no se puede calcular'])
        else:
            trans = int(elemento[1][1])
            hor = (int(trans/3600))
            minu = int((trans-(hor*3600))/60)
            seg = trans-((hor*3600)+(minu*60))
            dias.append([elemento[0],
                         (str(hor)+"h "+str(minu)+"m "+str(seg)+"s")])
            for tipomonitoreo in monitoreosSNMP:
                nombrecad = str(str(tipomonitoreo[0])+str(elemento[0])+'.rrd')
                if not os.path.isfile(nombrecad):
                    creardb(nombrecad, elemento)
                listahilos.append([elemento[0],
                                   tipomonitoreo[0],
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
    cadena = [[elemento[3], str("/media/"+str(elemento[0])+str(Id)+'.png')]
              for elemento in monitoreosSNMP]
    contexto = {'usuarios': usuario,
                'dispositivos': dispositivos,
                'dispositivo': dispositivo,
                'respuesta': respuesta,
                'lista': sis,
                'dias': dias,
                'cadena': cadena}
    return render(request,
                  'Dispositivo/dispositivo_individual.html',
                  contexto)


@staff_required(login_url="/")
@login_required(login_url='/')
def AgregarDispositivo(request):
    usuario = Usuario.objects.filter(Usuario_id=request.user.id)
    dispositivo = Dispositivo.objects.filter(
        Usuario_Dispositivo_id=request.user.id)
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
    usuario = Usuario.objects.filter(Usuario_id=request.user.id)
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
                   'dispositivo': dispositivo,
                   'usuarios': usuario})


@staff_required(login_url="/")
@login_required(login_url='/')
def EliminarDispositivo(request, Id):
    dispositivo = Dispositivo.objects.get(id=Id)
    usuario = Usuario.objects.filter(Usuario_id=request.user.id)
    if request.method == 'POST':
        dispositivo.delete()
        return redirect('Dispositivo:VistaDispositivo')
    return render(request,
                  'Dispositivo/dispositivo_borrar.html',
                  {'dispositivo': dispositivo,
                   'usuario': usuario})
