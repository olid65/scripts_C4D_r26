from typing import Optional
import c4d

doc: c4d.documents.BaseDocument  # The active document
op: Optional[c4d.BaseObject]  # The active object, None if unselected

"""Sélectionner les deux objets à unir"""

def union_objects(op1,op2, doc, name = None):
    """renvoie l'objet' résultat d'une opération booléenne union"""
    boolobj = c4d.BaseObject(c4d.Oboole)
    boolobj[c4d.BOOLEOBJECT_SINGLE_OBJECT] = True
    
    boolobj[c4d.BOOLEOBJECT_TYPE] = c4d.BOOLEOBJECT_TYPE_UNION
    mg1 = op1.GetMg()
    mg2 = op2.GetMg()
    #clone1 = op1.GetClone()
    #clone2 = op2.GetClone()
    op1.InsertUnder(boolobj)
    op2.InsertUnder(boolobj)
    
    op1.SetMg(mg1)
    op2.SetMg(mg2)
    
    doc.InsertObject(boolobj)
    
    res = c4d.utils.SendModelingCommand(command=c4d.MCOMMAND_MAKEEDITABLE,  
                                    list=[boolobj],
                                    mode=c4d.MODELINGCOMMANDMODE_ALL,   
                                    bc=c4d.BaseContainer(),    
                                    doc=doc)
    
    if res:
        resobj = res[0].GetDown() 
        if name and resobj:
            resobj.SetName(name)
        doc.InsertObject(resobj)
        return resobj
    return None
        
    

def main() -> None:
    #doc.StartUndo()
    op1 = None
    for op2 in op.GetChildren():
        if not op1:
            op1 = op2
            continue
        #doc.AddUndo(c4d.UNDOTYPE_DELETEOBJ, op1)
        #doc.AddUndo(c4d.UNDOTYPE_DELETEOBJ, op2)
        res = union_objects(op1,op2,doc, name = 'union')
        if res:
            #doc.AddUndo(c4d.UNDOTYPE_NEWOBJ, res)
            op1 = res
        else:
            print('pas bien')
            return
    #doc.EndUndo()
    c4d.EventAdd()
    return
    op1,op2 = doc.GetActiveObjects(0)
    boolobj = c4d.BaseObject(c4d.Oboole)
    boolobj[c4d.BOOLEOBJECT_SINGLE_OBJECT] = True
    
    boolobj[c4d.BOOLEOBJECT_TYPE] = c4d.BOOLEOBJECT_TYPE_UNION
    
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
        doc.InsertObject(res[0].GetDown())
    
    c4d.EventAdd()
    

"""
def state():
    # Defines the state of the command in a menu. Similar to CommandData.GetState.
    return c4d.CMD_ENABLED
"""

if __name__ == '__main__':
    main()