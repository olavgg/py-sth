"""
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
"""
from multiprocessing import Process
from multiprocessing import JoinableQueue
from multiprocessing import Manager
from multiprocessing import active_children
from Queue import Empty

from domain.user import User


class TaskService(object):
    """
    Asynchronous tasks class for storing tasks into a queue so only one
    process can be run concurrently.
    """
    tasks = None
    work_queue = None

    def __init__(self, func, **values):
        """ Constructor """
        if TaskService.tasks is None:
            TaskService.tasks = Manager().dict()
            TaskService.work_queue = JoinableQueue()
        if 'user' not in values:
            values['user'] = User('admin', mock=True)
        if 'wait' not in values:
            values['wait'] = False
        if 'function_name' in values:
            self.name = '{f}'.format(
                f=values['function_name'], u=values['user'].uid)
        else:
            self.name = '{f},{u}'.format(f=func.__name__, u=values['user'].uid)
        if TaskService.find_task_by_name(self.name):
            raise ValueError('Task {n} already exists'.format(n=self.name))
        self.func = func
        self.values = values
        TaskService.tasks[self.name] = self
        TaskService.work_queue.put(self.name)
        from flask import current_app as app
        app.logger.debug("Added process: {name}".format(name=self.name))
        max_p = app.config['MAX_PROCESSES']
        if len([1 for v in active_children() if isinstance(v, Worker)]) < max_p:
            worker = Worker(TaskService.work_queue, wait=values['wait'])
            worker.start()

    def __str__(self):
        """ Return the task name """
        return self.name

    def remove(self):
        """ Delete the Task """
        del (TaskService.tasks[self.name])
        del self

    @staticmethod
    def find_task_by_name(name):
        """ Find task by name """
        task = [val for key, val in TaskService.tasks.items() if key == name]
        if task:
            return task[0]
        return None


class Worker(Process):
    """ Worker class """

    def __init__(self, work_queue, wait=False):
        """ Constructor """
        Process.__init__(self)
        self.w_queue = work_queue
        self.wait = wait

    def run(self):
        """ Executes a worker """
        while True:
            task = None
            try:
                name = self.w_queue.get(block=self.wait, timeout=3)
                task = TaskService.find_task_by_name(name)
                task.func(task.values)
                task.remove()
                self.w_queue.task_done()
            except Empty:
                break
            except Exception, err:
                from flask import current_app as app
                app.logger.exception(str(err))
                task.remove()
                self.w_queue.task_done()
                break
