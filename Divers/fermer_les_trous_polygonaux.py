from typing import Optional
import c4d

doc: c4d.documents.BaseDocument  # The active document
op: Optional[c4d.BaseObject]  # The active object, None if unselected

#from https://forums.cgsociety.org/t/finding-holes-in-mesh-tools-anyone/1554584/2

from c4d import gui
from c4d import utils


def main():
    doc.SetMode(c4d.Medges)
    nbr = utils.Neighbor()
    nbr.Init(op)
    vcnt = op.GetPolygonCount()
    settings = c4d.BaseContainer()
    settings[c4d.MDATA_CLOSEHOLE_INDEX] = op
    doc.AddUndo(c4d.UNDO_CHANGE,op)

    for i in range(0,vcnt):
        vadr = op.GetPolygon(i)
        pinf = nbr.GetPolyInfo(i)
        if nbr.GetNeighbor(vadr.a, vadr.b, i) == c4d.NOTOK:
            settings[c4d.MDATA_CLOSEHOLE_EDGE] = pinf["edge"][0]
            utils.SendModelingCommand(command = c4d.ID_MODELING_CLOSEHOLE_TOOL, list = [op], mode = c4d.MODELINGCOMMANDMODE_EDGESELECTION, bc = settings, doc = doc)
            nbr.Init(op)
        if nbr.GetNeighbor(vadr.b, vadr.c, i) == c4d.NOTOK:
            settings[c4d.MDATA_CLOSEHOLE_EDGE] = pinf["edge"][1]
            utils.SendModelingCommand(command = c4d.ID_MODELING_CLOSEHOLE_TOOL, list = [op], mode = c4d.MODELINGCOMMANDMODE_EDGESELECTION, bc = settings, doc = doc)
            nbr.Init(op)
        if vadr.c != vadr.d and nbr.GetNeighbor(vadr.c, vadr.d, i) == c4d.NOTOK:
            settings[c4d.MDATA_CLOSEHOLE_EDGE] = pinf["edge"][2]
            utils.SendModelingCommand(command = c4d.ID_MODELING_CLOSEHOLE_TOOL, list = [op], mode = c4d.MODELINGCOMMANDMODE_EDGESELECTION, bc = settings, doc = doc)
            nbr.Init(op)
        if nbr.GetNeighbor(vadr.d, vadr.a, i) == c4d.NOTOK:
            settings[c4d.MDATA_CLOSEHOLE_EDGE] = pinf["edge"][3]
            utils.SendModelingCommand(command = c4d.ID_MODELING_CLOSEHOLE_TOOL, list = [op], mode = c4d.MODELINGCOMMANDMODE_EDGESELECTION, bc = settings, doc = doc)
            nbr.Init(op)

    doc.SetMode(c4d.Mpolygons)
    #select the new polygons
    sel = op.GetPolygonS()
    for i in range(vcnt, op.GetPolygonCount()):
        sel.Select(i)
    c4d.EventAdd()


if __name__=='__main__':
    main()
