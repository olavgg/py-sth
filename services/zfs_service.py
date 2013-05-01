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

Created on May 1, 2013

@Author: Olav Groenaas Gjerde
"""
from domain.user import User
from services.os_cmd_service import OSCommandService


class ZFSService(object):
    """
    Handles creation and destruction of ZFS filesystems
    """
    # TODO: Enable asynchronous destroy on pool 'tank' when its in ZFS

    def __init__(self, uid):
        """
        Constructor
        """
        self.uid = uid

    def create(self, size):
        """
        Create a regular filesystem
        """
        shell_script = """
        zfs create -o quota={size}G tank/home/{uid};
        mkdir /tank/temp/{uid}/{uid};
        chown -R {uid}:{uid} /tank/temp/{uid}/{uid};
        """.format(size=size, uid=self.uid)
        result = self.__execute(shell_script)
        if result is False:
            User(self.uid)
        return result


    def create_anonymous(self, size):
        """
        Create a temporary filesystem for an anonymous user
        """
        shell_script = """
        zfs create -o quota={size}G tank/temp/{uid};
        mkdir /tank/temp/{uid}/{uid};
        chown -R {uid}:{uid} /tank/temp/{uid}/{uid};
        """.format(size=size, uid=self.uid)
        result = self.__execute(shell_script)
        if result is False:
            User(self.uid)
        return result

    def destroy(self, user):
        """
        Destroys the filesystem
        """
        if not isinstance(user, User):
            return dict(error=u"User doesn't exist")
        shell_script = """
        zfs destroy -f {fs}
        """.format(fs=user.uid)
        result = self.__execute(shell_script)
        if result is False:
            del User.users[user.uid]
        return result

    def __execute(self, shell_script):
        """
        Executes the command
        """
        result, error = OSCommandService.executeCommand(shell_script)
        if result is False:
            return dict(error=error)
        return True