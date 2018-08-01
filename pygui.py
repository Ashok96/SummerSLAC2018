#!/usr/bin/python3

from PyQt5 import QtCore, QtGui, uic,QtWidgets
import moxacode
import backup
from PyQt5.QtCore import Qt, pyqtSignal
import sys
import time
from subprocess import call

form_class, base_class = uic.loadUiType('MoxaGui.ui')
moxa = moxacode.TelnetHelper()

class MoxaSetupThread(QtCore.QThread):
    
    sig2 = pyqtSignal('PyQt_PyObject')
    sig3 = pyqtSignal('PyQt_PyObject')
    sig4 = pyqtSignal('PyQt_PyObject')
    sig5 = pyqtSignal('PyQt_PyObject')
    

    
    """MoxaSetup Thread"""
    def __init__(self, lock, parent = None):
        super(MoxaSetupThread, self).__init__(parent)
        self.lock      = lock
        self.mutex     = QtCore.QMutex()
        self.stopped   = False
        self.completed = False
        self.assign = False
        

        
        

    def initialize(self, current_action):
        self.current_action = current_action
        self.stopped        = False
        self.completed      = False
        return True

    def run(self):
        
       
        if self.current_action == 'setup':
            self._setup()
        if self.current_action == 'backup':
            self._backup()
        if self.current_action == 'restore':
            self._restore()
        if self.current_action == 'exit':
            self._shutdown()
        
    def _setup(self):
        """ - Setup MOXA with DHCP and users priviledges"""
        print('From Thread: Calling Setup method')
        
        moxa.connect()
        moxa.set_console()
        moxa.login()
        moxa.set_change_pw()
        moxa.network()
        moxa.basic()
        moxa.dhcp_setup()
        moxa.ip_source_verify()
        moxa.add_users()
        moxa.save_users()
        moxa.restart()
        moxa.close_connection()
        self.sig2.emit(True)
        
        

    def _backup(self):
        """TBD - Backup current configuraton to file"""
        print('From Thread: Backup configuration...')
        backup.backup_moxa('192.168.127.254', moxapass='moxa')
        self.sig3.emit(True)
       

    def _restore(self):
        """TBD - Restore configuration from file"""
        print('From Thread: Restore configuration...')
        self.sig4.emit(True)

    def _shutdown(self):
    	print('From Thread: Shutting down the system...')
    	call("sudo shutdown -h now", shell=True)
    	self.sig5.emit(True)

    def stop(self):
        try:
            self.mutex.lock()
            self.stopped = True
        finally:
            self.mutex.unlock()

    def isStopped(self):
        try:
            self.mutex.lock()
            return self.stopped
        finally:
            self.mutex.unlock()

#    def outprint(self, msg):
#        self.emit(QtCore.SIGNAL("pmsg(QString)"), msg)

#    def outdialog(self, mode, inp1, inp2, inp3):
#        sig3 = QtCore.SIGNAL("dialog(QString, QString, QString, QString)")
#        self.emit(sig3 , mode, inp1, inp2, inp3)

class MoxaSetupForm(QtWidgets.QWidget, form_class):

    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        super(MoxaSetupForm, self).__init__(parent)
       
       # titleBarHeight = self.style().pixelMetric(QtWidgets.QStyle.PM_TitleBarHeight, QtWidgets.QStyleOptionTitleBar(), self)

        self.setupUi(self)
        #self.showMaximized()
        self.setWindowState(QtCore.Qt.WindowMaximized)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.lock = QtCore.QReadWriteLock()
        self.MoxaSetupThread = MoxaSetupThread(self.lock, self)
        
        #geometry = app.desktop().screenGeometry()
        #geometry.setHeight(geometry.height()- titleBarHeight )
        #self.setGeometry(geometry)
        self._initActions()           # setup button actions

    def _initActions(self):
        
        self.pB_SETUP.clicked.connect(self._setup)
        self.MoxaSetupThread.sig2.connect(self._pBsetup)
        
        self.pB_BACKUP.clicked.connect(self._backup)
        self.MoxaSetupThread.sig3.connect(self._pBbackup)
        
        self.pB_EXIT.clicked.connect(self._exit)
        self.MoxaSetupThread.sig5.connect(self._pBexit)
        
        self.pB_RESTORE.clicked.connect(self._restore)
        self.MoxaSetupThread.sig4.connect(self._pBrestore)
        
        
    def _setup(self): 
        '''  Sets MOXA to DHCP and setup all user and permission levels'''
        '''      Starts the thread MoxaSetupThread process                 '''
        #moxa.connect()
        # Check for thread instance:
        if self.MoxaSetupThread.isRunning():
            self.MoxaSetupThread.terminate()
            self.MoxaSetupThread.wait()
            self.MoxaSetupThread.stop()
            return False

        # Call Moxa Setup Thread:
        self.MoxaSetupThread.wait()

        # HERE THE LIST OF PARAMETERS NEEDED BY THE THREAD
        self.MoxaSetupThread.initialize('setup')

        # Disable setup button:
        self.pB_SETUP.setDisabled(True)
        self._startThread()
        return True

    def _pBsetup(self, action):
        if action == True:
            self.pB_SETUP.setDisabled(False)
        elif action == False:
            self.pB_SETUP.setDisabled(True)

    def _exit(self):
        ''' Shutdown the system'''
        self.MoxaSetupThread.initialize('exit')
        self._startThread()

    def _pBexit(self, action):
        if action == True:
            self.pB_EXIT.setDisabled(False)
        elif action == False:
            self.pB_EXIT.setDisabled(True)

    def _backup(self):
        '''TBD - Saves the current configuration'''
        self.MoxaSetupThread.initialize('backup')
        
        
        self._startThread()
   
    def _pBbackup(self, action):
        if action == True:
            self.pB_BACKUP.setDisabled(False)
        elif action == False:
            self.pB_BACKUP.setDisabled(True)

    def _restore(self):
        
        '''TBD -
        Loads the saved configuration
        '''
        self.MoxaSetupThread.initialize('restore')
        self._startThread()

    def _pBrestore(self, action):
        if action == True:
            self.pB_RESTORE.setDisabled(False)
        elif action == False:
            self.pB_RESTORE.setDisabled(True)

    def _startThread(self):
        self.MoxaSetupThread.start()
    



if __name__ == "__main__":
    # ---------------------------------------------------------------------------
    style = {'CL' : 'Cleanlooks', 'XP': 'WindowsXP', 'PL' : 'Plastique'}
    app   = QtWidgets.QApplication(sys.argv)
    app.setStyle(style['PL'])
    app.setPalette(app.style().standardPalette())
    # ---------------------------------------------------------------------------

    try:
        MoxaSetup = MoxaSetupForm()
        if MoxaSetup:
            MoxaSetup.show()

        sys.exit(app.exec_())
    except (KeyboardInterrupt, SystemExit):
        pass

