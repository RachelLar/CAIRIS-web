#!/usr/bin/python
#  Licensed to the Apache Software Foundation (ASF) under one
#  or more contributor license agreements.  See the NOTICE file
#  distributed with this work for additional information
#  regarding copyright ownership.  The ASF licenses this file
#  to you under the Apache License, Version 2.0 (the
#  "License"); you may not use this file except in compliance
#  with the License.  You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing,
#  software distributed under the License is distributed on an
#  "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
#  KIND, either express or implied.  See the License for the
#  specific language governing permissions and limitations
#  under the License.
import sys
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.wsgi import WSGIContainer
import WebConfig

def start(args):
    options = {
        'port': 0,
        'unitTesting': False
    }

    if len(args) > 1:
        for arg in args[1:]:
            if arg == '-d':
                options['loggingLevel'] = 'debug'
            if arg == '--unit-test':
                options['unitTesting'] = True

    WebConfig.config(options)
    if options['unitTesting']:
        import IRISDaemon
        from Borg import Borg
        b = Borg()
        b.logger.info('Starting Werkzeug server')
        client = IRISDaemon.start()
        if client is not None:
            return client
    else:
        from IRISDaemon import app
        from Borg import Borg
        b = Borg()
        http_server = HTTPServer(WSGIContainer(app))
        http_server.listen(b.webPort)

        try:
            b.logger.info('Starting Tornado server')
            IOLoop.instance().start()
        except KeyboardInterrupt:
            print "stop"
            IOLoop.instance().stop()


if __name__ == '__main__':
  start(sys.argv)
