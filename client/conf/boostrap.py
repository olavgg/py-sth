'''
Copyright (C) <2012> <Olav Groenaas Gjerde>

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

Created on Dec 23, 2012

@Author: Olav Groenaas Gjerde
'''
from domain.user import User

class Bootstrap(object):
    '''
    Bootstrap class, use this file to configure and setup data 
    that's needed for each environment.
    '''
    
    def __init__(self, base):
        '''
        Constructor, based on the environment settings,
        run the method for data initialization.
        '''
        if base.app.config['DEBUG'] == True:
            Bootstrap.init_dev_data()
        elif base.app.config['TESTING'] == True:
            Bootstrap.init_test_data()
        
    @staticmethod
    def init_dev_data():
        ''' Init dev data '''
        User('olav')
        User('olavgg')
        
    @staticmethod
    def init_test_data():
        ''' Init test data '''
        User('olav')
        User('olavgg')
        
    @staticmethod
    def init_prod_data():
        ''' Init prod data '''
        pass