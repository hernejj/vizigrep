import subprocess, tempfile, re
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
        self.case_sensitive = True
        self.max_matches = 0
        self.cancelled = False
        self.is_remote = False
	
    def remote_params(self, searchPath):
        m = re.match('(.+)@(.+):(.+)', searchPath)
        if (m):
            return (m.group(1), m.group(2), m.group(3))
        return (None, None, searchPath)
	    
    def grep(self, string, searchPath):
        # Figure out if we're executig a local grep, or remote grep via ssh
        #(user, host, searchPath) = self.remote_params(searchPath)
        #self.is_remote = (user != None) 
        
        self.cancelled = False
        self.check_regex(string)
        searchPath = Path.full(searchPath)
    
        # Construct args for grep command execution
        argList = self.build_grep_args(string, searchPath)
        #if self.is_remote:
        #    argList = self.build_ssh_args(user, host) + argList
        
        # Run command   
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
        if self.grepProc.returncode > 1:
            raise GrepException(errMsg)

        return self.parse_output(output, searchPath, string, self.is_remote)

    def build_grep_args(self, string, realPath):
        argList = ['/bin/grep', '-Irn']
        if not self.case_sensitive:
            argList.append('-i')
        argList = argList + self.arg_exclude_list()

        argList.append('--') # End of - or -- style command options
        argList.append(string)
        argList.append(realPath)
        return argList
    
    def build_ssh_args(self, user, host):
        return ['ssh', '-o', 'PasswordAuthentication=no', '-o', 'PubkeyAuthentication=yes', '-o BatchMode=yes', '%s@%s' % (user, host)]
        
    def parse_output(self, output, searchPath, searchString, is_remote):
        results = GrepResults()
        results.search_path = searchPath
        results.search_string = searchString
        results.is_remote = is_remote
        
        for line in output.splitlines():
            (filename, sep, rest) = line.partition(':')
            (linenum, sep, text) = rest.partition(':')
            
            if (not filename) or (not text) or (not linenum):
                continue
            if (self.max_matches > 0) and len(results) == self.max_matches:
                break
            
            # Ignore case where we have malformed data in output
            try:
                lnstr = int(linenum)
            except Exception as e:
                continue
            
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
        
