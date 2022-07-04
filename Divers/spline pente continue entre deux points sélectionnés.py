import c4d
from c4d import gui
#Welcome to the world of Python


def main():
    bs = op.GetPointS()
    if bs.GetCount() != 2:
        c4d.gui.MessageDialog("Vous devez sélectionner deux points de références sur la spline")
        return
    calcul_lg = False
    lg_tot = 0
    pred = None
    alts = []
    for i,p in enumerate(op.GetAllPoints()):
        p1 = c4d.Vector(p.x,0,p.z)
        if calcul_lg:
            lg_tot+= (p1-pred).GetLength()
            
        if bs.IsSelected(i):
            calcul_lg = not calcul_lg
            alts.append(p.y)
        pred = p1
    alt =  alts[1] -alts[0]

    modify = False
    lg= 0
    pred = None
    
    doc.StartUndo()
    for i,p in enumerate(op.GetAllPoints()):
        p1 = c4d.Vector(p.x,0,p.z)
        if modify :
            if bs.IsSelected(i) :break
            lg += (p1-pred).GetLength()
            
            p.y = alts[0] + alt*lg/lg_tot
            doc.AddUndo(c4d.UNDOTYPE_CHANGE,op)
            op.SetPoint(i,p)
            
        if bs.IsSelected(i):
            modify = not modify
            
        pred = p1
        
    op.Message(c4d.MSG_UPDATE)    
    doc.EndUndo()
    c4d.EventAdd()    
    
if __name__=='__main__':
    main()
