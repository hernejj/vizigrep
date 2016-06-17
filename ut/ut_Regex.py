#!/usr/bin/python
import unittest, re

class testCases(unittest.TestCase):

    def setUp(self):
        pass
        
    def tearDown(self):
        pass

    def testMatchSimple(self):
        self.checkRegex('foo', 'foo', 'foo')

    def testNoMatch(self):
        self.checkRegex('foo', 'bar', '')
        
    def testMatchDot(self):
        self.checkRegex('abcdefghijk', 'bc.e', 'bcde')
    
    def testMatchDotStar(self):
        self.checkRegex('abcdefghijk', 'bc.*j', 'bcdefghij')
    
    def testMatchGroup(self):
        self.checkRegex('abcdefghijk', 'bc[wvdg]e', 'bcde')
    
    def testMatchGroupStar(self):
        self.checkRegex('abcdefghijk', 'bc[defg]*h', 'bcdefgh')
    
    def testMatchDoubleQuote(self):
        self.checkRegex('Hello"World"', 'o"W', 'o"W')
    
    def testMatchStringStartingWithHash(self):
        self.checkRegex('#include<stdio.h>"', '#inc', '#inc')
    
    def testMatchAngleBrackets(self):
        self.checkRegex('#include<stdio.h>"', '<stdio.h>', '<stdio.h>')
    
    def testMatchBackslash(self):
        self.checkRegex('foo\gbc"', 'o\g', 'o\g')
    
    def checkRegex(self, haystack, needle, expected_match):
        needle = self.escape_regex_str(needle)
        m = re.search(needle, haystack)
        if (not m) and (not expected_match): return
        if not m: self.fail('No match found! haystack=%s, needle=%s, expected_match=%s' % (haystack, needle, expected_match))
        matched_text = m.group()
        self.assertTrue(matched_text == expected_match)
    
    def escape_regex_str(self, regex):
        if '\\' in regex:
            regex = regex.replace('\\', '\\\\')  # Escape \
        return regex
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
