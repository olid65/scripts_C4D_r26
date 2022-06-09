from typing import Optional
import c4d

doc: c4d.documents.BaseDocument  # The active document
op: Optional[c4d.BaseObject]  # The active object, None if unselected

"""Sélectionner les deux objets à unir"""

def intersection_objects(op1,op2, doc, name = None):
    """renvoie l'objet' résultat d'une opération booléenne union"""
    boolobj = c4d.BaseObject(c4d.Oboole)
    boolobj[c4d.BOOLEOBJECT_SINGLE_OBJECT] = True

    boolobj[c4d.BOOLEOBJECT_TYPE] = c4d.BOOLEOBJECT_TYPE_INTERSECT

    clone1 = op1.GetClone()
    clone2 = op2.GetClone()
    clone1.InsertUnder(boolobj)
    clone2.InsertUnder(boolobj)

    clone1.SetMg(c4d.Matrix(op1.GetMg()))
    clone2.SetMg(c4d.Matrix(op2.GetMg()))

    doc.InsertObject(boolobj)

    res = c4d.utils.SendModelingCommand(command=c4d.MCOMMAND_MAKEEDITABLE,
                                    list=[boolobj],
                                    mode=c4d.MODELINGCOMMANDMODE_ALL,
                                    bc=c4d.BaseContainer(),
                                    doc=doc)

    if res:
        obj = res[0]
        if name : obj.SetName(name)
        return obj
    return None



def main() -> None:
    
    op1,op2 = doc.GetActiveObjects(0)
    
    res = intersection_objects(op1,op2, doc, name = 'Prout')
    if res :
        doc.InsertObject(res)
        c4d.EventAdd()
    return    
    
    boolobj = c4d.BaseObject(c4d.Oboole)
    boolobj[c4d.BOOLEOBJECT_SINGLE_OBJECT] = True

    boolobj[c4d.BOOLEOBJECT_TYPE] = c4d.BOOLEOBJECT_TYPE_INTERSECT

    clone1 = op1.GetClone()
    clone2 = op2.GetClone()
    clone1.InsertUnder(boolobj)
    clone2.InsertUnder(boolobj)

    clone1.SetMg(c4d.Matrix(op1.GetMg()))
    clone2.SetMg(c4d.Matrix(op2.GetMg()))

    doc.InsertObject(boolobj)

    res = c4d.utils.SendModelingCommand(command=c4d.MCOMMAND_MAKEEDITABLE,
                                    list=[boolobj],
                                    mode=c4d.MODELINGCOMMANDMODE_ALL,
                                    bc=c4d.BaseContainer(),
                                    doc=doc)

    if res:
        doc.InsertObject(res[0])

    c4d.EventAdd()


"""
def state():
    # Defines the state of the command in a menu. Similar to CommandData.GetState.
    return c4d.CMD_ENABLED
"""

if __name__ == '__main__':
    main()