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


import wx
import armid
import DocumentReference
from DocumentReferenceDialog import DocumentReferenceDialog
from DialogClassParameters import DialogClassParameters
import ARM
from DimensionBaseDialog import DimensionBaseDialog

class DocumentReferencesDialog(DimensionBaseDialog):
  def __init__(self,parent):
    DimensionBaseDialog.__init__(self,parent,armid.DOCUMENTREFERENCES_ID,'Document References',(930,300),'persona.png')
    self.theMainWindow = parent
    idList = [armid.DOCUMENTREFERENCES_REFLIST_ID,armid.DOCUMENTREFERENCES_BUTTONADD_ID,armid.DOCUMENTREFERENCES_BUTTONDELETE_ID]
    columnList = ['Name','Contributor']
    self.buildControls(idList,columnList,self.dbProxy.getDocumentReferences,'document_reference')
    listCtrl = self.FindWindowById(armid.DOCUMENTREFERENCES_REFLIST_ID)
    listCtrl.SetColumnWidth(0,900)
    wx.EVT_COMBOBOX(self,armid.DOCUMENTREFERENCES_COMBOEXTERNALDOCUMENT_ID,self.onExternalDocumentChange)


  def addObjectRow(self,listCtrl,listRow,objt):
    listCtrl.InsertStringItem(listRow,objt.name())
    listCtrl.SetStringItem(listRow,1,objt.contributor())

  def onAdd(self,evt):
    try:
      addParameters = DialogClassParameters(armid.DOCUMENTREFERENCE_ID,'Add Document Reference',DocumentReferenceDialog,armid.DOCUMENTREFERENCE_BUTTONCOMMIT_ID,self.dbProxy.addDocumentReference,True)
      self.addObject(addParameters)
    except ARM.ARMException,errorText:
      dlg = wx.MessageDialog(self,str(errorText),'Add document reference',wx.OK | wx.ICON_ERROR)
      dlg.ShowModal()
      dlg.Destroy()
      return

  def onUpdate(self,evt):
    selectedObjt = self.objts[self.selectedLabel]
    objtId = selectedObjt.id()
    try:
      updateParameters = DialogClassParameters(armid.DOCUMENTREFERENCE_ID,'Edit Document Reference',DocumentReferenceDialog,armid.DOCUMENTREFERENCE_BUTTONCOMMIT_ID,self.dbProxy.updateDocumentReference,False)
      self.updateObject(selectedObjt,updateParameters)
    except ARM.ARMException,errorText:
      dlg = wx.MessageDialog(self,str(errorText),'Edit document reference',wx.OK | wx.ICON_ERROR)
      dlg.ShowModal()
      dlg.Destroy

  def onDelete(self,evt):
    try:
      self.deleteObject('No document reference','Delete document reference',self.dbProxy.deleteDocumentReference)
    except ARM.ARMException,errorText:
      dlg = wx.MessageDialog(self,str(errorText),'Delete document reference',wx.OK | wx.ICON_ERROR)
      dlg.ShowModal()
      dlg.Destroy

  def onExternalDocumentChange(self,evt):
    docName = self.docCtrl.GetStringSelection()
    listCtrl = self.FindWindowById(armid.DOCUMENTREFERENCES_REFLIST_ID)
    listCtrl.DeleteAllItems()
    try:
      self.objts = self.dbProxy.getExternalDocumentReferences(docName)
      listRow = 0
      keyNames = self.objts.keys()
      keyNames.sort()
      for keyName in keyNames:
        objt = self.objts[keyName]
        self.addObjectRow(listCtrl,listRow,objt)
        listRow += 1
    except ARM.ARMException,errorText:
      dlg = wx.MessageDialog(self,str(errorText),'Filter document references',wx.OK | wx.ICON_ERROR)
      dlg.ShowModal()
      dlg.Destroy()
      return
