function handleEvent(event){
  dir("event", event.data);
}

function log(msg) {
  debug.log("[SHELL] - 00:00:00.000 - [D]: [shell] " + msg)
}

function dcFlush(){
  zfwk.Service.DataCollector.flush(true);
}

function restart(){
  TVLib.Event.sendControllerRestart({})
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
  xmlhttp.open("POST", 'http://localhost:8877/answer_zfwk', true);
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
  callAjax('http://localhost:8877/shell_zfwk?rand=' + Math.random(), function (data) {
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

log("Injected ZFWK shell is ready.");
sendAnswer("Hi from ZFWK!")
waitCmd();