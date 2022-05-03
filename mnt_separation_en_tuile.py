from typing import Optional
import c4d
from math import floor
import numpy as np

doc: c4d.documents.BaseDocument  # The active document
op: Optional[c4d.BaseObject]  # The active object, None if unselected


def extractMNTpart(id_col,id_row):
    return

def main() -> None:
    # Called when the plugin is selected by the user. Similar to CommandData.Execute.
    nb_pt_x = 20
    nb_pt_z = 12
    
    arr = np.array([p for p in op.GetAllPoints()])
    newarr = arr.reshape(nb_pt_z,nb_pt_x,)
    
    div_x = 4
    div_z = 2
    nb_pces = div_x * div_z
    
    
    nb_pt_x_par_elem = floor((nb_pt_x-1)/div_x+1)
    nb_pt_z_par_elem = floor((nb_pt_z-1)/div_z+1)
    
    id_pt = 0
    #calcul des CPolygon
    polys = []
    for ncol in range(nb_pt_z_par_elem-1):
        for nrow in range(nb_pt_x_par_elem-1):
            a = id_pt
            b = a+1
            c = b+nb_pt_x_par_elem
            d = c-1
            polys.append(c4d.CPolygon(a,b,c,d))
            id_pt+=1
        id_pt+=1
    
    for n in range(nb_pces):
        pts=list(newarr[0:nb_pt_z_par_elem,0:nb_pt_x_par_elem].flatten())
        #print(len(pts))
        
        poly = c4d.PolygonObject(len(pts),len(polys))
        poly.SetAllPoints(pts)
        for i,p in enumerate(polys):
            poly.SetPolygon(i,p)
        poly.InsertUnderLast(op)
        poly.Message(c4d.MSG_UPDATE)
        c4d.EventAdd()
        return
    
            
            

"""
def state():
    # Defines the state of the command in a menu. Similar to CommandData.GetState.
    return c4d.CMD_ENABLED
"""

if __name__ == '__main__':
    main()