import os, pickle

class Preferences:

    def __init__(self, appname):
        self.appname = appname
        self.appdir = os.path.join(os.path.expanduser('~'), '.local', 'share', appname)
        self.ppath = os.path.join(self.appdir, appname + '.data')
        self.set_defaults()
        self.ensure_appdir_exists()
        self.read_prefs()
        
    def set_defaults(self):
        self.defaults = {}
        self.defaults['path-history'] = []
        self.defaults['search-history'] = []
        self.defaults['window-size'] = (800,600)
        self.defaults['exclude-dirs'] = ['.git', '.svn']
        self.defaults['exclude-files'] = ['*~']
        self.defaults['show-line-numbers'] = True
        self.defaults['editor'] = 'gedit $1'
        
    def ensure_appdir_exists(self):
        if not os.path.exists(self.appdir):
            os.makedirs(self.appdir)

    def read_prefs(self):
        self.pdict = {}
        if not os.path.exists(self.ppath):
            return

        try:
            f = open(self.ppath, "rb")
            self.pdict = pickle.load(f)
            f.close()
        except Exception as e:
            raise e

    def write_prefs(self):
        try:
            f = open(self.ppath, "wb")
            pickle.dump(self.pdict, f)
            f.close()
        except Exception as e:
            raise e

    def get(self, prefname):
        if prefname in self.pdict:
            return self.pdict[prefname]
        else:
            return self.defaults[prefname]

    def set(self, prefname, value):
        self.pdict[prefname] = value
        
    def reset_to_default(self, prefname):
        self.set(prefname, self.defaults[prefname])
        
    def list_add(self, prefname, item):
        self.pdict[prefname].append(item)
    
    def list_remove(self, prefname, item):
        self.pdict[prefname].remove(item)
    
    def list_sort(self, prefname):
        self.pdict[prefname].sort()

