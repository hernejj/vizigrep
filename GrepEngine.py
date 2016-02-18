import subprocess, os, tempfile
import Path

class NoResultsException(Exception):
    pass

class GrepException(Exception):
    pass

class BadRegexException(Exception):
    pass

class GrepEngine:
    def __init__(self):
        self.exclude_dirs = []
        self.exclude_files = []
	
    def grep(self, string, path, max_matches, case_sensitive):
        realPath = Path.full(path)
        string = self.check_regex(string)
        
        try:
            argList = ['grep', '-I', '-r', '-n']
            if not case_sensitive:
                argList.append('-i')
            argList = argList + self.arg_exclude_list()
            argList.append(string)
            argList.append(realPath)
            
            stdErrFile = tempfile.TemporaryFile()
            o = subprocess.check_output(argList, stderr=stdErrFile)
            o = o.decode('utf-8', 'replace')

            results = GrepResults()
            for line in o.splitlines():
                (filename, sep, rest) = line.partition(':')
                (linenum, sep, text) = rest.partition(':')
                
                if (not filename) or (not text) or (not linenum):
                    continue
                if (max_matches > 0) and len(results) == max_matches:
                    break
                results.append(GrepResult(Path.relativeTo(filename, realPath), text, linenum))

            return results
            
        except subprocess.CalledProcessError as e:
            if (e.returncode == 2):
                stdErrFile.seek(0)
                sdterrStr = stdErrFile.read()
                
                print "CMD=", e.cmd
                print "OUTPUT=", e.output
                print "STDERR=", sdterrStr
                
                newE = GrepException()
                newE.output = sdterrStr
                raise newE
            elif (e.returncode == 1):
                raise NoResultsException()
            else:
                raise e
                
    def check_regex(self, regex):
        
        # Escape funky chars
        if '\\' in regex: 
            regex = regex.replace('\\', '\\\\')  # Escape \
        if regex.startswith('--'):
            regex = '\-\-' + regex[2:]  # Escape double dashes
        if regex.startswith('-'):
            regex = '\-' + regex[1:]  # Escape single dash
        if '"' in regex: 
            regex = regex.replace('"', '\\"')  # Escape quotes
        if '#' in regex: 
            regex = regex.replace('#', '\#')  # Escape hash
        
        # Check for invalid regex
        if regex == '':
            raise BadRegexException("Search string is empty")
        if regex.startswith('*'):
            raise BadRegexException("Search string cannot start with *")
        if '**' in regex:
            raise BadRegexException("Search string cannot contain **")
        if regex.strip().replace('.','') == '':
            raise BadRegexException("Search string is way too vague")
        if regex.strip() == '.*':
            raise BadRegexException("Search string is way too vague")
            
        return regex
    
    def arg_exclude_list(self):
        argList = []
        if len(self.exclude_dirs) > 0:
            for d in self.exclude_dirs:
                argList.append('--exclude-dir=%s' % d)
        
        if len(self.exclude_files) > 0:
            for d in self.exclude_files:
                argList.append('--exclude=%s' % d)
        
        return argList

class GrepResult():
    def __init__(self, filename, result_string, linenum=None):
        self.fn = filename
        self.str = result_string
        self.linenum = linenum
        
    def rel_fn(self, base_path):
        abs_base_path = os.path.expanduser(base_path) + '/'
        
        if self.fm.startswith(abs_base_path):
            return self.fn.replace(abs_base_path, '')
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
    
    def max_txtlen(self):
        maxlen = 0
        for result in self:
            if len(result.str) > maxlen:
                maxlen = len(result.str)
        return maxlen
    
    def unique_fns(self):
        count = 0
        fdict = {}
        for r in self:
            if not r.fn in fdict:
                count += 1
                fdict[r.fn] = True
        return count
        
