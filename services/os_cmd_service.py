from subprocess import Popen, PIPE

from flask import current_app as app


class OSCommandService(object):
    """
    Executes an operating system command
    """

    @staticmethod
    def executeCommand(command):
        output = Popen(command, shell=True, stdout=PIPE, stderr=PIPE)
        data = output.communicate()
        lines = data[0].splitlines()
        error = data[1]
        output.wait()
        if output.returncode != 0:
            error_msg = u"Couldn't execute command: %s" % command
            app.logger.exception("Error description: " + error_msg)
            app.logger.exception("Internal error description: " + error)
            return False, error
        return lines, None
