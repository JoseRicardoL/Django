/* Creamos un servidor http y conectamos las
funciones de socket a este servidor */
var http = require('http').Server();
var io = require('socket.io')(http);
var redis = require('redis');

// Conectamos con el servidor de redis
var redisClient = redis.createClient(6379, 'redis');

/* Esta función recibe cualquier petición de
conexión desde un socket en el navegador (cliente)
e imprime en consola que un nuevo usuario se ha
conectado */
io.on('connection', function (socket) {
  console.log('A user has connected...');

  /* Cuando el socket cliente envíe un mensaje
  llamado 'subscribe', el socket se suscribe al
  canal de redis que tiene por nombre el ID de
  la tarea de Celery */
  socket.on('subscribe', function(celeryTaskId){
    redisClient.subscribe(celeryTaskId);
  })

  /* Cuando redis genere una publicación (message)
  el mesaje de esa publicación se emite al socket
  bajo el nombre de 'result' */
  redisClient.on('message', function(channel, message) {
    socket.emit('result', message);
  });

});

/* Levantamos el servidor http y lo ponemos a
escuchar en el puerto 3000 */
http.listen(3000, function (){
  console.log('Listening on port 3000...');
});
