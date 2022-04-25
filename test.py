from typing import Optional
import c4d
import laspy
import os
CONTAINER_ORIGIN =1026473

def polygonByList(lst_pts,lst_polygon, pos, name = None):
    poly = c4d.PolygonObject(len(lst_pts),len(lst_polygon))
    poly.SetAllPoints(lst_pts)
    poly.SetAbsPos(pos)
    for i,p in enumerate(lst_polygon): poly.SetPolygon(i,p)
    if name : poly.SetName(name)
    poly.Message(c4d.MSG_UPDATE)
    return poly

doc: c4d.documents.BaseDocument  # The active document
op: Optional[c4d.BaseObject]  # The active object, None if unselected

def main() -> None:
    # Called when the plugin is selected by the user. Similar to CommandData.Execute.
    fn = c4d.storage.LoadDialog()
    if not fn : return

    with laspy.open(fn) as f:
        inFile = f.read()
        origine = doc[CONTAINER_ORIGIN]
        origine_obj =  c4d.Vector(inFile.header.min[0],0,inFile.header.min[1])
        nom,ext = os.path.splitext(os.path.basename(fn))
        if not origine:
            doc[CONTAINER_ORIGIN] = origine_obj
            origine = origine_obj

        pts = []

        #pointformat = inFile.point_format
        #for spec in inFile.point_format:
            #print(spec.name)


        for x,y,z,classif in zip(inFile.x,inFile.y,inFile.z,inFile.classification):
            if classif ==5:
                p = c4d.Vector(x,z,y)-origine_obj
                pts.append(p)

        nom = os.path.basename(fn)
        doc.InsertObject(polygonByList(pts,[],origine_obj -doc[CONTAINER_ORIGIN],nom))

    c4d.EventAdd()

"""
def state():
    # Defines the state of the command in a menu. Similar to CommandData.GetState.
    return c4d.CMD_ENABLED
"""

if __name__ == '__main__':
    main()
