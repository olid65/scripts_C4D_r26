from typing import Optional
import c4d
import os
import json
from pprint import pprint

doc: c4d.documents.BaseDocument  # The active document
op: Optional[c4d.BaseObject]  # The active object, None if unselected

CONTAINER_ORIGIN =1026473
#LOCATIONS_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)),'noms_lieux.json')

FN = '/Users/olivierdonze/Library/Preferences/Maxon/Maxon Cinema 4D R26_8986B2D7/plugins/swisstopo_extractor/noms_lieux.json'

class MonDlg(c4d.gui.GeDialog):
    def __init__(self):
        self.localites = []
        self.coords = []
        #lecture du fichier des lieux
        if os.path.isfile(FN):
            with open(FN, encoding = 'utf-8') as f:
                dico_lieux = json.load(f)
                
                for loc,coord in dico_lieux.items():
                    self.localites.append(loc)
                    self.coords.append(coord)
        

    def CreateLayout(self):
        self.SetTitle('Localisation: ')
        self.GroupBegin(1000,flags=c4d.BFH_SCALEFIT, cols=3, rows=1)
        self.GroupBorderSpace(10, 10, 10, 0)                                  
        self.AddComboBox(1004,flags=c4d.BFH_MASK, initw=400, allowfiltering=True) 
        
        for i,lieu in enumerate(self.localites):
            self.AddChild(1004,i,lieu)

        self.GroupEnd()
        return True
        
    def Command(self,id,msg): 
        if id==1004 : 
            res = self.GetLong(1004)
            x,z = self.coords[res]
            coord = c4d.Vector(x,0,z)
            #si le doc n'est pas georef -> on geoloc avec l'emplecemnt
            if not doc[CONTAINER_ORIGIN]:
                doc[CONTAINER_ORIGIN] = coord
            
            bd = doc.GetActiveBaseDraw()
            camera = bd.GetSceneCamera(doc)
            if not camera[c4d.CAMERA_PROJECTION] == c4d.Ptop:
                c4d.gui.MessageDialog("Vous devez être sur une caméra ou une vue de haut")
                return True
            
            mg = camera.GetMg()
            mg.off = coord-doc[CONTAINER_ORIGIN]
            camera.SetMg(mg)
            c4d.EventAdd()
            

        return True


def main() -> None:
    bd = doc.GetActiveBaseDraw()
    camera = bd.GetSceneCamera(doc)
    if not camera[c4d.CAMERA_PROJECTION] == c4d.Ptop:
        c4d.gui.MessageDialog("Vous devez être sur une caméra ou une vue de haut")
        return
    print(camera.GetMg().off)
    
    
"""
def state():
    # Defines the state of the command in a menu. Similar to CommandData.GetState.
    return c4d.CMD_ENABLED
"""

if __name__ == '__main__':
    #main()
    dlg = MonDlg()
    dlg.Open(c4d.DLG_TYPE_ASYNC)