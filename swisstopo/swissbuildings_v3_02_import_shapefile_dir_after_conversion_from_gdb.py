import c4d
import shapefile as shp
import os.path
# Welcome to the world of Python


# Script state in the menu or the command palette
# Return True or c4d.CMD_ENABLED to enable, False or 0 to disable
# Alternatively return c4d.CMD_ENABLED|c4d.CMD_VALUE to enable and check/mark
#def state():
#    return True

CONTAINER_ORIGIN = 1026473


def listdirectory2(path):
    fichier=[]
    for root, dirs, files in os.walk(path):
        for i in files:
            #print(i)
            if i == 'Building_solid.shp':
                fichier.append(os.path.join(root, i))
    return fichier

def import_swissbuildings3D_v3_shape(fn,doc):
    res = c4d.BaseObject(c4d.Onull)
    #pour le nom on donne le nom du dossier parent
    res.SetName(os.path.basename(os.path.dirname(fn)))
    r = shp.Reader(fn)

    xmin,ymin,xmax,ymax = r.bbox
    centre = c4d.Vector((xmin+xmax)/2,0,(ymax+ymin)/2)

    origin = doc[CONTAINER_ORIGIN]
    if not origin :
        doc[CONTAINER_ORIGIN] = centre
        origin = centre


    # géométries
    shapes = r.shapes()

    nbre = 0
    for shape in shapes:
        xs = [x for x,y in shape.points]
        zs = [y for x,y in shape.points]
        ys = [z for z in shape.z]
        
        #pour l'axe on prend la moyenne de x et z et le min de y auquel on ajoute 3m
        #car les bati swisstopo rajoute 3m sous le point le plus bas du MNT    
        #comme ça on peut modifier l'échelle des hauteurs  
        axe = c4d.Vector((min(xs)+max(xs))/2,min(ys)+3,(min(zs)+max(zs))/2)
        
        pts = [c4d.Vector(x,z,y)-axe for (x,y),z in zip(shape.points,shape.z)]
        
        nb_pts = len(pts)
        polys = []

        pred = 0
        for i in shape.parts:
            if pred:
                nb_pts_poly = i-pred

            poly = c4d.CPolygon(i,i+1,i+2,i+3)
            polys.append(poly)
            pred = i


        po =c4d.PolygonObject(nb_pts,len(polys))
        #TODO : tag phong !
        po.SetAllPoints(pts)
        for i,poly in enumerate(polys):
            po.SetPolygon(i,poly)

        po.SetAbsPos(axe-origin)
        po.Message(c4d.MSG_UPDATE)
        po.InsertUnderLast(res)
    return res

# Main function
def main():
    path_doc = doc.GetDocumentPath()
    path = os.path.join(path_doc,'swissbuildings3D_v3','shapefiles')
    #path = os.path.join(')
    #path = '/Users/olivierdonze/Documents/TEMP/Trient_test_maquette/download/shapefiles'
    for fn in listdirectory2(path):
        res = import_swissbuildings3D_v3_shape(fn,doc)
        doc.InsertObject(res)
    c4d.EventAdd()
    return



    res = c4d.BaseObject(c4d.Onull)
    #pour le nom on donne le nom du dossier parent
    res.SetName(os.path.basename(os.path.dirname(fn)))
    r = shp.Reader(fn)

    xmin,ymin,xmax,ymax = r.bbox
    centre = c4d.Vector((xmin+xmax)/2,0,(ymax+ymin)/2)

    origin = doc[CONTAINER_ORIGIN]
    if not origin :
        doc[CONTAINER_ORIGIN] = centre
        origin = centre


    # géométries
    shapes = r.shapes()

    nbre = 0
    for shape in shapes:
        pts = [c4d.Vector(x,z,y)-origin for (x,y),z in zip(shape.points,shape.z)]
        nb_pts = len(pts)
        polys = []

        pred = 0
        for i in shape.parts:
            if pred:
                nb_pts_poly = i-pred

            poly = c4d.CPolygon(i,i+1,i+2,i+3)
            polys.append(poly)
            pred = i


        po =c4d.PolygonObject(nb_pts,len(polys))
        #TODO : tag phong !
        po.SetAllPoints(pts)
        for i,poly in enumerate(polys):
            po.SetPolygon(i,poly)

        po.SetAbsPos(c4d.Vector(0))
        po.Message(c4d.MSG_UPDATE)
        po.InsertUnderLast(res)

    doc.InsertObject(res)
    c4d.EventAdd()
    return


# Execute main()
if __name__=='__main__':
    main()