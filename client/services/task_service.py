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

Created on Jan 8, 2013

@Author: Olav Groenaas Gjerde
'''
from multiprocessing import Process
from multiprocessing import JoinableQueue
from multiprocessing import Manager
from multiprocessing import active_children
from Queue import Empty

from conf import LOG

class TaskService(object):
    ''' 
    Asynchronous tasks class for storing tasks so only one type can be run.
    A Queue implementation should be added.
    '''
    tasks = None
    work_queue = None

    def __init__(self, func, **values):
        ''' Constructor '''
        if TaskService.tasks == None:
            TaskService.tasks = Manager().dict()
            TaskService.work_queue = JoinableQueue()
        self.name = '{f},{u}'.format(f=func.__name__, u=values['user'].uid)
        if TaskService.find_task_by_name(self.name):
            raise ValueError('Task {n} already exists'.format(n=self.name))
        self.func = func
        self.values = values
        TaskService.tasks[self.name] = self
        TaskService.work_queue.put(self.name)
        if len(active_children()) < 2:
            worker = Worker(TaskService.work_queue)
            worker.start()
        
    def __str__(self):
        ''' Return the task name '''
        return self.name
        
    def remove(self):
        ''' Delete the Task '''
        LOG.debug('Deleting task: {t}'.format(t=self.name))
        del(TaskService.tasks[self.name])
        del(self)
        
    @staticmethod
    def find_task_by_name(name):
        ''' Find task by name '''
        task = [val for key,val in TaskService.tasks.items() if key == name]
        if task:
            return task[0]
        return None
        
class Worker(Process):
    ''' Worker class '''
    
    def __init__(self, work_queue):
        ''' Constructor '''
        Process.__init__(self)
        self.w_queue = work_queue
        self.kill_received = False

    def run(self):
        ''' Executes a worker '''
        while not self.kill_received:
            try:
                name = self.w_queue.get()
                task = TaskService.find_task_by_name(name)
                LOG.debug("Starting " + str(task) + " ...")
                task.func(task.values)
                task.remove()
            except Empty:
                break
            finally:
                self.w_queue.task_done()
