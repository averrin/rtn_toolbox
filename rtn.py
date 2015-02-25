# -*- coding: utf8 -*-
import websocket
import thread
import time
import json
from termcolor import colored
# from fabulous import fg256 as colored
import subprocess
import os, sys
import logging
CWD = os.getcwd()
logging.basicConfig(filename=os.path.join(CWD, 'rtn_log.log'), level=logging.DEBUG)
import time
from rtn_rules import *

BFS_PATH = '/home/user/.wine/drive_c/Cisco-SDK/downloads/bfs'

def spinning_cursor():
    while True:
        for cursor in u'▁▃▄▅▆▇█▇▆▅▄▃':
            yield cursor

spinner = spinning_cursor()

def getAttrs(log):
    ls = log.split(" - ")
    if len(ls) == 3:
        prefix, ts, log = ls
        ls = log.split(": ")
        if len(ls) >= 2:
            tag = ls[0]
        return prefix[-6:], tag, ": ".join(ls[1:])
    return None, None, log

def getColored(log, colorfn=colored):
    prefix, tag, log = getAttrs(log)
    msg = None
    for r in color_pref:
        if r['check'](prefix, tag, log):
            msg = colorfn(log, r['color'], attrs=r['attrs'])
    return msg

def activateEmulator():
    time.sleep(1)
    c = "xdotool search 'Cisco Vantage'"                                                                                       
    p = subprocess.Popen(["/bin/bash", "-c", c], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    wid = p.communicate()[0].strip()
    subprocess.call(["xdotool", "windowactivate", wid])
    return wid

def tuneChannel(num, sleep=1):
    for n in str(num):
        subprocess.call(["xdotool", "key", n])
    subprocess.call(["xdotool", "key", "Return"])
    time.sleep(sleep)

def openAppMenu():
    tuneChannel(101)
    subprocess.call(["xdotool", "key", "Right"])

def openZDCT():
    # subprocess.call(["xdotool", "key", "Down"])
    # subprocess.call(["xdotool", "key", "Down"])
    subprocess.call(["xdotool", "key", "Down"])
    subprocess.call(["xdotool", "key", "Return"])

def isEmulatorLoaded(log):
    return "Mosaic has been changed to state [Passive Snooze] from [Passive Waiting]" in log

def on_message(ws, message):
    msg = json.loads(message)
    log = msg['data'].strip()

    try:
        msg = getColored(log)
        if msg is not None:
            print(msg)
    except:
        pass

    if isEmulatorLoaded(log):
        print(colored("Emulator loaded", 'yellow', attrs=["bold"]))
        activateEmulator()
#         openAppMenu()
#         openZDCT()
#         tuneChannel(15, 5)
#         tuneChannel(16, 12)
#         tuneChannel(101)
    logging.info(log)

def on_error(ws, error):
    print(colored(error, "red"))

def on_close(ws):
    print(colored("### closed ###", "white", attrs=["bold"]))

def on_open(ws):
    print(colored("### connected to emulog server ###", "white", attrs=["bold"]))


def startEmulator():
    if not os.path.isfile("run_galio_HD.bat"):
        location = "/home/user/.wine/drive_c/Cisco-SDK/"
        os.chdir(location)
    cmd = ["wine", "cmd", "/c", "run_galio_HD.bat"]
    subprocess.Popen(cmd)

def startEmulogServer():
    if not os.path.isfile("ws-translator.js"):
        os.chdir(os.path.join(CWD, "emulog_server"))
    cmd = ["nodejs", "ws-translator.js"]
    subprocess.Popen(cmd)

def runLogTail(callback):
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp(
        "ws://localhost:11337/",
        on_message = callback,
        on_error = on_error,
        on_close = on_close
    )
    ws.on_open = on_open
    ws.run_forever()

import threading

def startGalio(callback=on_message):
    startEmulator()
    startEmulogServer()

    time.sleep(2)
    runLogTail(callback)

def stopGalio():
    os.system('killall galio.exe')
    os.system('killall tail')
    os.system('killall inotifywait')
    os.system('killall nodejs')

if __name__ == "__main__":
    startGalio()
