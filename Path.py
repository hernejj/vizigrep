import os

class Path:

    def __init__(self, path):
        self.fullpath = self.__fullpath(path)
    
    # FIXME: This does not handle ~userfoo
    def __fullpath(self, path):
        # Handle ~
        if (path.startswith('~')):
            path = path.replace('~', os.path.expanduser('~'))
        
        # Handle relative path
        if (not path.startswith('/')):
            path = os.path.join(os.getcwd(), path)
        return path
    
    def pretty(self):
        return self.trunc_path(self.fullpath)
    
    def trunc_path(self, fn):
        path = self.fullpath.rstrip('/')
        
        if (fn.startswith(os.path.expanduser('~'))):
            fn = fn.replace(os.path.expanduser('~'), '~')
        
        if fn.startswith(path + '/'):
            fn = fn.replace(path + '/', '')
        
        return fn
