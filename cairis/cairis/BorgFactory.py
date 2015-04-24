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
from TemplateGenerator import TemplateGenerator


def initialise():
  b = Borg()
  b.runmode = 'desktop'
  b.logger = logging.getLogger('CAIRIS')
  
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
      b.cairisRoot = cfgVal
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
      elif cfgKey == 'root':
        b.cairisRoot = cfgVal
      elif cfgKey == 'web_port':
        try:
          b.webPort = int(cfgVal)
        except TypeError, ex:
          b.logger.error(str(ex.message))
          b.webPort = 0
      elif cfgKey == 'log_level':
        b.logLevel = cfgVal
      elif cfgKey == 'web_static_dir':
        b.staticDir = cfgVal

    cfgFile.close()
  except IOError as ex:
    print('Unable to read config file: %s' % ex.strerror)
    exit(5)

  b.imageDir = os.path.join(b.cairisRoot, '/cairis/images')
  b.configDir = os.path.join(b.cairisRoot, 'cairis/config')
  b.templateDir = os.path.join(b.cairisRoot, 'cairis/templates')
  b.exampleDir = os.path.join(b.cairisRoot, 'examples')

  b.template_generator = TemplateGenerator()
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

  b.settings['test']['dbProxy'] = MySQLDatabaseProxy(
    host=b.settings['test']['dbHost'],
    port=b.settings['test']['dbPort'],
    user=b.settings['test']['dbUser'],
    passwd=b.settings['test']['dbPasswd'],
    db=b.settings['test']['dbName']
  )