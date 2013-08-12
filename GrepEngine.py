import subprocess, os
import sys
class NoResultsException(Exception):
    pass

class BadPathException(Exception):
    pass

class BadRegexException(Exception):
    pass

class GrepEngine:
    def __init__(self):
        self.exclude_dirs = []
        self.exclude_files = []
	
    def grep(self, string, path, max_matches, case_sensitive):
        try:
            if case_sensitive: case_arg = ''
            else: case_arg = 'i'
            
            args = '-Irn%s %s %s' % (case_arg, self.arg_exclude_dirs(), self.arg_exclude_files())
            cmd = 'grep %s "%s" %s' % (args, string, path)
            
            o = subprocess.check_output(cmd, shell=True)
            o = o.decode('utf-8', 'replace')

            results = GrepResults()
            for line in o.splitlines():
                (filename, sep, rest) = line.partition(':')
                (linenum, sep, text) = rest.partition(':')
                
                if (not filename) or (not text) or (not linenum):
                    continue
                if (max_matches > 0) and len(results) == max_matches:
                    break
                results.append(GrepResult(self.trunc_path(filename, path), text, linenum))

            return results
            
        except subprocess.CalledProcessError as e:
            if (e.returncode == 2):
                raise BadPathException()
            elif (e.returncode == 1):
                raise NoResultsException()
            else:
                raise e
                
    def check_regex(self, regex):
        if '**' in regex:
            regex = regex.replace('**', '*')
        if regex == '':
            raise BadRegexException("Search string is empty")
        if regex.strip()  == '*':
            raise BadRegexException("Search string is way too vague")
        if regex.strip().replace('.','') == '':
            raise BadRegexException("Search string is way too vague")
        if regex.strip() == '.*':
            raise BadRegexException("Search string is way too vague")
            
        return regex
    
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

    def trunc_path(self, fn, path):
        path = path.rstrip('/')
        
        if (fn.startswith(os.path.expanduser('~'))):
            fn = fn.replace(os.path.expanduser('~'), '~')
        
        if fn.startswith(path + '/'):
            fn = fn.replace(path + '/', '')
        
        return fn

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
    
    def unique_fns(self):
        count = 0
        fdict = {}
        for r in self:
            if not r.fn in fdict:
                count += 1
                fdict[r.fn] = True
        return count
        
