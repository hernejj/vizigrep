#!/usr/bin/python
import unittest, sys, os, shutil

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
from GrepEngine import GrepEngine, GrepResult, GrepResults, NoResultsException, BadPathException, BadRegexException

class testCases(unittest.TestCase):

    def setUp(self):
        self.ge = GrepEngine()
        self.path = 'test-data'
        
    def tearDown(self):
        pass

    def testFindSimple(self):
        results = self.ge.grep('foo', self.path, 0, True)
        self.assertTrue(len(results) == 1)
        self.checkResult(results[0], "File1", "linefoo", "2")

    def testNoMatches(self):
        with self.assertRaises(NoResultsException):
            results = self.ge.grep('idonotexistidonotexistidonotexist', self.path, 0, True)

    def testDoubleQuote(self):
        results = self.ge.grep('"stdio.h', self.path, 0, True)
        self.assertTrue(len(results) == 1)
        self.checkResult(results[0], 'FolderA/File2', '#include "stdio.h"', '1')
    
    def testDoubleQuotes(self):
        results = self.ge.grep('"stdio.h"', self.path, 0, True)
        self.assertTrue(len(results) == 1)
        self.checkResult(results[0], 'FolderA/File2', '#include "stdio.h"', '1')
    
    def testStringStartingWithHash(self):
        results = self.ge.grep('#include', self.path, 0, True)
        self.assertTrue(len(results) == 1)
        self.checkResult(results[0], 'FolderA/File2', '#include "stdio.h"', '1')

    def testAngleBrackets(self):
        results = self.ge.grep('<stdio.h>', self.path, 0, True)
        self.assertTrue(len(results) == 1)
        self.checkResult(results[0], 'FolderA/File2', '@fnclude <stdio.h>', '2')
    
    def testBackslash(self):
        results = self.ge.grep('fi\le', self.path, 0, True)
        self.assertTrue(len(results) == 1)
        self.checkResult(results[0], 'FolderA/File1', 'fi\le', '4')
        
    def testPathWithSpaces(self):
        path = 'test-data/Space A'
        results = self.ge.grep('space_marker', path, 0, True)
        self.assertTrue(len(results) == 1)
        self.checkResult(results[0], 'Space File', 'space_marker', '1')
    
    def testIgnoreDirSimple(self):
        self.ge.exclude_dirs.append('FolderA')
        results = self.ge.grep('file', self.path, 0, True)
        self.ge.exclude_dirs = []
        self.assertTrue(len(results) == 2)
        self.checkResult(results[0], "File1", "This is a test file", "1")
        self.checkResult(results[1], "File2", "Another file!", "1")
    
    def testIgnoreDirWithSpaceInPath(self):
        self.ge.exclude_dirs.append('Space A')
        with self.assertRaises(NoResultsException):
            results = self.ge.grep('space_marker', self.path, 0, True)
        self.ge.exclude_dirs = []
        
    
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
