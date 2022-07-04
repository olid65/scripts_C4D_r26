from typing import Optional
import c4d

doc: c4d.documents.BaseDocument  # The active document
op: Optional[c4d.BaseObject]  # The active object, None if unselected

#BUFFER = 2*37 #si on a un terrain la largeur de la maille ne suffit pas -> 2x

def main() -> None:
    # Called when the plugin is selected by the user. Similar to CommandData.Execute.
    sp = op.GetNext()
    pointobj = op
    
    #calcul de la taille d'une maille, d'après le premier polygone
    poly = pointobj.GetPolygon(0)
    pts = [pointobj.GetPoint(i) for i in [poly.a,poly.b,poly.c,poly.d]]
    x = [p.x for p in pts]
    z = [p.z for p in pts]
    larg_maille = max(x)-min(x)
    haut_maille = max(z)-min(z)

    #sélection des points à l'intérieur de la spline rectangle'
    ml = sp.GetMl()
    rad = sp.GetRad()
    #je prends 2x la largeur de la maille de chaque côté par sécuritéé !
    xmin = -rad.x-larg_maille*2
    xmax =+rad.x +haut_maille*2
    zmin = -rad.z -larg_maille*2
    zmax = rad.z +haut_maille*2

    bs = pointobj.GetPointS()
    bs.DeselectAll()

    for i,p in enumerate(pointobj.GetAllPoints()):
        pt = p*pointobj.GetMg()*~ml
        if pt.x>xmin and pt.x<xmax and pt.z>zmin and pt.z<zmax:
            bs.Select(i)

    #conversion de la sélection en polygone
    settings = c4d.BaseContainer()  # Settings

    settings[c4d.MDATA_CONVERTSELECTION_LEFT] = 0
    settings[c4d.MDATA_CONVERTSELECTION_RIGHT] = 2
    settings[c4d.MDATA_CONVERTSELECTION_TOLERANT] = False

    res = c4d.utils.SendModelingCommand(command=c4d.MCOMMAND_CONVERTSELECTION,
                                    list=[pointobj],
                                    bc=settings,
                                    doc=doc)


    #SPLIT

    res = c4d.utils.SendModelingCommand(command=c4d.MCOMMAND_SPLIT,
                                    list=[pointobj],
                                    mode = c4d.MODELINGCOMMANDMODE_POLYGONSELECTION  ,
                                    doc=doc)
    if res:
        obj = res[0]
        obj.SetName(f'{pointobj.GetName()}_{sp.GetName()}')
        doc.InsertObject(obj)
        
    c4d.EventAdd()

"""
def state():
    # Defines the state of the command in a menu. Similar to CommandData.GetState.
    return c4d.CMD_ENABLED
"""

if __name__ == '__main__':
    main()