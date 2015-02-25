ownerWafer.addEventListener("ControllerStartApplication", handleEvent, false);
ownerWafer.addEventListener("ControllerHideAll", handleEvent, false);
ownerWafer.addEventListener("ControllerRestart", handleEvent, false);
ownerWafer.addEventListener("ControllerStartApplication", handleEvent, false);
ownerWafer.addEventListener("ControllerStopApplication", handleEvent, false);
ownerWafer.addEventListener("ControllerKillApplication", handleEvent, false);
ownerWafer.addEventListener("ControllerBroadcastMessage", handleEvent, false);
ownerWafer.addEventListener("ControllerSendMessage", handleEvent, false);
ownerWafer.addEventListener("ApplicationShown", handleEvent, false);

hideAll = controllerHideAll

function startApp(app){
  controllerHideAll();
  TVLib.Event.sendControllerStartApplication({name: app});
}

function handleEvent(event){
  dir("event", event);
}

function log(msg) {
  debug.log("[SHELL] - 00:00:00.000 - [D]: [shell] " + msg)
}

function dirarr(name, array) {
  var i = 0,
    l = array.length;

  while (i < l) {
    if (array[i] instanceof Array) {
      dirarr(name + '[' + i + ']', array[i]);
    } else if (array[i] instanceof Object) {
      dir(name + '[' + i + ']', array[i]);
    } else {
      log(name + '[' + i + '] = ' + array[i]);
    }

    i += 1;
  }
};

function dir(name, object) {
  for (var key in object) {
    if (object.hasOwnProperty(key)) {
      if (key instanceof Object) {
        dir(key, object[key]);
      } else if (object[key] instanceof Array) {
        dirarr(name + '[' + key + ']', object[key]);
      }  else {
        log(name + '.' + key + ' = ' + object[key]);
      }
    }
  }
};

function sendAnswer(answ){
  var xmlhttp;
  xmlhttp = new XMLHttpRequest();
  xmlhttp.open("POST", 'http://localhost:8877/answer', true);
  xmlhttp.send('answer=' + answ);
}

function callAjax(url, callback) {
  var xmlhttp;
  xmlhttp = new XMLHttpRequest();
  xmlhttp.onreadystatechange = function () {
    if (xmlhttp.readyState == 4) {
      if (xmlhttp.status == 200) {
        clearTimeout(timeout);
        callback(xmlhttp.responseText);
      } else {
        if (xmlhttp.status != 404) {
          log("Error: " + xmlhttp.statusText);
        }
        return false;
      }
    }
  };
  xmlhttp.open("GET", url, true);
  xmlhttp.send();
  // log("waiting for command...");
  var timeout = setTimeout( function(){ xmlhttp.abort(); waitCmd(); }, 1000);
}
function waitCmd() {
  callAjax('http://localhost:8877/shell?rand=' + Math.random(), function (data) {
    if (data) {
      log("injected: " + data);
      try {
        var answ = eval(data);
        if (answ) {
          log("answer: " + answ);
          sendAnswer(answ)
        }
      } catch (e) {
        log("error: " + e);
      }
    }
    setTimeout(waitCmd, 500);
  });
}

log("Injected shell is ready.");
sendAnswer("Hi from Galio!")
waitCmd();
