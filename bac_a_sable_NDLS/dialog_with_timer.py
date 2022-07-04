from typing import Optional
import c4d

doc: c4d.documents.BaseDocument  # The active document
op: Optional[c4d.BaseObject]  # The active object, None if unselected

NAME_OBJ_DEPTHMAP = 'depthmap'
NAME_TAG_ALTS = 'altitudes_initiales'
NAME_TAG_GRADIENT = 'gradient'


class DlgBbox(c4d.gui.GeDialog):


    TIME_INTERVAL = 1000 #milliseconds

    TXT_BTON_TIMER_ON = "stop process"
    TXT_BTON_TIMER_OFF = "start process"

    ID_BTON_TEST = 1000

    timer = False

    def CreateLayout(self):

        self.SetTitle("Bac à sable")
        self.GroupBegin(500, flags=c4d.BFH_CENTER, cols=1, rows=1)
        self.AddButton(self.ID_BTON_TEST, flags=c4d.BFH_CENTER, initw=300, inith=50, name=self.TXT_BTON_TIMER_OFF)

        return True

    def Command(self, id, msg):
        if id == self.ID_BTON_TEST:
            if self.timer:
                self.timer = False
                self.SetTimer(0)
                self.SetString(self.ID_BTON_TEST,self.TXT_BTON_TIMER_OFF)
            else:
                self.timer = True
                self.SetTimer(self.TIME_INTERVAL)
                self.SetString(self.ID_BTON_TEST,self.TXT_BTON_TIMER_ON)
        return True

    def Timer(self,msg):
        print('test')
        
class Sandbox(object):
    def __init__(self,depthmap_obj,tag_alts,tag_gradient):
        self.depthmap_obj = depthmap_obj
        self.tag_alts = tag_alts
        self.tag_gradient = tag_gradient
        

def main() -> None:
    depthmap_obj = doc.SearchObject(NAME_OBJ_DEPTHMAP)
    
    #TODO : error
    if not depthmap_obj:
        print('No depthmap object')
        return
    tag_alts = None
    tag_gradient = None
    for tag in depthmap_obj.GetTags():
        if tag.CheckType(c4d.Tvertexmap):
            if tag.GetName()==NAME_TAG_ALTS:
                tag_alts = tag
        if tag.CheckType(c4d.Tvertexmap):
            if tag.GetName()==NAME_TAG_GRADIENT:
                tag_gradient = tag
    #TODO : error
    if not tag_alts or not tag_gradient:
        print('manque un tag')
    
"""
def state():
    # Defines the state of the command in a menu. Similar to CommandData.GetState.
    return c4d.CMD_ENABLED
"""

if __name__ == '__main__':
    main()
    #dlg = DlgBbox()
    #dlg.Open(c4d.DLG_TYPE_ASYNC)
    