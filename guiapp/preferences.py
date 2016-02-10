import os, pickle

class Preferences:

    def __init__(self, prefsFilePath):
        #self.appdir = os.path.join(os.path.expanduser('~'), '.local', 'share', appname)
        self.prefsFilePath = prefsFilePath
        self.set_defaults()
        self.read_prefs()
    
    # FIXME: Move defaults out to application code
    def set_defaults(self):
        self.defaults = {}
        self.defaults['path-history'] = []
        self.defaults['search-history'] = []
        self.defaults['last-opened-folder'] = '~'
        self.defaults['window-size'] = (800,600)
        self.defaults['exclude-dirs'] = ['.git', '.svn']
        self.defaults['exclude-files'] = ['*~']
        self.defaults['show-line-numbers'] = True
        self.defaults['editor'] = 'gedit $1 +$n'
        self.defaults['match-limit'] = 200
        self.defaults['case-sensitive'] = True

        
    def read_prefs(self):
        self.pdict = {}
        if not os.path.exists(self.prefsFilePath):
            return

        try:
            f = open(self.prefsFilePath, "rb")
            self.pdict = pickle.load(f)
            f.close()
        except Exception as e:
            raise e

    def write_prefs(self):
        try:
            f = open(self.prefsFilePath, "wb")
            pickle.dump(self.pdict, f)
            f.close()
        except Exception as e:
            raise e

    def get(self, prefname):
        if prefname in self.pdict:
            return self.pdict[prefname]
        elif prefname in self.defaults:
            return self.defaults[prefname]
        else:
            return None

    def set(self, prefname, value):
        self.pdict[prefname] = value
        
    def reset_to_default(self, prefname):
        self.set(prefname, self.defaults[prefname])
        
    def list_add(self, prefname, item):
        self.pdict[prefname] = self.get(prefname)
        self.pdict[prefname].append(item)
    
    def list_remove(self, prefname, item):
        self.pdict[prefname] = self.get(prefname)
        self.pdict[prefname].remove(item)
    
    def list_sort(self, prefname):
        self.pdict[prefname] = self.get(prefname)
        self.pdict[prefname].sort()
            

