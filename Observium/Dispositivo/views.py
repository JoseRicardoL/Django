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
import time
import os
import thread
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


def creardb(nombrecad, dispositivo):
        ret = rrdtool.create(
            str(nombrecad), str("--start"),
            str('N'), str("--step"), str('60'),
            str("DS:inoctets:COUNTER:600:U:U"),
            str("DS:outoctets:COUNTER:600:U:U"),
            str("RRA:AVERAGE:0.5:6:700"),
            str("RRA:AVERAGE:0.5:1:600"))
        if ret:
            print rrdtool.error()


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
            print valor
            cadena1 = str(str(hilos[1])+str(dispositivo.id)+".rrd")
            rrdtool.update(cadena1, valor)
            rrdtool.dump(str(str(hilos[1])+str(dispositivo.id)+".rrd"),
                         str(str(hilos[1])+str(dispositivo.id)+".xml"))
            time.sleep(1)


def muchasimagenes(listaimagenes):
    tiempo_actual = int(time.time())
    tiempo = tiempo_actual-300
    while 1:
        for imagenalv in listaimagenes:
            dispositivo = Dispositivo.objects.get(id=imagenalv[0])
            cad = str(imagenalv[1])+str(dispositivo.id)
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
                print '***sigo vivo : '+str(dispositivo.Comunidad)+str(ret)
            except ProgrammingError:
                print "Oops!  That was no valid number.  Try again..."
            except OperationalError:
                print "Oops!  That was no valid number.  Try again..."
            except Exception:
                print "Oops!  That was no valid number.  Try again..."
        time.sleep(30)


def staff_required(login_url=None):
    return user_passes_test(lambda u: u.is_staff, login_url=login_url)


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


@staff_required(login_url="/")
@login_required(login_url='/')
def VistaDispositivo(request):
    listanumerointerfaz = []
    listawalk = []
    listahilos = []
    listaimagenes = []
    lista = []
    dias = []
    usuario = Usuario.objects.filter(Usuario_id=request.user.id)
    dispositivo = Dispositivo.objects.filter(
        Usuario_Dispositivo_id=request.user.id)
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
                if os.path.isfile(nombrecad):
                    print '****** si hay'
                else:
                    creardb(nombrecad, elemento)
                    print '****** no hay'
                nombreimagen = str(
                    "media/"+str(tipomonitoreo[0])+str(elemento[0])+'.png')
                if os.path.isfile(nombreimagen):
                    print ("Ya existe imagen")
                else:
                    listahilos.append([elemento[0],
                                       tipomonitoreo[0],
                                       tipomonitoreo[1], tipomonitoreo[2]])
                    listaimagenes.append([elemento[0], tipomonitoreo[0]])
    thread.start_new_thread(muchosupdatedb, (listahilos,))
    thread.start_new_thread(muchasimagenes, (listaimagenes,))
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
    usuario = Usuario.objects.filter(Usuario_id=request.user.id)
    dispositivos = Dispositivo.objects.filter(
        Usuario_Dispositivo_id=request.user.id)
    lista_dispositivo = []
    listahilos = []
    listaimagenes = []
    lista = []
    dias = []
    cadena = []
    dispositivo = Dispositivo.objects.get(id=Id)
    lista_dispositivo.append(dispositivo)
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
    respuesta = consultaSNMP(lista_dispositivo, lista_oid)
    for elemento in respuesta:
        lista.append([elemento[0], elemento[1][0]])
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
                if os.path.isfile(nombrecad):
                    print '****** si hay'
                else:
                    creardb(nombrecad, elemento)
                    print '****** no hay'
                nombreimagen = str(
                    "media/"+str(tipomonitoreo[0])+str(elemento[0])+'.png')
                if os.path.isfile(nombreimagen):
                    print ("Ya existe imagen")
                else:
                    listahilos.append([elemento[0],
                                       tipomonitoreo[0],
                                       tipomonitoreo[1], tipomonitoreo[2]])
                    listaimagenes.append([elemento[0], tipomonitoreo[0]])
    thread.start_new_thread(muchosupdatedb, (listahilos,))
    thread.start_new_thread(muchasimagenes, (listaimagenes,))
    for elemento in monitoreosSNMP:
        cadena.append([elemento[3], str(
            "/media/"+str(elemento[0])+str(Id)+'.png')])
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
