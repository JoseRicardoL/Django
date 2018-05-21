from celery import task
from .crearRRD import crear
from .constants import monitoreosSNMP
import redis
import os

redis_client = redis.StrictRedis(host='redis', port=6379, db=0)


@task(bind=True)
def crearBDRRD(self, agentes):
    nombreHost = agentes['NombreHost']
    comunidad = agentes['Comunidad']
    ip = agentes['Ip']
    ip = ip.replace(".", "")
    path = os.getcwd()
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
    redis_client.publish(self.request.id, 'crearBDRRD')


@task(bind=True)
def actualizarBDRRD(self, agentes):
    # enddate = int(time.mktime(time.localtime()))
    # begdate = enddate - (86400)
    #
    # total_input_traffic = 0
    # total_output_traffic = 0
    nombreHost = agentes['NombreHost']
    comunidad = agentes['Comunidad']
    ip = agentes['Ip']
    direcciones = []
    ip = ip.replace(".", "")
    path = os.getcwd()
    rrd = path+"/static/files/"+comunidad+"/"+ip+"/"+nombreHost+"/rrd/"

    for elemento in monitoreosSNMP:
        direcciones.append(rrd+elemento[0]+".rrd")
    print(direcciones)
    redis_client.publish(self.request.id, 'actualizarBDRRD')
