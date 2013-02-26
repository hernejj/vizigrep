import subprocess, os

class NoResultsException(Exception):
    pass

class BadPathException(Exception):
    pass

class GrepEngine:
    def __init__(self):
        self.exclude_dirs = []
        self.exclude_files = []
	
    def grep(self, string, path):
        try:
            args = '-Irn %s %s' % (self.arg_exclude_dirs(), self.arg_exclude_files())
            cmd = 'grep %s "%s" %s' % (args, string, path)
            print cmd
            o = subprocess.check_output(cmd, shell=True)
            
            results = GrepResults()
            for line in o.splitlines():
                (filename, sep, rest) = line.partition(':')
                (linenum, sep, text) = rest.partition(':')
                
                if (not filename) or (not text) or (not linenum):
                    continue
                results.append(GrepResult(self.trunc_path(filename),text, linenum))
            return results
            
        except subprocess.CalledProcessError as e:
            if (e.returncode == 2):
                raise BadPathException()
            elif (e.returncode == 1):
                raise NoResultsException()
            else:
                raise e
                
    def arg_exclude_dirs(self):
        arg = ''
        if len(self.exclude_dirs) > 0:
            for d in self.exclude_dirs:
                arg += ' --exclude-dir="%s"' % d
        return arg
        
    def arg_exclude_files(self):
        arg = ''
        if len(self.exclude_files) > 0:
            for d in self.exclude_files:
                arg += ' --exclude="%s"' % d
        return arg

    def trunc_path(self, path):
        if (path.startswith(os.path.expanduser('~'))):
            path = path.replace(os.path.expanduser('~'), '~')
        return path


class GrepResult():
    def __init__(self, filename, result_string, linenum=None):
        self.fn = filename
        self.str = result_string
        self.linenum = linenum
        
    def rel_fn(self, base_path):
        abs_base_path = os.path.expanduser(search_dir) + '/'
        
        if self.fm.startswith(abs_base_path):
            return filename.replace(abs_base_path, '')
        else:
            return self.fn
            
class GrepResults(list):
    def max_fnlen(self):
        maxlen = 0
        for result in self:
            if len(result.fn) > maxlen:
                maxlen = len(result.fn)
        return maxlen
    
    def max_lnlen(self):
        maxlen = 0
        for result in self:
            if len(result.linenum) > maxlen:
                maxlen = len(result.linenum)
        return maxlen
        
