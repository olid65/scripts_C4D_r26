from typing import Optional
import c4d

doc: c4d.documents.BaseDocument  # The active document
op: Optional[c4d.BaseObject]  # The active object, None if unselected

#SELECTIONNER LES OBJETS PARENTS SWISSBUILDINGS_3_0...

def selectContour(op):
    res = False

    nb = c4d.utils.Neighbor()
    nb.Init(op)
    bs = op.GetSelectedEdges(nb,c4d.EDGESELECTIONTYPE_SELECTION)
    bs.DeselectAll()
    for i,poly in enumerate(op.GetAllPolygons()):
        inf = nb.GetPolyInfo(i)
        if nb.GetNeighbor(poly.a, poly.b, i)==-1:
            bs.Select(inf['edge'][0])

        if nb.GetNeighbor(poly.b, poly.c, i)==-1:
            bs.Select(inf['edge'][1])


        #si pas triangle
        if not poly.c == poly.d :
            if nb.GetNeighbor(poly.c, poly.d, i)==-1:
                bs.Select(inf['edge'][2])
                res = True
        if nb.GetNeighbor(poly.d, poly.a, i)==-1:
            bs.Select(inf['edge'][3])
            res = True

    op.SetSelectedEdges(nb,bs,c4d.EDGESELECTIONTYPE_SELECTION)
    return res

def closePolys(op):
    doc.SetMode(c4d.Medges)
    nbr = c4d.utils.Neighbor()
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
            c4d.utils.SendModelingCommand(command = c4d.ID_MODELING_CLOSEHOLE_TOOL, list = [op], mode = c4d.MODELINGCOMMANDMODE_EDGESELECTION, bc = settings, doc = doc)
            nbr.Init(op)
        if nbr.GetNeighbor(vadr.b, vadr.c, i) == c4d.NOTOK:
            settings[c4d.MDATA_CLOSEHOLE_EDGE] = pinf["edge"][1]
            c4d.utils.SendModelingCommand(command = c4d.ID_MODELING_CLOSEHOLE_TOOL, list = [op], mode = c4d.MODELINGCOMMANDMODE_EDGESELECTION, bc = settings, doc = doc)
            nbr.Init(op)
        if vadr.c != vadr.d and nbr.GetNeighbor(vadr.c, vadr.d, i) == c4d.NOTOK:
            settings[c4d.MDATA_CLOSEHOLE_EDGE] = pinf["edge"][2]
            c4d.utils.SendModelingCommand(command = c4d.ID_MODELING_CLOSEHOLE_TOOL, list = [op], mode = c4d.MODELINGCOMMANDMODE_EDGESELECTION, bc = settings, doc = doc)
            nbr.Init(op)
        if nbr.GetNeighbor(vadr.d, vadr.a, i) == c4d.NOTOK:
            settings[c4d.MDATA_CLOSEHOLE_EDGE] = pinf["edge"][3]
            c4d.utils.SendModelingCommand(command = c4d.ID_MODELING_CLOSEHOLE_TOOL, list = [op], mode = c4d.MODELINGCOMMANDMODE_EDGESELECTION, bc = settings, doc = doc)
            nbr.Init(op)


def main() -> None:
    # Called when the plugin is selected by the user. Similar to CommandData.Execute.
    
    
    for op in doc.GetActiveObjects(0):
        #print(parent)

        #OPTIMIZE POINTS
        settings = c4d.BaseContainer()  # Settings
        settings[c4d.MDATA_OPTIMIZE_TOLERANCE] = 0.1
        settings[c4d.MDATA_OPTIMIZE_POINTS] = True
        settings[c4d.MDATA_OPTIMIZE_POLYGONS] = True
        settings[c4d.MDATA_OPTIMIZE_UNUSEDPOINTS] = True
    
    
    
        res = c4d.utils.SendModelingCommand(command=c4d.MCOMMAND_OPTIMIZE,
                                        list=[o for o in op.GetChildren()],
                                        mode=c4d.MODELINGCOMMANDMODE_POLYGONSELECTION,
                                        bc=settings,
                                        doc=doc)
    
        for o in op.GetChildren():
            #on ferme d'abord les polygones'
            closePolys(o)
            #si on a encore des edges contour on met l'objet en rouge
            if selectContour(o):
                o[c4d.ID_BASEOBJECT_USECOLOR] = c4d.ID_BASEOBJECT_USECOLOR_ALWAYS
                o[c4d.ID_BASEOBJECT_COLOR] = c4d.Vector(1,0,0)
                #icone
                o[c4d.ID_BASELIST_ICON_COLORIZE_MODE] =c4d.ID_BASELIST_ICON_COLORIZE_MODE_CUSTOM
                o[c4d.ID_BASELIST_ICON_COLOR]= c4d.Vector(1,0,0)
                #on le met en haut de la hierarchie
                o.InsertUnder(op)
            else:
                o[c4d.ID_BASEOBJECT_USECOLOR] = c4d.ID_BASEOBJECT_USECOLOR_OFF
                o[c4d.ID_BASELIST_ICON_COLORIZE_MODE] =c4d.ID_BASELIST_ICON_COLORIZE_MODE_NONE

    c4d.EventAdd()


"""
def state():
    # Defines the state of the command in a menu. Similar to CommandData.GetState.
    return c4d.CMD_ENABLED
"""

if __name__ == '__main__':
    main()