#!/usr/bin/python
# -*- coding: utf8 -*-

import sys
import time
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebKitWidgets import QWebView
from rtn import *
import subprocess
try:
    from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
except:
    from http.server import BaseHTTPRequestHandler, HTTPServer
try:
    from SocketServer import ThreadingMixIn
except:
    from socketserver import ThreadingMixIn
try:
    import urlparse
except:
    import urllib.parse as urlparse
    unicode = str
import json
import random
import binascii
import socket
from de7bit import Decoder, encodeInt
import base64

CWD = os.path.split(sys.argv[0])[0]
CWD = os.getcwd()


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""

color_correct = {
    ("blue", "bold"): '#8888ff',
    ("green", ''): '#A6E22E',
    ("green", 'bold'): '#A6D22E',
}


def colored(msg, color, attrs=[], emblem=None):
    if (color, attrs[0] if attrs else '') in color_correct:
        color = color_correct[(color, attrs[0] if attrs else '')]
    msg = '<span style="color: %s; font-weight: %s">%s</span>' % (
        color,
        "bold" if "bold" in attrs else "normal",
        msg
    )
    # if emblem is not None:
    # msg = ('<img src="emblems/%s.png">' % emblem) + msg
    return msg

app = QApplication(sys.argv)


class WorkThread(QThread):
    update = pyqtSignal(unicode)

    def __init__(self):
        QThread.__init__(self)

    def run(self):
        self.work = True
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        startGalio()
        connected = False
        ws = ' connecting...'
        while not connected:
            try:
                sock.connect(("localhost", 54321))
                connected = True
            except:
                sys.stdout.write('    ' + spinner.next().encode("utf8") + ws)
                sys.stdout.flush()
                time.sleep(0.3)
                sys.stdout.write('\b' * (len(ws) + 5))
        print('')
        print('Connected!')

        sock.send('hi')
        msg = ''
        sep = '\n'
        while self.work:
            msg += sock.recv(1024)
            while sep in msg:
                line = msg.split(sep)[0]
                msg = msg[len(line):].strip()
                if line:
                    self.handler(line)
        return

    def handler(self, line):
        self.update.emit(line)


class BfsThread(QThread):
    update = pyqtSignal(unicode)

    def __init__(self):
        QThread.__init__(self)

    def run(self):
        cmd = [
            "inotifywait",
            "-m",
            "-r",
            BFS_PATH,
            "--timefmt",
            "%d-%m-%Y",
            "--format",
            "'%T -- %w -- %f -- %e'"]
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        while 1:
            line = p.stdout.readline()
            self.update.emit(line)
            if not line:
                break


class LogThread(QThread):
    update = pyqtSignal(unicode)

    def __init__(self):
        QThread.__init__(self)

    def run(self):
        fn = os.path.join(CWD, 'rtn_log.log')
        p = subprocess.Popen(["tail", "-f", fn], stdout=subprocess.PIPE)
        while 1:
            line = p.stdout.readline()
            self.update.emit(line)
            if not line:
                break


class ConsoleThread(QThread):
    update = pyqtSignal(unicode, unicode)
    payload = pyqtSignal(unicode)

    def __init__(self, q, q_zfwk):
        QThread.__init__(self)
        self.q = q
        self.q_zfwk = q_zfwk
        self.consoleHandler = handleRequestsUsing(self)
        self.consoleServer = None
        ws = ' connecting...'
        while self.consoleServer is None:
            try:
                self.consoleServer = ThreadedHTTPServer(
                    ('localhost', 8088), self.consoleHandler)
            except Exception as e:
                sys.stdout.write('    ' + spinner.next().encode("utf8") + ws)
                sys.stdout.flush()
                time.sleep(0.3)
                sys.stdout.write('\b' * (len(ws) + 5))
        print('')
        print('Connected!')

    def run(self):
        self.consoleServer.serve_forever()


def handleRequestsUsing(parent):
    return lambda *args: Handler(parent, *args)


SSE_APPS = []
SSE_APPS_inited = []
class Handler(BaseHTTPRequestHandler):
    def __init__(self, parent, *args):
        self.parent = parent
        BaseHTTPRequestHandler.__init__(self, *args)

    def msg(self, message, fix):
        self.parent.update.emit(message, fix)

    def send(self, msg, code=200):
        self.send_response(code)
        self.end_headers()
        self.wfile.write(msg)
        self.wfile.write('\n')

    def inject(self, fix=''):
        self.send(
            open(os.path.join(CWD, "js/rtn_inject%s.js" % fix), 'r').read())
        self.msg("Shell injected", fix)

    def injectFB(self):
        self.send(open(os.path.join(CWD, "js/firebug-lite.js"), 'r').read())

    def createEvent(self, event_type, headers, msg=''):
        event = "id: %s\n" % random.randint(0, 9999)
        event += "event:%s\n" % event_type
        for key, value in headers:
            event += "data:%s=%s\n" % (key, value)
        if msg:
            data = msg
            data = base64.b64encode(data) + '\n'
            event += "data: %s" % data
        return event

    def fakeSSEEvents(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.end_headers()
        o = urlparse.urlparse(self.path)
        args = urlparse.parse_qs(o.query)
        app_name = args['application'][0]
        headers = [('service', 'GSLEmulator')]
        if app_name not in SSE_APPS:
            event_type = "service-online"
            msg = ''
        else:
            if app_name not in SSE_APPS_inited:
                event_type = "client-connect"
                headers.append(('connection', random.randint(0, 999)))
                headers.append(('ip', '127.0.0.1'))
                headers.append(('port', '7890'))
                msg = ''
                SSE_APPS_inited.append(app_name)
            else:
                event_type = "remoteServiceEvent"
                headers.append(('ip', '127.0.0.1'))
                headers.append(('port', '7890'))
                msg = "Event data from gsl emulator"
        event = self.createEvent(event_type, headers, msg)
        if config.getboolean('logging', 'LOG_SSE'):
            print(event)
        self.wfile.write(event)

    def do_GET(self):
        if self.path.startswith('/initProxyClient') or \
            self.path.startswith('/remoteServiceEvent') or \
            self.path.startswith('/initTCPServer') or \
                self.path.startswith('/initUDPService'):
            self.send_response(200)
            self.end_headers()
            self.wfile.write('GSLEmulator')
            return

        if self.path.startswith('/SSEEvents'):
            return self.fakeSSEEvents()
        if self.path.startswith("/inject_zfwk"):
            return self.inject('_zfwk')
        if self.path.startswith("/firebug-lite.js"):
            return self.injectFB()
        if self.path.startswith("/inject"):
            return self.inject()
        if self.path.startswith("/shell_zfwk"):
            if self.parent.q_zfwk:
                return self.send(self.parent.q_zfwk.pop())
        if self.path.startswith("/shell"):
            if self.parent.q:
                return self.send(self.parent.q.pop())
        if not self.path.startswith("/shell"):
            print(self.path)
        self.send('oops', code=404)
        return

    def do_POST(self):
        length = int(self.headers['Content-Length'])
        answer = urlparse.parse_qs(self.rfile.read(length).decode('utf-8'))
        if self.path.startswith('/initProxyClient') or \
            self.path.startswith('/initTCPServer') or \
                self.path.startswith('/initUDPService'):
            print(answer)
            self.send_response(200)
            self.end_headers()
            self.wfile.write('GSLEmulator')
            return
        if self.path.startswith('/remoteServiceEventCancel') or self.path.startswith('/finalize'):
            app_name = answer['application'][0]
            if app_name in SSE_APPS:
                SSE_APPS.remove(app_name)
            if app_name in SSE_APPS_inited:
                SSE_APPS_inited.remove(app_name)
            print(SSE_APPS, SSE_APPS_inited)
            self.send_response(200)
            self.end_headers()
        if self.path.startswith('/remoteServiceEvent'):
            app_name = answer['application'][0]
            if app not in SSE_APPS:
                SSE_APPS.append(app_name)
            self.send_response(200)
            self.end_headers()
            return
        if self.path.startswith('/applicationID'):
            print(answer)
            try:
                self.send_response(200)
                self.end_headers()
                self.wfile.write(answer['name'][0])
            except Exception as e:
                print(e)
                self.send_response(200)
                self.end_headers()
                self.wfile.write('Galio')
            return
        try:
            if self.path == '/answer':
                answer = answer['answer'][0]
                self.msg(">> %s" % answer, '')
                return
            if self.path == '/answer_zfwk':
                answer = answer['answer'][0]
                self.msg(">> %s" % answer, '_zfwk')
                return
        except Exception as e:
            print(e.message)
            print(self.path, answer)

        if self.path == '/sendRequest' or self.path == '/sendUDP':
            print(answer['payload'])
            pl = answer['payload'][0][16:].strip()
            if len(pl) % 4 != 0:  # check if multiple of 4
                while len(pl) % 4 != 0:
                    pl = pl + "="
            pl = binascii.a2b_base64(pl)
            print('Payload:')
            print(pl)
            pl = "".join("{:02x}".format(ord(c)) for c in pl)
            self.parent.payload.emit(pl)
            self.send('thx')

    def log_message(self, format, *args):
        if config.getboolean('logging', 'LOG_HTTP'):
            BaseHTTPRequestHandler.log_message(self, format, *args)
        return


class RTN(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.resize(800, 600)
        self.setWindowTitle('RTN toolbox')
        self.setWindowIcon(QIcon(os.path.join(CWD, "icon.png")))
        widget = QWidget()
        bpanel = QWidget()
        self.setCentralWidget(widget)

        self.workThread = WorkThread()
        self.workThread.update.connect(self.logHandler)

        self.BfsThread = BfsThread()
        self.BfsThread.update.connect(self.bfsHandler)
        self.BfsThread.start()

        self.history = json.load(open(os.path.join(CWD, 'history.txt'), 'r'))
        self.logView = QTextBrowser()
        for emblem in os.listdir(os.path.join(CWD, 'emblems')):
            self.logView.document().addResource(2, QUrl("emblems/%s" % emblem),
                                                QImage("emblems/%s" % emblem))
        self.fullogView = QTextBrowser()
        self.consoleView = QTextBrowser()
        self.consoleView.append(colored('Galio javascript console', '#666'))
        self.consoleInput = QLineEdit()
        self.consoleInput.returnPressed.connect(self.consoleInputHandler)

        self.consoleView2 = QTextBrowser()
        self.consoleView2.append(colored('ZFWK javascript console', '#666'))
        self.consoleInput2 = QLineEdit()
        self.consoleInput2.returnPressed.connect(self.consoleInputHandler2)

        self.q = []
        self.q_zfwk = []
        self.consoleThread = ConsoleThread(self.q, self.q_zfwk)
        self.consoleThread.update.connect(self.consoleIOHandler)
        self.consoleThread.payload.connect(self.gslPayload)
        self.consoleThread.start()

        self.notes_widget = QTextEdit()
        self.notes_widget.setText(
            open(os.path.join(CWD, "notes.txt"), 'r').read().decode("utf8"))
        self.notes_widget.textChanged.connect(self.saveNotes)

        console_widget = QWidget()
        console_widget.setLayout(QVBoxLayout())
        console_widget.layout().addWidget(self.consoleView)
        iw = QWidget()
        iw.setLayout(QHBoxLayout())
        iw.layout().addWidget(self.consoleInput)
        self.cc = QCheckBox()
        iw.layout().addWidget(self.cc)
        console_widget.layout().addWidget(iw)
        console_widget2 = QWidget()
        console_widget2.setLayout(QVBoxLayout())
        console_widget2.layout().addWidget(self.consoleView2)
        iw2 = QWidget()
        iw2.setLayout(QHBoxLayout())
        iw2.layout().addWidget(self.consoleInput2)
        self.cc2 = QCheckBox()
        iw2.layout().addWidget(self.cc2)
        console_widget2.layout().addWidget(iw2)
        console_tabs = QTabWidget()
        console_tabs.addTab(console_widget2, 'ZFWK')
        console_tabs.addTab(console_widget, 'Galio')
        console_tabs.addTab(self.notes_widget, 'Notes')
        dock = QDockWidget()
        dock.setWidget(console_tabs)
        self.addDockWidget(Qt.BottomDockWidgetArea, dock)

        self.parserView = QWebView()
        self.parserView.setUrl(
            QUrl(os.path.join(CWD, 'dc_parser/DCParser.html')))

        self.parserViewNG = QWidget()
        self.parserViewNG.setLayout(QVBoxLayout())
        self.dcMessageInput = QTextEdit()
        self.dcMessageOutput = QTextBrowser()
        self.parserViewNG.layout().addWidget(self.dcMessageInput)
        self.parserViewNG.layout().addWidget(self.dcMessageOutput)
        self.dcMessageInput.textChanged.connect(self.decodeDC)

        tabs = QTabWidget()
        tabs.addTab(self.logView, 'Log')
        shortcutT1 = QShortcut(QKeySequence("Alt+1"), self)
        shortcutT1.activated.connect(lambda: tabs.setCurrentIndex(0))
        # tabs.addTab(self.fullogView, 'Full log')
        # tabs.addTab(self.parserView, 'DC Parser')
        tabs.addTab(self.parserViewNG, 'DC Parser NG')
        shortcutT2 = QShortcut(QKeySequence("Alt+2"), self)
        shortcutT2.activated.connect(lambda: tabs.setCurrentIndex(1))
        # tabs.addTab(console_widget, 'JS Console')

        start_button = QPushButton('Start')
        start_button.clicked.connect(self.startWork)
        restart_button = QPushButton('Restart')
        restart_button.clicked.connect(self.restartGalio)
        crestart_button = QPushButton('Clear && Restart')
        crestart_button.clicked.connect(self.clear_restart)

        shortcut = QShortcut(QKeySequence("Ctrl+S"), self)
        shortcut.activated.connect(self.clear_restart)

        stop_button = QPushButton('Stop')
        stop_button.clicked.connect(self.stopGalio)
        widget.setLayout(QHBoxLayout())
        bpanel.setLayout(QVBoxLayout())
        widget.layout().addWidget(tabs)
        widget.layout().addWidget(bpanel)

        rules_button = QPushButton('Edit log rules')
        rules_button.clicked.connect(self.editRules)
        rrules_button = QPushButton('Reload rules')
        rrules_button.clicked.connect(self.reloadRules)

        clear_button = QPushButton('Clear logs')
        clear_button.clicked.connect(self.clearLogs)
        remove_button = QPushButton('Remove log')
        remove_button.clicked.connect(self.removeLog)
        openlog_button = QPushButton('Open log')
        openlog_button.clicked.connect(self.openLog)
        shortcut3 = QShortcut(QKeySequence("Ctrl+l"), self)
        shortcut3.activated.connect(self.openLog)

        openinject_button = QPushButton('Edit injects')
        openinject_button.clicked.connect(self.openInject)

        ruler_button = QPushButton('Run ruler')
        ruler_button.clicked.connect(self.runRuler)

        flush_button = QPushButton('DC Flush')
        flush_button.clicked.connect(self.dcFlush)

        shortcut2 = QShortcut(QKeySequence("Ctrl+F"), self)
        shortcut2.activated.connect(self.dcFlush)

        bpanel.layout().addWidget(QLabel("Galio controls"))
        bpanel.layout().addWidget(start_button)
        bpanel.layout().addWidget(restart_button)
        bpanel.layout().addWidget(crestart_button)
        bpanel.layout().addWidget(stop_button)
        bpanel.layout().addWidget(QLabel("Other utils"))
        bpanel.layout().addWidget(rules_button)
        bpanel.layout().addWidget(rrules_button)
        bpanel.layout().addWidget(clear_button)
        bpanel.layout().addWidget(remove_button)
        bpanel.layout().addWidget(openlog_button)
        bpanel.layout().addWidget(openinject_button)
        bpanel.layout().addWidget(ruler_button)
        bpanel.layout().addWidget(flush_button)

        bpanel.layout().addWidget(QLabel("Log details"))
        self.bfs_check = QCheckBox('Show BFS')
        bpanel.layout().addWidget(self.bfs_check)

        self.rtnui_check = QCheckBox('Show RTNUI')
        self.rtnui_check.stateChanged.connect(self.rtn_toggle)
        bpanel.layout().addWidget(self.rtnui_check)

        self.zfwk_check = QCheckBox('Show ZFWK')
        self.zfwk_check.stateChanged.connect(self.zfwk_toggle)
        bpanel.layout().addWidget(self.zfwk_check)

        self.errors_check = QCheckBox('Show Errors')
        self.errors_check.stateChanged.connect(self.errors_toggle)
        bpanel.layout().addWidget(self.errors_check)

        bpanel.layout().addSpacerItem(
            QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        # self.workThread.start()

        QShortcut(QKeySequence("Ctrl+R"), self, self.restartGalio)
        QShortcut(QKeySequence("Ctrl+X"), self, self.clearLogs)

        self.completer = QCompleter(self.history)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        # completer.setFilterMode(Qt.MatchContains)
        self.consoleInput.setCompleter(self.completer)
        self.consoleInput2.setCompleter(self.completer)

    def decodeDC(self, *args):
        message = str(self.dcMessageInput.toPlainText())
        d = Decoder(message)
        self.dcMessageOutput.clear()
        # if True:
        try:
            d.decode()
            # print(d.json())
            d.display(show=self.displayDC)
        except Exception as e:
            self.dcMessageOutput.append("Decode error: %s" % e.message)
            # print(e)

    def displayDC(self, msg):
        self.dcMessageOutput.append(msg)

    def gslPayload(self, msg):
        msg = str(msg)
        self.message(colored("Fake GSL recieved:", 'orange', attrs=[""]))
        self.message(colored(msg, 'orange', attrs=["bold"]))
        self.dcMessageInput.setText(msg)
        self.decodeDC()

    def dcFlush(self):
        self.q_zfwk.append('dcFlush()')

    def stopGalio(self):
        self.workThread.work = False
        stopGalio()
        self.workThread.wait()
        self.message(colored(
            " === Emulator stopped === ", 'red', attrs=["bold"], emblem='red'))

    def rtn_toggle(self):
        if self.rtnui_check.checkState() == Qt.Checked:
            rtn_rules.active_rules.append('rtnui')
        elif 'rtnui' in rtn_rules.active_rules:
            rtn_rules.active_rules.remove('rtnui')

    def zfwk_toggle(self):
        if self.zfwk_check.checkState() == Qt.Checked:
            rtn_rules.active_rules.append('zfwk')
        elif 'zfwk' in rtn_rules.active_rules:
            rtn_rules.active_rules.remove('zfwk')

    def errors_toggle(self):
        if self.errors_check.checkState() == Qt.Checked:
            rtn_rules.active_rules.append('errors')
        elif 'errors' in rtn_rules.active_rules:
            rtn_rules.active_rules.remove('errors')

    def saveNotes(self):
        t = self.notes_widget.toPlainText().toUtf8()
        open(os.path.join(CWD, "notes.txt"), 'w').write(t)

    def clearLogs(self):
        self.logView.clear()

    def restartApp(self):
        stopGalio()
        python = sys.executable
        os.execl(python, python, * sys.argv)

    def editRules(self):
        subprocess.Popen(['atom', os.path.join(CWD, 'rtn_rules.py')])

    def reloadRules(self):
        reload(rtn_rules)
        self.rtn_toggle()
        self.zfwk_toggle()
        self.errors_toggle()

    def removeLog(self):
        open(os.path.join(CWD, 'rtn_log.log'), 'w').write("")

    def openLog(self):
        subprocess.Popen(['glogg', os.path.join(CWD, 'rtn_log.log')])

    def openInject(self):
        subprocess.Popen([
            'atom',
            os.path.join(CWD, 'js/rtn_inject.js'),
            os.path.join(CWD, 'js/rtn_inject_zfwk.js')]
        )

    def runRuler(self):
        subprocess.Popen([
            'kruler',
        ])

    def consoleInputHandler(self):
        cmd = self.consoleInput.text()
        if self.cc.checkState() != Qt.Checked:
            self.consoleInput.clear()
        self.consoleView.append("> %s" % cmd)
        if cmd == 'clear':
            self.consoleView.clear()
        else:
            if cmd not in self.history:
                self.history.append(cmd)
                self.completer.setModel(QStringListModel(self.history))
            self.q.append(cmd)

    def consoleInputHandler2(self):
        cmd = self.consoleInput2.text()
        if self.cc2.checkState() != Qt.Checked:
            self.consoleInput2.clear()
        self.consoleView2.append("> %s" % cmd)
        if cmd == 'clear':
            self.consoleView2.clear()
        else:
            if cmd not in self.history:
                self.history.append(cmd)
                self.completer.setModel(QStringListModel(self.history))
            self.q_zfwk.append(cmd)

    def bfsHandler(self, msg):
        msg = str(msg).strip()
        try:
            ts, folder, filename, event = msg.replace("'", '').split(' -- ')
            if 'ISDIR' in event or 'CLOSE' in event:
                return
            path = os.path.join(folder, filename)[len(BFS_PATH):]
            if self.bfs_check.checkState() == Qt.Checked:
                self.message(colored("BFS: %s -- %s" % (event, path), "pink"))
        except:
            print(msg)

    def message(self, msg):
        if len(msg) > 500:
            msg = msg[:500] + '...'
        self.logView.append(msg)
        self.logView.verticalScrollBar().setValue(
            self.logView.verticalScrollBar().maximum())

    def fullogHandler(self, msg):
        msg = str(msg).strip()
        print(msg)
        self.fullogView.append(msg)
        self.fullogView.verticalScrollBar().setValue(
            self.fullogView.verticalScrollBar().maximum())

    def consoleIOHandler(self, msg, fix):
        msg = str(msg).strip()
        if not fix:
            self.consoleView.append(msg)
            self.consoleView.verticalScrollBar().setValue(
                self.consoleView.verticalScrollBar().maximum())
        else:
            self.consoleView2.append(msg)
            self.consoleView2.verticalScrollBar().setValue(
                self.consoleView2.verticalScrollBar().maximum())

    def clear_restart(self):
        self.clearLogs()
        self.removeLog()
        self.logThread = LogThread()
        self.logThread.update.connect(self.logHandler)
        self.logThread.start()
        self.restartGalio()

    def restartGalio(self):
        self.consoleView2.clear()
        self.consoleView.clear()
        stopGalio()
        time.sleep(2)
        self.workThread.work = False
        self.startWork()
        self.BfsThread.start()

    def startWork(self):
        self.message(colored(
            " === Start emulator === ", 'yellow',
            attrs=["bold"], emblem='yellow'))
        self.workThread = WorkThread()
        self.workThread.update.connect(self.logHandler)
        self.workThread.start()
        self.BfsThread.start()

    def logHandler(self, message):
        try:
            log = str(message).strip()
        except:
            self.workThread.work = False
            self.workThread = None
            return
        try:
            msg = getColored(log, colored)
            if msg is not None:
                self.message(msg)
        except Exception as e:
            print(e)
            return

        if isEmulatorLoaded(log):
            self.message(colored(
                " === Emulator loaded === ", 'green',
                attrs=["bold"], emblem='green'))
            activateEmulator()
        logging.info(log)


stopGalio()
widget = RTN()
widget.show()

if __name__ == "__main__":
    app.exec_()
    stopGalio()
    time.sleep(2)
    if widget.workThread is not None:
        widget.workThread.work = False
        widget.workThread.wait()
    json.dump(
        map(str, widget.history), open(os.path.join(CWD, 'history.txt'), 'w'))
    sys.exit()
