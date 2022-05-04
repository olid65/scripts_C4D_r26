from typing import Optional
import c4d
from math import floor
import numpy as np

doc: c4d.documents.BaseDocument  # The active document
op: Optional[c4d.BaseObject]  # The active object, None if unselected


def tuilageMnt(pts,div_x,div_z,nb_pt_x,nb_pt_z):
    lst_tuiles = []
    arr = np.array([p for p in pts])
    newarr = arr.reshape(nb_pt_z,nb_pt_x,)
    nb_pces = div_x * div_z

    nb_pt_x_par_elem = floor((nb_pt_x-1)/div_x+1)
    nb_pt_z_par_elem = floor((nb_pt_z-1)/div_z+1)

    reste_x = nb_pt_x - div_x*(nb_pt_x_par_elem-1) -1
    reste_z = nb_pt_z - div_z*(nb_pt_z_par_elem-1) -1

    #calcul des CPolygon
    id_pt = 0
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

    #extraction des tuiles
    doc.StartUndo()
    id_z = int(reste_z/2)
    id_x = int(reste_x/2)
    id_pce = 1
    for n in range(div_z):
        for i in range(div_x):
            pts=list(newarr[id_z:id_z+nb_pt_z_par_elem,id_x:id_x+nb_pt_x_par_elem].flatten())
            poly = c4d.PolygonObject(len(pts),len(polys))
            poly.SetName(f'tuile_{str(id_pce).zfill(2)}')
            poly.SetAllPoints(pts)
            for id_poly,p in enumerate(polys):
                poly.SetPolygon(id_poly,p)
            poly.InsertUnderLast(op)
            poly.Message(c4d.MSG_UPDATE)
            lst_tuiles.append(poly)

            id_x += nb_pt_x_par_elem-1
            id_pce+=1

        id_x = int(reste_x/2)
        id_z += nb_pt_z_par_elem-1
    return lst_tuiles

def main() -> None:
    zpred = op.GetPoint(0).z
    nb_pt_x = 0
    for p in op.GetAllPoints():
        if p.z == zpred:
            nb_pt_x+=1
        else: break
    nb_pts = op.GetPointCount()
    nb_pt_z = int(nb_pts/nb_pt_x)

    div_x = 7
    div_z = 3


    lst_tuiles = tuilageMnt(op.GetAllPoints(),div_x,div_z,nb_pt_x,nb_pt_z)
    doc.StartUndo()
    for tuile in lst_tuiles:
        tuile.InsertUnderLast(op)
        doc.AddUndo(c4d.UNDOTYPE_NEWOBJ,tuile)

    doc.EndUndo()
    c4d.EventAdd()

    return
    arr = np.array([p for p in op.GetAllPoints()])
    newarr = arr.reshape(nb_pt_z,nb_pt_x,)

    nb_pces = div_x * div_z


    nb_pt_x_par_elem = floor((nb_pt_x-1)/div_x+1)
    nb_pt_z_par_elem = floor((nb_pt_z-1)/div_z+1)

    reste_x = nb_pt_x - div_x*(nb_pt_x_par_elem-1) -1
    reste_z = nb_pt_z - div_z*(nb_pt_z_par_elem-1) -1


    #calcul des CPolygon
    id_pt = 0
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

    #extraction des tuiles
    doc.StartUndo()
    id_z = int(reste_z/2)
    id_x = int(reste_x/2)
    id_pce = 1
    for n in range(div_z):
        for i in range(div_x):
            pts=list(newarr[id_z:id_z+nb_pt_z_par_elem,id_x:id_x+nb_pt_x_par_elem].flatten())
            poly = c4d.PolygonObject(len(pts),len(polys))
            poly.SetName(f'tuile_{str(id_pce).zfill(2)}')
            poly.SetAllPoints(pts)
            for id_poly,p in enumerate(polys):
                poly.SetPolygon(id_poly,p)
            poly.InsertUnderLast(op)
            doc.AddUndo(c4d.UNDOTYPE_NEWOBJ,poly)
            poly.Message(c4d.MSG_UPDATE)
            id_x += nb_pt_x_par_elem-1
            id_pce+=1

        id_x = int(reste_x/2)
        id_z += nb_pt_z_par_elem-1

    doc.EndUndo()

    c4d.EventAdd()
    if reste_x or reste_z:
        c4d.gui.MessageDialog(f"Attention {reste_x} mailles en x et {reste_z} mailles en z nont pas été prises en compte")




"""
def state():
    # Defines the state of the command in a menu. Similar to CommandData.GetState.
    return c4d.CMD_ENABLED
"""

if __name__ == '__main__':
    main()