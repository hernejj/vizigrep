import os, stat, time, thread, inspect, platform

# Multilogger is a multithread-friendly logging service that logs information
# to a data source (currently a local file is the only supported data source).
# Optionally logged data can also be printed to standard out.
# NOTE: It is safe to use multilogger to log data from multiple threads
# in the same prorgam. It is NOT SAFE to create two separate multilogger instances
# that both log data to the same file (either in the same or different programs)!
class MultiLogger:

    # Log file
    logfile         = None
    logfile_path    = None

    # Lock protecting logfile.
    logfile_lock    = thread.allocate_lock()

    # Options affecting behavior of this multilogger.
    stdout          = False         # Print logged data to stdout.

    max_size        = 0             # Upon opening the log file, its size in
                                    # bytes is compared with this value. If it
                                    # is larger, the log file will be reduced
                                    # by removing the oldest lines first. A
                                    # value of zero indicates that the log file
                                    # should be allowed to grow without limit.

    reduced_size    = 0             # This is the maximum size of the reduced
                                    # log file. The oldest line is removed
                                    # until its size in bytes is less than or
                                    # equal to this value. (must be <= max_size
                                    # when max_size > 0)

    def __init__(self, stdout=False, max_size=100000, reduced_size=50000):
        
        if ( max_size < 0) or (reduced_size < 0):
            raise Exception("max_size must be greater than 0")
        
        self.stdout = stdout
        self.max_size = max_size
        self.reduced_size = reduced_size
        self.logDebug = False
    
    def log_debug(self, isDebugOn):
        self.logDebug = isDebugOn
    
    # Open the log file that this multilogger instance should use to log data. If the
    # given file exists data will be appended to it. If the given file does not exist
    # it will be created. If the parent directory of the log file does not exist then
    # an error is returned.
    #
    # Before the log file is opened, it is checked to see if it has grown past
    # its maximum byte size. If this is the case, the oldest lines in the file
    # are removed until it is less than or equal to the maximum reduced size
    # (see the max_size & reduced_size attributes).
    def open_logfile(self, logfile_path):

        if ( not self.__validateLogfilePath__(logfile_path) ):
            return False
        
        # Open the log file and reduce it if necessary.
        try:
            self.reduce_logfile(logfile_path)
            self.logfile = open(logfile_path, 'a')
        except Exception as e:
            print e
            return False

        # Remember path to log file.        
        self.logfile_path = logfile_path
        
        return True

    def __validateLogfilePath__(self, logfile_path):
        
        if ( self.__parentDirectoryExists__(logfile_path) ):
            return False

        if ( self.__isSpecialFile__(logfile_path) ):
            return False
            
        return True

    def __parentDirectoryExists__(self, file_path):
        
        parent_dir = os.path.dirname(file_path)
        if (not os.path.exists(parent_dir)):
            return False

    def __isSpecialFile__(self, file_path):
        
        if ( os.path.exists(file_path) ):
            mode = os.stat(file_path)[stat.ST_MODE]
            if (not stat.S_ISREG(mode)):
                return True
        return False
    
    # Reduce the size of the given log file if it has grown past its maximum
    # size. The file is reduced by removing as many lines (starting from the
    # beginning) as it takes for the byte size of the file to be less than or
    # equal to its maximum reduced size. When the log file does not exist, this
    # method does nothing.
    #
    # In the event that any problems are encountered while reading or writing
    # the log file, an IOError will be raised.
    def reduce_logfile(self, path):

        # Check if the file exists and has grown past its limit.
        if (self.max_size > 0    and
            os.path.isfile(path) and
            os.path.getsize(path) > self.max_size):

            # Read in the greatest number of lines from the end of the file
            # that do not put us past the maximum reduced size.
            with open(path, "rb") as f:

                # We only want to read in complete lines, so we're going to
                # start one byte before the first character we want to save.
                # This allows us to preserve the entire first line if possible
                # since the previous line will be discarded later.
                offset = self.reduced_size + 1
                f.seek(-offset, os.SEEK_END)

                f.readline()        # Discard the first line
                content = f.read()  # Read in the remaining data

            # Save the reduced log file.
            with open(path, "wb") as f:
                f.write(content)

    #
    # Closes the log file. Call this when all threads are done writting to it.
    #
    def close_logfile(self):

        self.logfile_lock.acquire()
        self.logfile.close()
        self.logfile = None
        self.logfile_lock.release()

    # Writes a given piece of data (meant to be a single line of text) to the log file. 
    # The data will be prepended with date/time information and a component identifier.
    def write(self, data, level='Info', component=None):

        # Get component (if it exists) ==> caller's class
        if component == None:
            try:
                component = str(inspect.stack()[1][0].f_locals['self'].__module__)
            except KeyError:
                component = ''
            component = component.replace(' ', '') # Remove spaces
        
        # If the log file is not open, just bail.
        if (not self.logfile): return

        # Get the date/time this data is being logged.
        time_str = time.asctime()        

        # Concatenate time, componenet and data
        log_line = '{0} [{1:8.8}] - {2:18.18} : {3}'.format(time_str, level, component, data)

        # Get lock
        self.logfile_lock.acquire()
        
        # Write the line to the log
        self.logfile.write(log_line + '\n')
        self.logfile.flush()

        # Write to stdout - Not on Windows, causes "Bad File Descriptor" messages
        if (self.stdout and (not platform.system() == "Windows") ): print log_line

        # Release lock
        self.logfile_lock.release()
    
    def debug(self, data):
        if not self.logDebug: return
        try:
            component = str(inspect.stack()[1][0].f_locals['self'].__module__)
        except KeyError:
            component = ''
        component = component.replace(' ', '') # Remove spaces
        component = component.ljust(18)[0:18] # Ensure string is exactly 18 characters
    
        self.write(data, level='Debug', component=component)
    
    def error(self, data):
        if not self.logDebug: return
        try:
            component = str(inspect.stack()[1][0].f_locals['self'].__module__)
        except KeyError:
            component = ''
        component = component.replace(' ', '') # Remove spaces
        component = component.ljust(18)[0:18] # Ensure string is exactly 18 characters
    
        self.write(data.replace('\n',' \\n '), level='Error', component=component)
