# Proyectos Django 
Estos son algunos de mis proyectos relizados en python con su framework Django

## Instalacion
Para poder correr cada uno de estos proyectos recomiendo el uso de entornos virtuales e instalar los respectivos paquetes 

## ObserviumProblem 
Es una paguina web con un sistema de monitoreo remoto usando los protocolos tipo SNMP ,en este sistemas podras registrar varios usuarios que tengan multiples dispositivos que se quieran monitorear y para cada uno de ellos se generara una base de datos tipo ROUND ROBIN con rrdtools que registre cada entrada y salida del objeto oid a consultar para posterior mente generar una imagen .png cada cierto tiempo que grafique cada una de las bases de datos que generen cada uno de los dispositivos que tiene el usuario de manera que la base de datos se vaya actualizando cada cierto tiempo

#### NOTA: 
El sistema esta en desarrollo y faltan mejoras en optimilidad y presenta unos problemas de concurrencia

### Entorno virtual:
los paquetes instalados en el entorno virtual fueron:

#### Django==1.11.5
#### geoip2==2.5.0
#### mysqlclient==1.3.12
#### Pillow==3.1.2
#### pysnmp==4.3.9
#### rrdtool==0.1.11
#### sorl-thumbnail==12.3

### Agentes / Dispositivos
Para poder registrar un agente es necesario haber registrado una comunidad SNMP 
He grabado unos videos y subudo a youtube para poder ver como realizar estos registros 

### Para windows: [Registrar agente](https://www.youtube.com/watch?v=Kakd94yA6U0&t=27s)
