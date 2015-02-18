#!/usr/bin/python
# -*- coding: utf8 -*-

import sys
import time
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from rtn import *
import subprocess
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from SocketServer import ThreadingMixIn
import urlparse
import json

CWD = os.getcwd()

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""

color_correct = {
    ("blue", "bold"): '#8888ff',
    ("green", ''): '#A6E22E'
}

def colored(msg, color, attrs=[]):
    if (color, attrs[0] if attrs else '') in color_correct:
        color = color_correct[(color, attrs[0] if attrs else '')]
    return '<span style="color: %s; font-weight: %s">%s</span>' % (
        color, 
        "bold" if "bold" in attrs else "normal", 
        msg
    )

app = QApplication(sys.argv)

class WorkThread(QThread):
    def __init__(self):
        QThread.__init__(self)
 
    def run(self):
        startGalio(self.handler)
        return

    def handler(self, *args):
        self.emit(SIGNAL("update(QString)"), QString(args[1]))

class LogThread(QThread):
    def __init__(self):
        QThread.__init__(self)

    def run(self):
        fn = os.path.join(CWD, 'rtn_log.log')
        p = subprocess.Popen(["tail", "-f", fn], stdout=subprocess.PIPE)
        while 1:
            line = p.stdout.readline()
            self.emit(SIGNAL("update(QString)"), QString(line))
            if not line:
                break

class ConsoleThread(QThread):
    def __init__(self, q, q_zfwk):
        QThread.__init__(self)
        self.q = q
        self.q_zfwk = q_zfwk
        self.consoleHandler = handleRequestsUsing(self)
        self.consoleServer = None
        ws = ' connecting...'
        while self.consoleServer is None:
            try:
                self.consoleServer = ThreadedHTTPServer(('localhost', 8877), self.consoleHandler)
            except Exception as e:
                sys.stdout.write('    ' + spinner.next().encode("utf8") + ws)
                sys.stdout.flush()
                time.sleep(0.3)
                sys.stdout.write('\b' * (len(ws) + 5))

    def run(self):
        self.consoleServer.serve_forever()

def handleRequestsUsing(parent):
    return lambda *args: Handler(parent, *args)

class Handler(BaseHTTPRequestHandler):
    def __init__(self, parent, *args):
        self.parent = parent
        BaseHTTPRequestHandler.__init__(self, *args)

    def msg(self, message, fix):
        self.parent.emit(SIGNAL("update(QString, QString)"), QString(message), QString(fix))

    def send(self, msg, code=200):
        self.send_response(code)
        self.end_headers()
        self.wfile.write(msg)
        self.wfile.write('\n')

    def inject(self, fix=''):
        self.send(file(os.path.join(CWD, "js/rtn_inject%s.js" % fix), 'r').read())
        self.msg("Shell injected", fix)

    def do_GET(self):
        if self.path.startswith('/SSEEvents'):
            return self.send('')
        if self.path.startswith("/inject_zfwk"):
            return self.inject('_zfwk')
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

        if self.path.startswith('/applicationID'):
            self.send('Galio')

        length = int(self.headers['Content-Length'])
        answer = urlparse.parse_qs(self.rfile.read(length).decode('utf-8'))
        if self.path == '/answer':
            answer = answer['answer'][0]
            self.msg(">> %s" % answer, '')
        if self.path == '/answer_zfwk':
            answer = answer['answer'][0]
            self.msg(">> %s" % answer, '_zfwk')
        
        self.send('thx')
        

    def log_message(self, format, *args):
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
        self.connect( self.workThread, SIGNAL("update(QString)"), self.logHandler )
        self.logThread = LogThread()
        self.connect( self.logThread, SIGNAL("update(QString)"), self.fullogHandler )
        self.logThread.start()

        self.history = json.load(file(os.path.join(CWD, 'history.txt'), 'r'))
        self.logView = QTextBrowser()
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
        self.connect( self.consoleThread, SIGNAL("update(QString, QString)"), self.consoleIOHandler )
        self.consoleThread.start()

        self.notes_widget = QTextEdit()
        self.notes_widget.setText(file(os.path.join(CWD, "notes.txt"), 'r').read())
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

        tabs = QTabWidget()
        tabs.addTab(self.logView, 'Log')
        tabs.addTab(self.fullogView, 'Full log')
        # tabs.addTab(console_widget, 'JS Console')

        start_button = QPushButton('Start')
        start_button.clicked.connect(self.workThread.start)
        restart_button = QPushButton('Restart')
        restart_button.clicked.connect(self.restartGalio)
        stop_button = QPushButton('Stop')
        stop_button.clicked.connect(stopGalio)
        widget.setLayout(QHBoxLayout())
        bpanel.setLayout(QVBoxLayout())
        widget.layout().addWidget(tabs)
        widget.layout().addWidget(bpanel)

        rules_button = QPushButton('Edit log rules')
        rules_button.clicked.connect(self.editRules)
        restartapp_button = QPushButton('Restart app')
        restartapp_button.clicked.connect(self.restartApp)

        clear_button = QPushButton('Clear logs')
        clear_button.clicked.connect(self.clearLogs)
        remove_button = QPushButton('Remove log')
        remove_button.clicked.connect(self.removeLog)
        openlog_button = QPushButton('Open log')
        openlog_button.clicked.connect(self.openLog)
        openinject_button = QPushButton('Edit injects')
        openinject_button.clicked.connect(self.openInject)

        bpanel.layout().addWidget(QLabel("Galio controls"))
        bpanel.layout().addWidget(start_button)
        bpanel.layout().addWidget(restart_button)
        bpanel.layout().addWidget(stop_button)
        bpanel.layout().addWidget(QLabel("Other utils"))
        bpanel.layout().addWidget(rules_button)
        # bpanel.layout().addWidget(restartapp_button)
        bpanel.layout().addWidget(clear_button)
        bpanel.layout().addWidget(remove_button)
        bpanel.layout().addWidget(openlog_button)
        bpanel.layout().addWidget(openinject_button)
        bpanel.layout().addSpacerItem(QSpacerItem(20,40,QSizePolicy.Minimum,QSizePolicy.Expanding))
        # self.workThread.start()

        QShortcut(QKeySequence("Ctrl+R"), self, self.restartGalio)
        QShortcut(QKeySequence("Ctrl+X"), self, self.clearLogs)

        completer = QCompleter(self.history)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        # completer.setFilterMode(Qt.MatchContains)
        self.consoleInput.setCompleter(completer)
        self.consoleInput2.setCompleter(completer)

    def saveNotes(self):
        t = self.notes_widget.toPlainText()
        file(os.path.join(CWD, "notes.txt"), 'w').write(t)

    def clearLogs(self):
        self.logView.clear()
        # self.fullogView.clear()

    def restartApp(self):
        stopGalio()
        python = sys.executable
        os.execl(python, python, * sys.argv)

    def editRules(self):
        subprocess.Popen(['subl', os.path.join(CWD, 'rtn_rules.py')])

    def removeLog(self):
        subprocess.Popen(['rm', os.path.join(CWD, 'rtn_log.log')])

    def openLog(self):
        subprocess.Popen(['subl', os.path.join(CWD, 'rtn_log.log')])

    def openInject(self):
        subprocess.Popen(['subl', os.path.join(CWD, 'js/rtn_inject.js'), os.path.join(CWD, 'js/rtn_inject_zfwk.js')])

    def consoleInputHandler(self):
        cmd = self.consoleInput.text()
        if self.cc.checkState() != Qt.Checked:
            self.consoleInput.clear()
        self.consoleView.append("> %s" % cmd)
        if cmd == 'clear':
            self.consoleView.clear()
        else:
            self.history.append(cmd)
            self.q.append(cmd)
            completer = QCompleter(self.history)
            completer.setCaseSensitivity(Qt.CaseInsensitive)
            self.consoleInput.setCompleter(completer)

    def consoleInputHandler2(self):
        cmd = self.consoleInput2.text()
        if self.cc2.checkState() != Qt.Checked:
            self.consoleInput2.clear()
        self.consoleView2.append("> %s" % cmd)
        if cmd == 'clear':
            self.consoleView2.clear()
        else:
            self.history.append(cmd)
            self.q_zfwk.append(cmd)
            completer = QCompleter(self.history)
            completer.setCaseSensitivity(Qt.CaseInsensitive)
            self.consoleInput2.setCompleter(completer)

    def message(self, msg):
        self.logView.append(msg)
        self.logView.verticalScrollBar().setValue(self.logView.verticalScrollBar().maximum())

    def fullogHandler(self, msg):
        msg = str(msg).strip()
        self.fullogView.append(msg)
        self.fullogView.verticalScrollBar().setValue(self.fullogView.verticalScrollBar().maximum())

    def consoleIOHandler(self, msg, fix):
        msg = str(msg).strip()
        if not fix:
            self.consoleView.append(msg)
            self.consoleView.verticalScrollBar().setValue(self.consoleView.verticalScrollBar().maximum())
        else:
            self.consoleView2.append(msg)
            self.consoleView2.verticalScrollBar().setValue(self.consoleView2.verticalScrollBar().maximum())

    def restartGalio(self):
        self.consoleView2.clear()
        self.consoleView.clear()
        stopGalio()
        time.sleep(2)
        self.workThread.start()

    def logHandler(self, message):
        message = str(message)
        msg = json.loads(message)
        if isinstance(msg['data'], dict):
            return
        log = msg['data'].strip()

        try:
            msg = getColored(log, colored)
            if msg is not None:
                self.message(msg)
        except:
            pass

        if isEmulatorLoaded(log):
            self.message(colored("Emulator loaded", 'yellow', attrs=["bold"]))
            activateEmulator()
        logging.info(log)


stopGalio()    
widget = RTN()
widget.show()

if __name__ == "__main__":
    app.exec_()
    stopGalio()
    time.sleep(2)
    widget.workThread.wait()
    json.dump(map(str, widget.history), file(os.path.join(CWD, 'history.txt'), 'w'))
    sys.exit()