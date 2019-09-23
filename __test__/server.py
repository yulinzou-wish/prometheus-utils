import os
import sys
import threading
import logging
import time
from tornado import ioloop, httpserver
import tornado.options
from tornado.options import options, define
from tornado.web import Application
from __test__.handlers.test_handler import TestHandler
from prometheus_utils import PromClient

class TestWebServer(object):
    """ Wrappered tornado.web.Application """
    def __init__(self):
        self._test_app = TestApplication()

    def start(self):
        """ will start TestApplication """
        logging.info("Starting Test Application ...")

        # Start test app
        self._test_app.start()


class TestApplication(Application):
    def start(self):
        """ Wrapper function for TestHandler.test """
        logging.info("Test Application started")
        TestHandler().test()


if __name__ == "__main__":
    define('env', type=str, default='stage')
    tornado.options.parse_command_line(None)

    PromClient.init_instance()

    try:
        TestWebServer().start()
    except:
        logging.exception("Unknown error")
        sys.exit(1)

