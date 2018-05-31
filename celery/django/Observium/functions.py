from easysnmp import snmp_get, Session
from Observium.settings import BASE_DIR
import pygeoip

listaWalk = {'hoja': '1.3.6.1.2.1.2.1.0', 'rama': '1.3.6.1.2.1.2.2.1'}
gloc = pygeoip.GeoIP(BASE_DIR+'/database/GeoLiteCity.dat')
listadeso = ["Linux", "Windows", "error"]


def sistemaop(lista):
    enlinea = 0
    fueralinea = 0
    tiposistema = [[elemento[0], tipo] for elemento in lista
                   for tipo in listadeso if tipo in elemento[1][0]]
    for elemento in tiposistema:
        if elemento[1] != 'error':
            enlinea += 1
        else:
            fueralinea += 1
    return tiposistema, [len(lista), enlinea, fueralinea]


def listar_posiciones(agentes):
    lista_posiciones = []
    for agente in agentes:
        addr_info = gloc.record_by_name(agente.Ip_publica)
        longitude = addr_info['longitude']
        latitude = addr_info['latitude']
        data = "{lat:"+str(latitude)+", lng: "+str(longitude)+"}"
        lista_posiciones.append(data)
    return lista_posiciones


def get_SNMP(agentes, listaGet):
    respuesta = []
    for agente in agentes:
        resultado = []
        for elemento in listaGet:
            try:
                resultado.append((snmp_get(elemento, hostname=agente.Ip,
                                           community=agente.Comunidad,
                                           version=agente.Protocolo)).value)
            except Exception:
                resultado.append('error')
        respuesta.append([agente.id, resultado])
    return respuesta


def get_SNMP_task(agente, oid_1, oid_2):
    r_1 = 0
    r_2 = 0
    try:
        r_1 = (snmp_get(oid_1, hostname=agente.Ip,
                        community=agente.Comunidad,
                        version=agente.Protocolo)).value
        r_2 = (snmp_get(oid_2, hostname=agente.Ip,
                        community=agente.Comunidad,
                        version=agente.Protocolo)).value
    except Exception:
        r_1 = 'error'
        r_2 = 'error'
    return r_1, r_2


def walk_SNMP(agentes, listaOID, tipodewalk):
    superlista = []
    for agente in agentes:
        sublista = []
        lista = []
        try:
            session = Session(hostname=agente.Ip, community=agente.Comunidad,
                              version=agente.Protocolo)
            get_s = session.get(listaOID['hoja']).value
            walk_s = session.walk(listaOID['rama'])
            for hoja in walk_s:
                sublista.append(hoja.value)
                if len(sublista) == int(get_s):
                    lista.append(sublista)
                    sublista = []
            superlista.append([agente.id, get_s, lista])
        except Exception as err:
            print(err)
    return superlista
