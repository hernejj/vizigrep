import subprocess, os, tempfile, time
import Path

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
        self.cancelled = False
	
    def grep(self, string, searchPath, max_matches, case_sensitive):
        self.cancelled = False
        self.check_regex(string)
        searchPath = Path.full(searchPath)
        argList = self.construct_args_list(string, searchPath, case_sensitive)
        stdErrFile = tempfile.TemporaryFile()
        stdOutFile = tempfile.TemporaryFile()
        
        self.grepProc = subprocess.Popen(argList, stdout=stdOutFile, stderr=stdErrFile)
        self.grepProc.wait()
        
        # Handle case where operation was cancelled
        if self.grepProc.returncode < 0:
            return
        
        # Read data from stdout/stderror
        stdOutFile.seek(0)
        output = stdOutFile.read().decode('utf-8', 'replace')
        stdOutFile.close()
        stdErrFile.seek(0)
        errMsg = stdErrFile.read()
        stdErrFile.close()
        
        if self.grepProc.returncode == 1:
            raise NoResultsException()
        if self.grepProc.returncode == 2:
            raise GrepException(errMsg)

        return self.parse_output(output, max_matches, searchPath, string)
    
    def construct_args_list(self, string, realPath, case_sensitive):
        argList = ['/bin/grep', '-Irn']
        if not case_sensitive:
            argList.append('-i')
        argList = argList + self.arg_exclude_list()

        argList.append('--') # End of - or -- style command options
        argList.append(string)
        argList.append(realPath)
        return argList
    
    def parse_output(self, output, max_matches, searchPath, searchString):
        results = GrepResults()
        results.search_path = searchPath
        results.search_string = searchString
        
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
    
    def cancel(self):
        self.grepProc.terminate()
        self.cancelled = True

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
        
