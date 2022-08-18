from typing import Optional
import c4d
import numpy as np
import os
import shapefile

doc: c4d.documents.BaseDocument  # The active document
op: Optional[c4d.BaseObject]  # The active object, None if unselected

CONTAINER_ORIGIN =1026473

def uv2list(dic):
    return [dic['a'],dic['b'],dic['c'],dic['d']]

def poly2list(poly):
    return[poly.a,poly.b,poly.c,poly.d]

def fichierCalage4points(w,h,pt1,pt2,pt3,pt4,fn):
    #d'après : https://portailsig.org/content/les-transformations-affines-avec-numpy-ou-la-signification-geometrique-d-un-fichier-worldfil.html'
    
    #Nombre de pixels en largeur (m) et en hauteur (n)

    # matrice des pixels:
    fp = np.matrix([[1,w,w,1],[1,1,h,h]])
    # ajout des cordonnées homogènes
    newligne = [1,1,1,1]
    fp  = np.vstack([fp,newligne])
    
    # matrice des coordonnées des 4 angles de l'image'
    tp = np.matrix([[pt1.x,pt2.x,pt3.x,pt4.x],[pt1.z,pt2.z,pt3.z,pt4.z]])

    # solution = fp x inverse(tp)
    M = tp * fp.I

    # paramètres
    A = M[:, 0][0]
    B = M[:, 1][0]
    C = M[:, 2][0]
    D = M[:, 0][1]
    E = M[:, 1][1]
    F = M[:, 2][1]

    # dans l'ordre d'un worldfiles
    lst =  [A,D,B,E,C,F]

    
    
    with open(fn,'w') as f:
        for m in lst:
            f.write(str(m.tolist()[0][0]))
            f.write("\n")
            
def fn_img_from_obj(obj):
    tag = obj.GetTag(c4d.Ttexture)
    if not tag : return None
    
    mat = tag[c4d.TEXTURETAG_MATERIAL]
    if not mat :return None
    
    shd = mat.GetFirstShader()
    while shd:
        if shd.CheckType(c4d.Xbitmap):
            fn = shd[c4d.BITMAPSHADER_FILENAME]
            if fn : return fn 
        shd = shd.GetNext()
    return None

def global_path_from_rel_path(fn, root_pth):
    for root, dirs, files in os.walk(root_pth):
        for f in files:
            if fn==f:
                return os.path.join(root,f)
    return None
    

def main() -> None:

    origin = doc[CONTAINER_ORIGIN]
    if not origin:
        origin = c4d.Vector(0)
        
    docpath = doc.GetDocumentPath()
        
    for o in doc.GetActiveObjects(0):
        
        #EXTRACTION DES 4 ANGLES SELON UVW
        mg = o.GetMg()
        obj = None
        if o.CheckType(c4d.Opolygon):
            obj = o
        if o.CheckType(c4d.Oplane):
            obj = o.GetCache()

        if not obj :
            print(f'{o.GetName} -> pas polygone ou plan')
            continue
        tag = obj.GetTag(c4d.Tuvw)
        if not tag :
            print(f'{o.GetName} -> pas de tag uvw')
            continue
        
        dico = {}
        #on cherche les coins
        a=b=c=d=None
        for i in range(tag.GetDataCount()):            
            for uv,no_pt in zip(uv2list(tag.GetSlow(i)),poly2list(obj.GetPolygon(i))):
                if uv == c4d.Vector(0,0,0):
                    a = obj.GetPoint(no_pt)*mg+origin
                if uv == c4d.Vector(1,0,0):
                    b = obj.GetPoint(no_pt)*mg+origin
                if uv == c4d.Vector(1,1,0):
                    c = obj.GetPoint(no_pt)*mg+origin
                if uv == c4d.Vector(0,1,0):
                    d = obj.GetPoint(no_pt)*mg+origin
        
        #print(a,b,c,d)
        
        #CHEMIN DE L'IMAGE EN MATERIAU (première trouvée si il y en plusieurs)
        fn_img = (fn_img_from_obj(obj))
        if not fn_img : 
            print(f"{o.GetName} -> pas d'image trouvée")
            continue
        
        #si on a un chemin relatif, on cherche l'image dans le dossier du doc
        if not os.path.isabs(fn_img):
            if docpath:
                fn_img = global_path_from_rel_path(fn_img, docpath)
            else:
                print(f'{fn_img} -> document pas enregistré recherche impossible')
                continue
        #dimensions de l'image en pixels
        w,h = None,None
        
        if os.path.isfile(fn_img):
            bmp = c4d.bitmaps.BaseBitmap()
            result, isMovie = bmp.InitWith(fn_img)
            if result == c4d.IMAGERESULT_OK: #int check
                # picture loaded   
                w,h = bmp.GetSize()   
        
        #création du fichier de calage
        fn_calage = fn_img[:-4]+'.wld'
        fichierCalage4points(w,h,a,b,c,d,fn_calage)

"""
def state():
    # Defines the state of the command in a menu. Similar to CommandData.GetState.
    return c4d.CMD_ENABLED
"""

if __name__ == '__main__':
    main()