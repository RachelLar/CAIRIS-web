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


#$URL$

import argparse
import BorgFactory
from ModelImport import *
from ARM import *

def file_import(importFile, mFormat, overwriteFlag, session_id=None):
  if overwriteFlag == None:
    overwriteFlag = 1

  msgStr = ''
  if (mFormat == 'securitypattern'):
    msgStr += importSecurityPatterns(importFile, session_id=session_id)
  if (mFormat == 'attackpattern'):
    msgStr += importAttackPattern(importFile, session_id=session_id)
  elif (mFormat == 'tvtypes'):
    msgStr += importTVTypeFile(importFile,int(overwriteFlag), session_id=session_id)
  elif (mFormat == 'directory'):
    msgStr += importDirectoryFile(importFile,int(overwriteFlag), session_id=session_id)
  elif (mFormat == 'requirements'):
    msgStr += importRequirementsFile(importFile, session_id=session_id)
  elif (mFormat == 'riskanalysis'):
    msgStr += importRiskAnalysisFile(importFile, session_id=session_id)
  elif (mFormat == 'usability'):
    msgStr += importUsabilityFile(importFile, session_id=session_id)
  elif (mFormat == 'associations'):
    msgStr += importAssociationsFile(importFile, session_id=session_id)
  elif (mFormat == 'project'):
    msgStr += importProjectFile(importFile, session_id=session_id)
  elif (mFormat == 'domainvalues'):
    msgStr += importDomainValuesFile(importFile, session_id=session_id)
  elif (mFormat == 'architecturalpattern'):
    msgStr += importComponentViewFile(importFile, session_id=session_id)
  elif (mFormat == 'synopses'):
    msgStr += importSynopsesFile(importFile, session_id=session_id)
  elif (mFormat == 'processes'):
    msgStr += importProcessesFile(importFile, session_id=session_id)
  elif (mFormat == 'assets'):
    msgStr += importAssetsFile(importFile, session_id=session_id)
  elif (mFormat == 'all'):
    msgStr += importModelFile(importFile,int(overwriteFlag), session_id=session_id)
  else:
    raise ARMException('Input model type ' + mFormat + ' not recognised')
  print msgStr
  return msgStr

if __name__ == '__main__':
  try:
    parser = argparse.ArgumentParser(description='Computer Aided Integration of Requirements and Information Security - Model Import')
    parser.add_argument('modelFile',help='model file to import')
    parser.add_argument('--type',dest='modelFormat',help='model type to import.  One of securitypattern, attackpattern, tvtypes, directory, requirements, riskanalysis, usability, project, domainvalues, architecturalpattern, associations, synopses, processes, assets or all')
    parser.add_argument('--overwrite',dest='isOverwrite',help='Where appropriate, overwrite an existing CAIRIS model with this model')
    args = parser.parse_args() 
    mFormat = args.modelFormat
    importFile = args.modelFile
    overwriteFlag = args.isOverwrite

    BorgFactory.initialise()
    file_import(importFile, mFormat, overwriteFlag)
  except ARMException, e:
    print 'cimport error: ',e
    exit(-1)