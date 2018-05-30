from __future__ import absolute_import, unicode_literals
from Agente.serializers import AgenteSerializer
from .constants import monitoreosSNMP
from celery.decorators import task
from Agente.models import Agente
from easysnmp import snmp_get
from .crearRRD import crear
import rrdtool
import redis
import os

redis_client = redis.StrictRedis(host='redis', port=6379, db=0)
path = os.getcwd()
request = ""


@task(name="crearBDRRD")
def crearBDRRD(agentes):
    nombreHost = agentes['NombreHost']
    comunidad = agentes['Comunidad']
    ip = agentes['Ip']
    ip = ip.replace(".", "")
    rrd = path+"/static/files/"+comunidad+"/"+ip+"/"+nombreHost+"/rrd/"
    if not os.path.exists(rrd):
        os.makedirs(rrd)
    os.chdir(rrd)
    for elemento in monitoreosSNMP:
        nombre = elemento[0]+".rrd"
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
def subActualizar(agente):
    enddate = int(time.mktime(time.localtime()))
    begdate = enddate - (86400)
    nombreHost = agente['NombreHost']
    comunidad = agente['Comunidad']
    protocolo = agente['Protocolo']
    ip = agente['Ip']
    direcciones = []
    ip = ip.replace(".", "")
    rrd = path+"/static/files/"+comunidad+"/"+ip+"/"+nombreHost+"/"
    os.chdir(rrd+"rrd/")
    for elemento in monitoreosSNMP:
        direcciones.append(rrd+"rrd/"+elemento[0]+".rrd")
        nombre = elemento[0]+".rrd"
        total_input_traffic = int((snmp_get(
            elemento[1], hostname=ip, community=comunidad,
            version=protocolo)).value)
        total_output_traffic = int((snmp_get(
            elemento[1], hostname=ip, community=comunidad,
            version=protocolo)).value)
        valor = str(rrdtool.last(nombre)+300)+":"+str(total_input_traffic)+':'
        +str(total_output_traffic)
        ret = rrdtool.update(nombre, valor)
        if not ret:
            rrdtool.dump(nombre, elemento[0]+'.xml')
            print("actualizado: ", elemento[0])
        else:
            print(rrdtool.error())
