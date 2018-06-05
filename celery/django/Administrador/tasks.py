from __future__ import absolute_import, unicode_literals
from Agente.models import Agente, convertSelializerAgenteToAgente
from Agente.serializers import AgenteSerializer
from Observium.functions import get_SNMP_task, walk_SNMP_task
from .constants import monitoreosSNMP, rendimientoSNMP, serviciosSNMP
from celery.decorators import task
from .aberraciones import main
from .crearRRD import crear
import rrdtool
import redis
import time
import os

'''
    ======= contribución ========
    author : Oscar Huitzilin Chavez Barrera
    github : Huitzoo
'''

redis_client = redis.StrictRedis(host='redis', port=6379, db=0)
path = os.getcwd()
request = ""


@task(name="crearBDRRD")
def crearBDRRD(agentes):
    agente = convertSelializerAgenteToAgente(agentes)
    rrd = '{}/static/files/{}/{}/{}/rrd/'.format(
        path, agente.Comunidad, agente.Ip.replace(".", ""), agente.NombreHost)
    if not os.path.exists(rrd):
        os.makedirs(rrd)
    os.chdir(rrd)
    for lista in (monitoreosSNMP, rendimientoSNMP, serviciosSNMP):
        for elemento in lista:
            nombre = elemento[0]+".rrd"
            tipo = 1
            if elemento in serviciosSNMP:
                tipo = 1
            elif elemento in monitoreosSNMP:
                tipo = 2
            else:
                tipo = 3
            error = crear(nombre, tipo)
            if error != "cool":
                print("Hubo un error: ", error)
                break
    walk = walk_SNMP_task(agente, '1.3.6.1.4.1.2021.9.1.2')
    for elemento in walk:
        nombre = elemento.value.replace("/", "_")+".rrd"
        nombre = "Disk"+nombre
        error = crear(nombre, 3)
        if error != "cool":
            print("Hubo un error: ", error)
            break


@task(name="actualizarBDRRD")
def actualizarBDRRD():
    agentes = Agente.objects.all()
    for agente in agentes:
        serializer = AgenteSerializer(agente)
        servicio.delay(serializer.data)
        discos.delay(serializer.data)


@task(name="servicio")
def servicio(agenteSerializer):
    enddate = int(time.mktime(time.localtime()))
    begdate = enddate - (86400)
    direcciones = {}
    agente = convertSelializerAgenteToAgente(agenteSerializer)
    rrd = '{}/static/files/{}/{}/{}/'.format(
        path, agente.Comunidad, agente.Ip.replace(".", ""), agente.NombreHost)
    os.chdir(rrd+"rrd/")
    for lista in (serviciosSNMP, rendimientoSNMP, monitoreosSNMP):
        for elemento in lista:
            nombre = elemento[0]+".rrd"
            direcciones.update({rrd+"rrd/"+elemento[0]: 0})
            total_input, total_output = get_SNMP_task(
                agente, elemento[1], elemento[2])
            if total_input is not "error" and total_output is not "error":
                valor = str(rrdtool.last(nombre)+300)+":"+str(
                    total_input)+':'+str(total_output)
                ret = rrdtool.update(nombre, valor)
                if not ret:
                    rrdtool.dump(nombre, elemento[0]+'.xml')
                else:
                    print(rrdtool.error())
    main(rrd, begdate, enddate, direcciones)


@task(name="discos")
def discos(agenteSerializer):
    agente = convertSelializerAgenteToAgente(agenteSerializer)
    rrd = '{}/static/files/{}/{}/{}/'.format(
        path, agente.Comunidad, agente.Ip.replace(".", ""), agente.NombreHost)
    os.chdir(rrd+"rrd/")
    walk = walk_SNMP_task(agente, '1.3.6.1.4.1.2021.9.1.2')
    if walk is not 'error':
        for elemento in walk:
            oid = elemento.oid.split(".")
            oid_1 = '1.3.6.1.4.1.2021.9.1.6.'+oid[-1]
            oid_2 = '1.3.6.1.4.1.2021.9.1.7.'+oid[-1]
            nombre = elemento.value.replace("/", "_")+".rrd"
            nombre = "Disk"+nombre
            total_input, total_output = get_SNMP_task(
                agente, oid_1, oid_2)
            if total_input is not "error" and total_output is not "error":
                valor = str(rrdtool.last(nombre)+300)+":"+str(
                    total_input)+':'+str(total_output)
                ret = rrdtool.update(nombre, valor)
                if not ret:
                    rrdtool.dump(nombre, nombre+'.xml')
                else:
                    print(rrdtool.error())
