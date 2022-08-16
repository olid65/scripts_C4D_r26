from typing import Optional
import c4d
from c4d import gui

doc: c4d.documents.BaseDocument  # The active document
op: Optional[c4d.BaseObject]  # The active object, None if unselected

class YourDialog(gui.GeDialog):

    BUTTON_ID = 1001
    DIALOG_ID = 1002   

    def CreateLayout(self):
        self.SetTitle("Web Browser")
        self.MenuFlushAll()
        self.TabGroupBegin(1003, 5)
        
        self.AddButton(self.BUTTON_ID, c4d.BFH_SCALE|c4d.BFV_SCALE, 25, 25, "Close Dialog")
        viewer = self.AddCustomGui(self.DIALOG_ID, c4d.CUSTOMGUI_HTMLVIEWER, "pyBROWSER", c4d.BFH_SCALEFIT|c4d.BFV_SCALEFIT, 1024, 512, c4d.BaseContainer())
        viewer.SetUrl("https://ge.ch/sitg/sitg_catalog/data_details/8e9e9638-eef1-41e9-91d6-d49bc5aa9996/xhtml", c4d.URL_ENCODING_UTF16)
        
        self.GroupEnd()
        self.InitValues()
        return True

    def Command(self, id, msg):
        if id==self.BUTTON_ID:
            self.Close()
        return True



if __name__=='__main__':
    dlg = YourDialog()
    #DLG_TYPE_MODAL = > synchronous dialog
    #DLG_TYPE_ASYNC = > asynchronous dialogs
    dlg.Open(dlgtype=c4d.DLG_TYPE_MODAL_RESIZEABLE, pluginid=1006, defaultw=1024, defaulth=576, subid=1005)
    