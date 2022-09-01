from typing import Optional
import c4d
from random import random
from math import pi

doc: c4d.documents.BaseDocument  # The active document
op: Optional[c4d.BaseObject]  # The active object, None if unselected

RATIO = 1.8 # ratio entre diametre et hauteur (3-> la hauteur est 3 x plus importante que le diam)
TAILLE_SRCE = 10 # taille de référence de la source

def main() -> None:
    if not op: return
    dic = {}
    for o in op.GetChildren():
        if not dic.get(o.GetName(),None):
            dic[o.GetName()] = []
        dic[o.GetName()].append(o)

    res = c4d.BaseObject(c4d.Onull)
    res.SetName(op.GetName()+'_instances')
    for k,lst in dic.items():
        onull = c4d.BaseObject(c4d.Onull)
        onull.SetName(k)
        onull.InsertUnderLast(res)
        srce = doc.SearchObject(k+'_srce')
        for circle in lst:
            diam = circle[c4d.PRIM_CIRCLE_RADIUS]*2
            inst = c4d.BaseObject(c4d.Oinstance)
            inst.SetMg(c4d.Matrix(circle.GetMg()))
            scale = c4d.Vector(diam/TAILLE_SRCE,diam/TAILLE_SRCE*RATIO,diam/TAILLE_SRCE )
            inst.SetAbsScale(scale)
            rot = c4d.Vector(random()*2*pi,0,0)
            inst.SetAbsRot(rot)
            inst[c4d.INSTANCEOBJECT_LINK] = srce
            inst.InsertUnderLast(onull)
            
    doc.StartUndo()
    doc.InsertObject(res)
    doc.AddUndo(c4d.UNDOTYPE_NEWOBJ,res)
    doc.EndUndo()
    c4d.EventAdd()
        

"""
def state():
    # Defines the state of the command in a menu. Similar to CommandData.GetState.
    return c4d.CMD_ENABLED
"""

if __name__ == '__main__':
    main()