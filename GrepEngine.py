import subprocess, os, tempfile
import Path

PATTERN_IN_FILE = False

class NoResultsException(Exception):
    pass

class GrepException(Exception):
    def __init__(self, errMsg):
        self.output = errMsg

class BadRegexException(Exception):
    pass

class GrepEngine:
    def __init__(self):
        self.exclude_dirs = []
        self.exclude_files = []
	
    def grep(self, string, path, max_matches, case_sensitive):
        realPath = Path.full(path)
        string = self.check_regex(string)
        
        # Basic Args
        argList = ['grep', '-I', '-r', '-n']
        if not case_sensitive:
            argList.append('-i')
        argList = argList + self.arg_exclude_list()
        
        # Search string
        if PATTERN_IN_FILE:
            (fd, patternFilePath) = tempfile.mkstemp()
            print patternFilePath
            patternFile = open(patternFilePath, 'w')
            patternFile.write(string)
            patternFile.close()
            argList.append('--file=%s' % (patternFilePath,))
        else:
            argList.append(string)
        
        # Path
        argList.append(realPath)
            
        try:
            stdErrFile = tempfile.TemporaryFile()
            o = subprocess.check_output(argList, stderr=stdErrFile)
            o = o.decode('utf-8', 'replace')
            return self.parse_output(o, max_matches, realPath)
            
        except subprocess.CalledProcessError as e:
            if (e.returncode == 1):
                raise NoResultsException()
            elif (e.returncode == 2):
                stdErrFile.seek(0)
                raise GrepException(stdErrFile.read())
            else:
                raise e
                
    def parse_output(self, output, max_matches, searchPath):
        results = GrepResults()
        
        for line in output.splitlines():
            (filename, sep, rest) = line.partition(':')
            (linenum, sep, text) = rest.partition(':')
            
            if (not filename) or (not text) or (not linenum):
                continue
            if (max_matches > 0) and len(results) == max_matches:
                break
            results.append(GrepResult(Path.relativeTo(filename, searchPath), text, linenum))
        return results
    
    def check_regex(self, regex):
        # Escape funky chars
        if regex.startswith('--'):
            regex = '\-\-' + regex[2:]  # Escape double dashes
        if regex.startswith('-'):
            regex = '\-' + regex[1:]  # Escape single dash
        
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
        
