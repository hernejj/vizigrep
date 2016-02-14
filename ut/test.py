#!/usr/bin/python

import unittest
import ut_GrepEngine, ut_Regex

##########
# Create and return a test suite for this set of tests.
##########
def suite():
    suite = unittest.TestSuite()
    
    suite.addTest(ut_GrepEngine.suite())
    suite.addTest(ut_Regex.suite())
    return suite


##########
# MAIN: Execute the tests in this file.
##########
if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())

