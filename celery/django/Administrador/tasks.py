from __future__ import absolute_import, unicode_literals
from Agente.models import Agente, convertSelializerAgenteToAgente
from Agente.serializers import AgenteSerializer
from Observium.functions import get_SNMP_task, walk_SNMP_task
from .constants import monitoreosSNMP
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
    for elemento in monitoreosSNMP:
        nombre = elemento[0]+".rrd"
        error = crear(nombre)
        if error != "cool":
            print("Hubo un error: ", error)
            break
    walk = walk_SNMP_task(agente, '1.3.6.1.4.1.2021.9.1.3')
    for elemento in walk:
        nombre = elemento.value.replace("/", "_")+".rrd"
        nombre = "Disk_"+nombre
        error = crear(nombre)
        if error != "cool":
            print("Hubo un error: ", error)
            break


@task(name="actualizarBDRRD")
def actualizarBDRRD():
    agentes = Agente.objects.all()
    for agente in agentes:
        serializer = AgenteSerializer(agente)
        subActualizar.delay(serializer.data)


@task(name="subActualizar")
def subActualizar(agenteSerializer):
    enddate = int(time.mktime(time.localtime()))
    begdate = enddate - (86400)
    direcciones = {}
    agente = convertSelializerAgenteToAgente(agenteSerializer)
    rrd = '{}/static/files/{}/{}/{}/'.format(
        path, agente.Comunidad, agente.Ip.replace(".", ""), agente.NombreHost)
    os.chdir(rrd+"rrd/")
    for elemento in monitoreosSNMP:
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
