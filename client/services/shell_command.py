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

Created on Dec 11, 2012

@Author: Olav Groenaas Gjerde
'''
from subprocess import Popen, PIPE
from conf import LOG

class ShellCommand(object):
    ''' 
    Execute a shell command and return its output. 
    If an error occurs, log it
    '''

    def __init__(self, cmd):
        ''' Constructor '''
        self._cmd = cmd
        
    @property
    def cmd(self):
        ''' Get cmd '''
        return self._cmd
    
    @cmd.setter
    def cmd(self, value):
        ''' Set cmd '''
        self._cmd = value
        
    def run(self):
        ''' Execute the cmd '''
        output = Popen(self.cmd, shell=True, stdout=PIPE, stderr=PIPE)
        data = output.communicate()
        lines = data[0].splitlines()
        error = data[1]
        output.wait()
        if output.returncode != 0:
            errormsg = (
                u"Couldn't execute command: %s"%(self.cmd))
            LOG.exception(errormsg)
            LOG.exception(error)
            lines = False
        if lines != False:
            length = len(lines)
            return lines , length
        else:
            return None