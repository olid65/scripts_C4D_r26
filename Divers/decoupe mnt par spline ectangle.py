from typing import Optional
import c4d

doc: c4d.documents.BaseDocument  # The active document
op: Optional[c4d.BaseObject]  # The active object, None if unselected


def cut_mnt_by_rectangle(mnt,sp,delta = 200) -> None:
    #altitudes min et max
    alts = [p.y for p in mnt.GetAllPoints()]
    ymin,ymax = min(alts),max(alts)

    #cube from rectangle
    cube = c4d.BaseObject(c4d.Ocube)
    cube[c4d.PRIM_CUBE_LEN,c4d.VECTOR_X] = sp[c4d.PRIM_RECTANGLE_WIDTH]
    cube[c4d.PRIM_CUBE_LEN,c4d.VECTOR_Z] = sp[c4d.PRIM_RECTANGLE_HEIGHT]
    cube[c4d.PRIM_CUBE_LEN,c4d.VECTOR_Y] = ymax-ymin + delta

    mg = c4d.Matrix(sp.GetMg())
    pos = mg.off
    pos.y = (ymin+ymax)/2
    mg.off = pos
    cube.SetMg(mg)

    #intersection boolean
    boolobj = c4d.BaseObject(c4d.Oboole)
    boolobj[c4d.BOOLEOBJECT_HIGHQUALITY] = False
    boolobj[c4d.BOOLEOBJECT_TYPE] = c4d.BOOLEOBJECT_TYPE_INTERSECT
    cube.InsertUnder(boolobj)
    mnt_clone = mnt.GetClone()
    mnt_clone.InsertUnder(boolobj)
    mnt_clone.SetMg(c4d.Matrix(mnt.GetMg()))
    doc.InsertObject(boolobj)

    #
    res = c4d.utils.SendModelingCommand(command=c4d.MCOMMAND_MAKEEDITABLE,
                                    list=[boolobj],
                                    mode=c4d.MODELINGCOMMANDMODE_ALL,
                                    bc=c4d.BaseContainer(),
                                    doc=doc)

    if res:
        #print(res)
        resobj = res[0]
        if resobj:
            resobj.SetName(mnt.GetName())
        doc.InsertObject(resobj)

        mnt_cut = resobj.GetDown()
        if mnt_cut:
            mnt_cut.InsertBefore(resobj)
            resobj.Remove()






def main() -> None:
    mnt = op
    sp = op.GetNext()
    cut_mnt_by_rectangle(mnt,sp)
    c4d.EventAdd()

"""
def state():
    # Defines the state of the command in a menu. Similar to CommandData.GetState.
    return c4d.CMD_ENABLED
"""

if __name__ == '__main__':
    main()