#!/usr/bin/env python
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

Created on Dec 8, 2012

@Author: Olav Groenaas Gjerde
"""
import logging
import os
import sys
from Crypto.Util.number import getRandomInteger
from datetime import timedelta
from flask import jsonify

from flask import Flask

from conf.boostrap import Bootstrap
from conf.base import Base


class PYSTHClient(object):
    """
    Main class for application startup
    """
    controllers = []

    @staticmethod
    def init_controllers(app):
        """
        Imports all controllers and register pages
        """
        for controller in os.listdir(os.getcwd() + "/controllers"):
            module_name, ext = os.path.splitext(controller)
            if module_name.endswith('_controller') and ext == '.py':
                module = __import__("controllers.%s" % module_name)
                PYSTHClient.controllers.append(
                    module.__getattribute__(module_name))
        for controller in PYSTHClient.controllers:
            app.register_blueprint(controller.PAGE)

    @staticmethod
    def start():
        """
        Start the application
        """
        config_type = 'DevelopmentConfig'
        if len(sys.argv) == 2:
            if sys.argv[1] == "dev":
                config_type = 'DevelopmentConfig'
            elif sys.argv[1] == "test":
                config_type = 'TestConfig'
            elif sys.argv[1] == "prod":
                config_type = 'ProductionConfig'
        app = Flask(__name__)
        app.config.from_object('conf.config.%s' % config_type)
        app.secret_key = getRandomInteger(128)
        app.permanent_session_lifetime = timedelta(seconds=10)
        FORMAT = "%(asctime)s %(levelname)s: " \
                 "%(message)s [in %(pathname)s:%(lineno)d]"
        logging.basicConfig(
            filename=app.config["LOGFILE"],
            level=logging.DEBUG,
            format=FORMAT
        )
        PYSTHClient.init_controllers(app)

        @app.errorhandler(400)
        def bad_request(exception):
            """Bad Request"""
            data = dict(
                status=exception.code,
                error=str(exception),
                description=bad_request.__doc__
            )
            return jsonify(data), 400

        @app.errorhandler(404)
        def page_not_found(exception):
            """Page Not Found"""
            data = dict(
                status=exception.code,
                error=str(exception),
                description=page_not_found.__doc__
            )
            return jsonify(data), 404

        if app.config['DEBUG'] is True:
            @app.errorhandler(500)
            def error(exception):
                """Internal Server Error"""
                data = dict(
                    status=exception.code,
                    error=str(exception),
                    description=error.__doc__
                )
                return jsonify(data), 500

        @app.errorhandler(403)
        def forbidden(exception):
            """Forbidden"""
            data = dict(
                status=exception.code,
                error=str(exception),
                description=forbidden.__doc__
            )
            return jsonify(data), 403

        # noinspection PyUnusedLocal
        @app.before_first_request
        def bootstrap():
            """
            Call the bootstrap function
            """
            Bootstrap()

        with app.app_context():
            Base.do_first_request()
        app.run(app.config["HOST"], app.config["PORT"])


if __name__ == '__main__':
    PYSTHClient.start()