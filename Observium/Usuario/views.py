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
from rrdtool import ProgrammingError, OperationalError
import rrdtool
import random
import pygeoip
import thread
import time
import os
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


def imagen(dispositivoid, nombregraf):
    dispositivo = Dispositivo.objects.get(id=dispositivoid)
    tiempo_actual = int(time.time())
    tiempo = tiempo_actual-300
    cad = str(nombregraf)+str(dispositivo.id)
    while 1:
        try:
            ret = rrdtool.graph(
                str("media/"+str(cad)+".png"),
                str("--start"), str(tiempo),
                str("--vertical-label=Bytes/s"),
                str("DEF:inoctets="+str(str(cad)+".rrd")+":inoctets:AVERAGE"),
                str("DEF:outoctets="+str(
                    str(cad)+".rrd")+":outoctets:AVERAGE"),
                str("AREA:inoctets#00FF00:In "+str(nombregraf)),
                str("LINE1:outoctets#0000FF:Out "+str(nombregraf)+"\r"))
            time.sleep(30+int(random.randrange(10)))
            print '***sigo vivo : '+str(dispositivo.Comunidad)+str(ret)
        except ProgrammingError:
            print "Oops!  That was no valid number.  Try again..."
        except OperationalError:
            print "Oops!  That was no valid number.  Try again..."
        except Exception:
            print "Oops!  That was no valid number.  Try again..."


@staff_required(login_url="/")
@login_required(login_url='/')
def VistaUsuario(request):
    puertos = [0, 0, 0, 0]
    mostrar = [0, 0]
    listanumerointerfaz = []
    listahilos = []
    listaimagenes = []
    listawalk = []
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
                 '1.3.6.1.2.1.2.1.0']
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
