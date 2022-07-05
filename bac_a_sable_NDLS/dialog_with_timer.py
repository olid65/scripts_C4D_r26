from typing import Optional
import c4d

doc: c4d.documents.BaseDocument  # The active document
op: Optional[c4d.BaseObject]  # The active object, None if unselected

NAME_OBJ_DEPTHMAP = 'depthmap'
NAME_TAG_ALTS = 'altitudes_initiales'
NAME_TAG_GRADIENT = 'gradient'


class DlgBbox(c4d.gui.GeDialog):


    TIME_INTERVAL = 10000 #milliseconds

    TXT_BTON_TIMER_ON = "stop process"
    TXT_BTON_TIMER_OFF = "start process"

    ID_BTON_TEST = 1000

    timer = False

    def __init__(self,sandbox):
        self.sandbox = sandbox

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
        self.sandbox.update()
        c4d.EventAdd()
        c4d.CallCommand(12163) # Render View

class Sandbox(object):

    FN_ASCII = '/Users/olivierdonze/switchdrive/Mandats/Nuit_de_la_science/Programmation_bac_a_sable/depthmap.asc'
    FN_TREES = '/Users/olivierdonze/switchdrive/Mandats/Nuit_de_la_science/Programmation_bac_a_sable/tags.json'

    SCALE_ALT = 200


    def __init__(self,depthmap_obj,tag_alts,tag_gradient,doc):
        self.depthmap_obj = depthmap_obj
        self.tag_alts = tag_alts
        self.tag_gradient = tag_gradient
        self.doc = doc

    def update(self):
        self.update_terrain()

    def update_terrain(self):
        pts = self.depthmap_obj.GetAllPoints()
        alts = self.get_alts_from_ascii()
        alts_initial = self.tag_alts.GetAllHighlevelData()
        gradient_values = self.tag_gradient.GetAllHighlevelData()

        for pt,alt,alt_initial,grad_val in zip(pts,alts,alts_initial,gradient_values):
            pt.y =alt*grad_val

        self.depthmap_obj.SetAllPoints(pts)
        self.depthmap_obj.Message(c4d.MSG_UPDATE)


    def get_alts_from_ascii(self,header_size = 6):
        """returns a list of heights multiplied by the scale factor
           from an asc file of type Esri grid ascii (with 6 lines header)"""
        alts = []
        with open(self.FN_ASCII) as f:
            for i,line in enumerate(f):
                #we don't need the header (6 lines)
                if i>=header_size:
                    alts += [float(alt)*self.SCALE_ALT for alt in line.split()]
        return alts


def get_sandbox(doc) -> Sandbox:
    depthmap_obj = doc.SearchObject(NAME_OBJ_DEPTHMAP)

    #TODO : gestion erreurs
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

    #TODO : gestion erreurs
    if not tag_alts or not tag_gradient:
        print('manque un tag')

    return Sandbox(depthmap_obj,tag_alts,tag_gradient,doc)
"""
def state():
    # Defines the state of the command in a menu. Similar to CommandData.GetState.
    return c4d.CMD_ENABLED
"""

if __name__ == '__main__':
    #main()
    sandbox = get_sandbox(doc)
    dlg = DlgBbox(sandbox)
    dlg.Open(c4d.DLG_TYPE_ASYNC)