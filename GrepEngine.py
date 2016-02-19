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
	
    def grep(self, string, searchPath, max_matches, case_sensitive):
        self.check_regex(string)
        searchPath = Path.full(searchPath)
        argList = self.construct_args_list(string, searchPath, case_sensitive)
        stdErrFile = tempfile.TemporaryFile()
        
        try:
            o = subprocess.check_output(argList, stderr=stdErrFile)
            o = o.decode('utf-8', 'replace')
            stdErrFile.close()
            return self.parse_output(o, max_matches, searchPath)
            
        except subprocess.CalledProcessError as e:
            if (e.returncode == 1):
                stdErrFile.close()
                raise NoResultsException()
            elif (e.returncode == 2):
                stdErrFile.seek(0)
                errMsg = stdErrFile.read()
                stdErrFile.close()
                raise GrepException(errMsg)
            else:
                stdErrFile.close()
                raise e
    
    def construct_args_list(self, string, realPath, case_sensitive):
        argList = ['grep', '-Irn']
        if not case_sensitive:
            argList.append('-i')
        argList = argList + self.arg_exclude_list()
        
        # Search string
        if PATTERN_IN_FILE:
            (fd, patternFilePath) = tempfile.mkstemp()
            patternFile = open(patternFilePath, 'w')
            patternFile.write(string)
            patternFile.close()
            argList.append('--file=%s' % (patternFilePath,))
            argList.append('--') # End of - or -- style command options
        else:
            argList.append('--') # End of - or -- style command options
            argList.append(string)
        
        # Path
        argList.append(realPath)
        return argList
    
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
        
