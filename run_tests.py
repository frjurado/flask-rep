######################################
#  temporary tool for running TESTS  #
######################################
#                                    #
# testing is handled more elegantly  #
# from the 'manage.py' file,         #
# but that must wait until           #
# we use Flask-Script.               #
#                                    #
######################################

import unittest

tests = unittest.TestLoader().discover('tests')

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(tests)
