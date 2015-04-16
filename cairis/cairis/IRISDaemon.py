import logging
import os

from Borg import Borg
import BorgFactory


__author__ = 'Robin Quetin'


class IRISDaemon:
    def __init__(self, settings):
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger('IRISDaemon')
        self.logger.info('Starting CAIRIS as web daemon')

        if settings.has_key('configFile'):
            self.loadSettingsFromFile(settings['configFile'])
        else:
            self.loadSettingsFromFile()
        if settings.has_key('staticDir'):
            self.setStaticDir(settings['staticDir'])
        if settings.has_key('port'):
            self.setPort(int(settings['port']))
        if settings.has_key('loggingLevel'):
            self.setLoglevel(settings['loggingLevel'])

        self.logParams()

    def loadSettingsFromFile(self, config_file=''):
        self.logger.info('Loading settings from file...')
        BorgFactory.dInitialise(config_file)

    def setLoglevel(self, log_level):
        b = Borg()
        self.logger.info('Applying log level...')

        log_level = log_level.lower()
        if log_level == 'verbose':
            realLevel = logging.INFO
        elif log_level == 'debug':
            realLevel = logging.DEBUG
        else:
            realLevel = logging.WARNING

        b.logLevel = realLevel

    def setPort(self, port):
        self.logger.info('Applying web port...')
        b = Borg()
        if port == 0:
            if not hasattr(b, 'webPort'):
                b.webPort = 7071
        else:
            b.webPort = port

    def logParams(self):
        b = Borg()
        self.logger.info('Config: %s/cairis.cnf', b.configDir)
        if b.logLevel == logging.INFO:
            self.logger.info('Log level: INFO')
        elif b.logLevel == logging.DEBUG:
            self.logger.info('Log level: DEBUG')
        elif b.logLevel == logging.WARNING:
            self.logger.info('Log level: WARNING')

        self.logger.info('Port: %d', b.webPort)

    def setStaticDir(self, static_dir):
        self.logger.info('Applying web port...')
        b = Borg()
        try:
            os.listdir(static_dir)
        except EnvironmentError as ex:
            self.logger.warning('The directory for static web content is not readable: %s' % ex.strerror)
            self.logger.warning('Static content may not be available')

        b.staticDir = os.path.abspath(static_dir)