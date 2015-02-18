var WebSocketServer = require('ws').Server;
var net = require('net');

var to;
var wsCount = 1;

function webServer() {
    websocket('localhost', 11337, function(ws) {
        to = ws;
        ws.on('close', function() {
            to = null;
        });
    });
}

webServer();

function websocket(host, port, done) {
    var wss = new WebSocketServer({host: host, port: port});
    wss.on('connection', function(ws) {
        var clientId = wsCount++;
        console.log('Client %s', clientId);
//        ws.on('message', function(message) {
//            // change settings
//            //ws.send('DATA: ' + message);
//        });
        ws.on('error', function() {
            console.log('Client %s is closed', clientId);
            ws.close();
        });
        done(ws);
    });
}



function rtnListen() {
    listen('localhost', 54321, function(message) {
        if (to) to.send(JSON.stringify(message));
    }, function() {
        setTimeout(rtnListen, 1000);
    });
}

rtnListen();

function listen(host, port, echo, finish) {
    var client = new net.Socket(),
        connected = false;

    function connect() {
        client.connect(port, host, function() {
            console.log('Connected: %s:%s', host, port);
            echo({type: 'connect', data: {host: host, port: port}});
            client.write('Hello');
            connected = true;
        });
    }

    connect();

    client.on('data', function(data) {
        echo({type: 'message', data: String(data)});
    });

    // Close the client socket completely
    //client.destroy();
    // Add a 'close' event handler for the client socket
    client.on('close', function() {
        if (connected) {
            console.log('Closed: %s:%s', host, port);
            echo({type: 'close', data: {host: host, port: port}});
        }
        client.destroy();
        finish();
    });

    client.on('error', function(e) {
        if (e.code == 'EADDRINUSE') {
            console.log('Address in use, retrying...');
            setTimeout(function () {
                client.close();
            }, 1000);
        }
    });
}

