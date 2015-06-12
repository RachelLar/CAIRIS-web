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

import os
import logging
from string import strip

from Borg import Borg
import DatabaseProxyFactory
from tools.GraphicsGenerator import GraphicsGenerator
from MySQLDatabaseProxy import MySQLDatabaseProxy


def initialise():
  b = Borg()
  b.runmode = 'desktop'
  b.logger = logging.getLogger('cairisd')
  
  homeDir = os.getenv("HOME")
  if homeDir is not None:
    cairisRoot = homeDir + "/CAIRIS/cairis"
  else:
    raise RuntimeError('The HOME environment variable is not defined.')
 
  cfgFileName = ''
  try:
    cfgFileName = os.environ['CAIRIS_CFG']
  except KeyError:
    cfgFileName = cairisRoot + '/cairis/config/cairis.cnf'

  if not os.path.exists(cfgFileName):
    raise IOError('''Unable to locate configuration file at the following location:
'''+cfgFileName) 

  cfgFile = open(cfgFileName)
  for cfgLine in cfgFile.readlines():
    cfgTuple = cfgLine.split('=')
    cfgKey = strip(cfgTuple[0])
    cfgVal = strip(cfgTuple[1])
 
    if cfgKey == 'dbhost':
      b.dbHost = cfgVal
    elif cfgKey == 'dbport':
      b.dbPort = int(cfgVal)
    elif cfgKey == 'dbuser':
      b.dbUser = cfgVal
    elif cfgKey == 'dbpasswd':
      b.dbPasswd = cfgVal
    elif cfgKey == 'dbname':
      b.dbName = cfgVal
    elif cfgKey == 'tmp_dir': 
      b.tmpDir = cfgVal
    elif cfgKey == 'root':
      if os.path.exists(cfgVal): 
         b.cairisRoot = cfgVal
      else:
         print('The root directory of CAIRIS specified in the config file is invalid.\nSpecified path: %s' % cfgVal)
         exit(6)
  cfgFile.close()

  b.dbProxy = DatabaseProxyFactory.build()

  pSettings = b.dbProxy.getProjectSettings()
  b.fontSize = pSettings['Font Size']
  b.apFontSize = pSettings['AP Font Size']
  b.fontName = pSettings['Font Name']

  b.imageDir = b.cairisRoot + '/cairis/images' 
  b.configDir = b.cairisRoot + '/cairis/config'
  b.exampleDir = os.path.join(b.cairisRoot, 'examples')

  b.docBookDir = 'http://www.docbook.org/sgml/4.5'
  if os.path.exists('/usr/share/sgml/docbook/dtd/4.5'):
    b.docBookDir = '/usr/share/sgml/docbook/dtd/4.5'
  else:
    b.logger.warning('Unable to find DocBook schemes. Check if DocBook is correctly installed.')

  b.mainFrame = None

def dInitialise(configFile):
  b = Borg()
  b.runmode = 'web'
  b.settings = dict()
  b.logger = logging.getLogger('cairisd')

  homeDir = os.getenv("HOME")
  if homeDir is not None:
    cairisRoot = os.path.join(homeDir, "CAIRIS/cairis")
  else:
    raise RuntimeError('The HOME environment variable is not defined.')

  cfgFileName = ''
  try:
    cfgFileName = os.environ['CAIRIS_CFG']
  except KeyError:
    cfgFileName = cairisRoot + '/cairis/config/cairis.cnf'

  if configFile is not '':
    if os.path.exists(configFile):
      cfgFileName = configFile
    else:
      raise IOError('''Unable to locate configuration file at the following location:
  '''+configFile)

  try:
    cfgFile = open(cfgFileName)
    for cfgLine in cfgFile.readlines():
      cfgTuple = cfgLine.split('=')
      cfgKey = strip(cfgTuple[0])
      cfgVal = strip(cfgTuple[1])

      if cfgKey == 'tmp_dir':
        b.tmpDir = cfgVal
      elif cfgKey == 'upload_dir':
        b.uploadDir = cfgVal
      elif cfgKey == 'root':
      	b.cairisRoot = cfgVal
      elif cfgKey == 'web_port':
        try:
          b.webPort = int(cfgVal)
        except TypeError, ex:
          b.logger.error(str(ex.message))
          b.webPort = 0
      elif cfgKey == 'log_level':
        log_level = cfgVal.lower()
        if log_level == 'debug':
            b.logLevel = logging.DEBUG
        elif log_level == 'none':
            b.logLevel = logging.FATAL
        elif log_level == 'info':
            b.logLevel = logging.INFO
        elif log_level == 'error':
            b.logLevel = logging.ERROR
        else:
            b.logLevel = logging.WARNING

    cfgFile.close()
  except IOError as ex:
    print('Unable to read config file: %s\nFilename: %s' % (ex.strerror, cfgFileName))
    exit(5)

  b.imageDir = os.path.join(b.cairisRoot, 'cairis/images')
  b.configDir = os.path.join(b.cairisRoot, 'cairis/config')
  b.exampleDir = os.path.join(b.cairisRoot, 'examples')
  if not hasattr(b, 'uploadDir'):
      b.uploadDir = os.path.join(b.cairisRoot, 'cairis/static')

  paths = {
    'root': b.cairisRoot,
    'image': b.imageDir,
    'configuration files': b.configDir,
    'examples': b.exampleDir,
    'upload': b.uploadDir
  }

  for key, path in paths.items():
    if not os.path.exists(path):
      err_msg = 'The {0} directory of CAIRIS is inaccessible or not existing.{1}Path: {2}'.format(key, os.linesep, path)
      b.logger.error(err_msg)
      exit(6)

  image_upload_dir = os.path.join(b.uploadDir, 'images')
  if os.path.exists(image_upload_dir):
    try:
      test_file = os.path.join(image_upload_dir, 'test.txt')
      fs_test = open(test_file, 'wb')
      fs_test.write('test')
      fs_test.close()
      os.remove(test_file)
    except IOError:
      err_msg = 'The upload directory for images is not writeable. Image uploading will propably not work.'
      b.logger.warning(err_msg)
  else:
    try:
      os.mkdir(image_upload_dir, 0775)
    except IOError:
      err_msg = 'Unable to create directory to store images into. Image uploading will probably not work.'
      b.logger.warning(err_msg)

  b.model_generator = GraphicsGenerator('svg')

  b.docBookDir = 'http://www.docbook.org/sgml/4.5'
  if os.path.exists('/usr/share/sgml/docbook/dtd/4.5'):
    b.docBookDir = '/usr/share/sgml/docbook/dtd/4.5'
  else:
    b.logger.warning('Unable to find DocBook schemes. Check if DocBook is correctly installed.')

  b.settings['test'] = {
    'session_id': 'test',
    'fontSize': '13',
    'fontName': 'Times New Roman',
    'jsonPrettyPrint': True,
    'apFontSize': '7.5',
    'dbHost': '127.0.0.1',
    'dbPort': 3306,
    'dbUser': 'cairis',
    'dbPasswd': 'cairis123',
    'dbName': 'cairis'
  }

  db_proxy = MySQLDatabaseProxy(
    host=b.settings['test']['dbHost'],
    port=b.settings['test']['dbPort'],
    user=b.settings['test']['dbUser'],
    passwd=b.settings['test']['dbPasswd'],
    db=b.settings['test']['dbName']
  )

  if db_proxy.conn.open:
      db_proxy.close()

  b.settings['test']['dbProxy'] = db_proxy