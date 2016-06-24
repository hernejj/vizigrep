#!/usr/bin/python
import unittest, sys, os, getpass

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir, 'vizigrep')))
from GrepEngine import GrepEngine, NoResultsException

class testCases(unittest.TestCase):

    def setUp(self):
        self.ge = GrepEngine()
        user = getpass.getuser()
        host = "127.0.0.1"
        fullpath = os.path.abspath('./test-data')
        self.path = '%s@%s:%s' % (user, host, fullpath)
        
    def tearDown(self):
        pass

    ### Basic Functionality ###
    
    def testFindSimple(self):
        results = self.ge.grep('foo', self.path)
        self.assertTrue(len(results) == 1)
        self.checkResult(results[0], "File1", "linefoo", "2")

    def testNoMatches(self):
        with self.assertRaises(NoResultsException):
            self.ge.grep('idonotexistidonotexistidonotexist', self.path)

    def testIgnoreDirSimple(self):
        self.ge.exclude_dirs.append('FolderA')
        results = self.ge.grep('file', self.path)
        self.ge.exclude_dirs = []
        self.assertTrue(len(results) == 2)
        self.checkResult(results[0], "File1", "This is a test file", "1")
        self.checkResult(results[1], "File2", "Another file!", "1")
    
    #def testIgnoreDirWithSpaceInPath(self):
    #    self.ge.exclude_dirs.append('Space A')
    #    with self.assertRaises(NoResultsException):
    #        results = self.ge.grep('space_marker', self.path)
    #    self.ge.exclude_dirs = []
        
    #def testGrepGivesErrorMessage(self):
    #    with self.assertRaises(GrepException):
    #        results = self.ge.grep('a[]b', self.path)
    
    ### Search path ###
    
    #def testPathWithSpaces(self):
    #    path = 'test-data/Space A'
    #    results = self.ge.grep('space_marker', path)
    #    self.assertTrue(len(results) == 1)
    #    self.checkResult(results[0], 'Space File', 'space_marker', '1')
        
    
    ### Broken Regex ###
    
    #def testStartsWithStar(self):
    #    with self.assertRaises(BadRegexException):
    #        results = self.ge.grep('*foo', self.path)

    #def testDoubleStar(self):
    #    with self.assertRaises(BadRegexException):
    #        results = self.ge.grep('foo**', self.path)
        
    #def testEmptyString(self):
    #    with self.assertRaises(BadRegexException):
    #        results = self.ge.grep('', self.path)
    
    #def testAllDots(self):
    #    with self.assertRaises(BadRegexException):
    #        results = self.ge.grep('...', self.path)
            
    #def testDotStar(self):
    #    with self.assertRaises(BadRegexException):
    #        results = self.ge.grep('.*', self.path)
            
    ### Test Special Chars & Shell Escaping ###
    
    #def testDoubleQuote(self):
    #    results = self.ge.grep('"stdio.h', self.path)
    #    self.assertTrue(len(results) == 1)
    #    self.checkResult(results[0], 'FolderA/File2', '#include "stdio.h"', '1')
    
    #def testDoubleQuotes(self):
    #    results = self.ge.grep('"stdio.h"', self.path)
    #    self.assertTrue(len(results) == 1)
    #    self.checkResult(results[0], 'FolderA/File2', '#include "stdio.h"', '1')
    
    #def testStringStartingWithHash(self):
    #    path = os.path.join(self.path, 'FolderA')
    #    results = self.ge.grep('#include', path)
    #    self.assertTrue(len(results) == 1)
    #    self.checkResult(results[0], 'File2', '#include "stdio.h"', '1')

    #def testAngleBrackets(self):
    #    results = self.ge.grep('<stdio.h>', self.path)
    #    self.assertTrue(len(results) == 1)
    #    self.checkResult(results[0], 'FolderA/File2', '@fnclude <stdio.h>', '2')
    
    #def testBackslash(self):
    #    results = self.ge.grep('fi\\\\le', self.path)
    #    self.assertTrue(len(results) == 1)
    #    self.checkResult(results[0], 'FolderA/File1', 'fi\le', '4')
        
    #def testDash(self):
    #    path = os.path.join(self.path, 'FolderA')
    #    results = self.ge.grep('-d', path)
    #    self.assertTrue(len(results) == 1)
    #    self.checkResult(results[0], 'File3.py', "        self.ge.exclude_dirs = self.prefs.get('exclude-dirs')", '17')
    
    #def testDashDash(self):
    #    path = os.path.join(self.path, 'FolderA')
    #    results = self.ge.grep('--link', path)
    #    self.assertTrue(len(results) == 1)
    #    self.checkResult(results[0], 'File3.py', "        self.lbl_options.connect('activate--link', self.options_clicked)", '32')
    
    #def testCPointerDereference(self):
    #    path = os.path.join(self.path, 'c-source')
    #    results = self.ge.grep('urb->status;', path)
    #    self.assertTrue(len(results) == 2)
    #    self.checkResult(results[0], 'xpad.c', "	status = urb->status;", '637')
    #    self.checkResult(results[1], 'xpad.c', "	status = urb->status;", '706')

    def checkResult(self, result, fn, line, linenum):
        self.assertTrue(result.fn == fn)
        self.assertTrue(result.str == line)
        self.assertTrue(int(result.linenum) == int(linenum))

##########
# Create and return a test suite for this set of tests.
##########
def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(testCases))
    return suite

##########
# MAIN: Execute the tests in this file.
##########
if __name__ == '__main__':
    unittest.main()
