import os

import multilogger
import preferences
import mbox

class GuiApp:

    def __init__(self, shortName):
        self.shortName = shortName

        self.appHomeDir = os.path.join(os.path.expanduser('~'), '.config', self.shortName)
        self.__checkHomeDir()

        # Components
        self.log = None
        self.prefs = None
        self.mbox = mbox.mbox()

        # Settings
        self.writePrefsOnClose = True

    def __checkHomeDir(self):
        if not os.path.exists(self.appHomeDir):
            os.mkdir(self.appHomeDir)

    def checkAppHomeDirPermissions(self):
        if not os.access(self.appHomeDir, os.W_OK):
            self.__homeDirError(self.appHomeDir)
            return

        path = os.path.join(self.appHomeDir, self.shortName + '.prefs')
        if not os.access(path, os.W_OK):
            self.__homeDirError(path)
            return

    def __homeDirError(self, path):
        msg = 'Your user does not have write permission for file %s, this means %s will be unable to save preferences and data' % (path, self.shortName)
        if self.mbox:
            self.mbox.error(msg)
        else:
            print(msg)

    def initLogging(self):
        self.logFilePath = os.path.join(self.appHomeDir, self.shortName + '.log')
        self.log = multilogger.MultiLogger()

        if not self.log.open_logfile(self.logFilePath):
            self.log = None

    def initPrefs(self):
        self.prefsFilePath = os.path.join(self.appHomeDir, self.shortName + '.prefs')
        self.prefs = preferences.Preferences(self.prefsFilePath)

    def shutdown(self):
        if self.log:
            self.log.close_logfile()

        if self.prefs and self.writePrefsOnClose:
            self.prefs.write_prefs()
