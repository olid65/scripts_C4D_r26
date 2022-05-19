import c4d
import json
import urllib
import os
from zipfile import ZipFile
from pprint import pprint
import subprocess

# Script state in the menu or the command palette
# Return True or c4d.CMD_ENABLED to enable, False or 0 to disable
# Alternatively return c4d.CMD_ENABLED|c4d.CMD_VALUE to enable and check/mark
#def state():
#    return True

CONTAINER_ORIGIN = 1026473

TXT_NOT_SAVED = "Le document doit être enregistré pour pouvoir copier les buildings, vous pourrez le faire à la prochaine étape\nVoulez-vous continuer ?"

def empriseObject(obj, origine):
    geom = obj
    if not geom.CheckType(c4d.Opoint):
        geom = geom.GetCache()
        if not geom.CheckType(c4d.Opoint) : return None
    mg = obj.GetMg()
    pts = [p*mg+origine for p in geom.GetAllPoints()]
    lst_x = [p.x for p in pts]
    lst_y = [p.y for p in pts]
    lst_z = [p.z for p in pts]

    xmin = min(lst_x)
    xmax = max(lst_x)
    ymin = min(lst_y)
    ymax = max(lst_y)
    zmin = min(lst_z)
    zmax = max(lst_z)

    mini = c4d.Vector(xmin,ymin,zmin)
    maxi = c4d.Vector(xmax,ymax,zmax)

    return mini, maxi

def empriseVueHaut(bd, origine):
    dimension = bd.GetFrame()
    largeur = dimension["cr"] - dimension["cl"]
    hauteur = dimension["cb"] - dimension["ct"]

    mini = bd.SW(c4d.Vector(0, hauteur, 0)) + origine
    maxi = bd.SW(c4d.Vector(largeur, 0, 0)) + origine

    return mini, maxi

def lv95towgs84(x,y):
    url = f'http://geodesy.geo.admin.ch/reframe/lv95towgs84?easting={x}&northing={y}&format=json'

    f = urllib.request.urlopen(url)
    #TODO : vérifier que cela à bien fonctionnéé (code =200)
    txt = f.read().decode('utf-8')
    json_res = json.loads(txt)

    return float(json_res['easting']),float(json_res['northing'])


def get_list_from_STAC_swisstopo(url,xmin,ymin,xmax,ymax):
    #conversion coordonnées
    est,sud = lv95towgs84(xmin,ymin)
    ouest, nord = lv95towgs84(xmax,ymax)

    sufixe_url = f"/items?bbox={est},{sud},{ouest},{nord}"


    url += sufixe_url
    f = urllib.request.urlopen(url)
    txt = f.read().decode('utf-8')
    json_res = json.loads(txt)

    res = []

    for item in json_res['features']:
        for k,dic in item['assets'].items():
            href = dic['href']
            #on garde que les gdb
            if href[-8:] == '.gdb.zip':
                #dans la version 3 on a soit un url qui se termine par swissbuildings3d_3_0_2021_2056_5728.gdb.zip
                #qui contient la moitié de la suisse
                #ou swissbuildings3d_3_0_2020_1301-31_2056_5728.gdb.zip sous forme de tuile
                #-> donc on ne garde que la dernière qui après un split('_') a une longueur de 7
                if len(dic['href'].split('/')[-1].split('_'))==7:
                    res.append(dic['href'])
    return res

# Main function
def main():
    path_doc = doc.GetDocumentPath()

    while not path_doc:
        rep = c4d.gui.QuestionDialog(TXT_NOT_SAVED)
        if not rep : return True
        c4d.documents.SaveDocument(doc, "", c4d.SAVEDOCUMENTFLAGS_DIALOGSALLOWED, c4d.FORMAT_C4DEXPORT)
        c4d.CallCommand(12098) # Enregistrer le projet
        path_doc = doc.GetDocumentPath()

    pth = os.path.join(path_doc,'swissbuildings3D_v3')
    if not os.path.isdir(pth):
        os.mkdir(pth)

    #dossier principal pour les shapefile
    pth_shapefile = os.path.join(pth,'shapefiles')
    if not os.path.isdir(pth_shapefile):
        os.mkdir(pth_shapefile)

    path_to_ogr2ogr = '/Applications/QGIS.app/Contents/MacOS/bin/ogr2ogr'


    #pprint(suppr_doublons_list_ortho(LST))

    origine = doc[CONTAINER_ORIGIN]


    #Si on a un objet sélectionné qui a une géométrie on l'utilise pour la bbox'
    if op and op.CheckType(c4d.Opoint):
        mini,maxi = empriseObject(op, origine)

    #sinon on prend la vue de haut
    else :
        bd = doc.GetActiveBaseDraw()
        camera = bd.GetSceneCamera(doc)

        if not camera[c4d.CAMERA_PROJECTION] == c4d.Ptop:
            c4d.gui.MessageDialog("Activez une vue de haut")
            return True
        mini, maxi = empriseVueHaut(bd, origine)

    xmin,ymin,xmax,ymax = mini.x,mini.z,maxi.x,maxi.z
    #url = 'swissbuildings3d_3_0_2016_1304-42_2056_5728.gdb.zip'
    url_base = 'https://data.geo.admin.ch/api/stac/v0.9/collections/ch.swisstopo.swissbuildings3d_3_0'
    lst = get_list_from_STAC_swisstopo(url_base,xmin,ymin,xmax,ymax)
    #pprint(lst)

    #TELECHARGEMENT
    for url in lst:
        name = url.split('/')[-1]
        fn_dst = os.path.join(pth,name)
        
        #on télécharge uniquement si le dossier gdb n'existe pas
        #pour le nom du gdb c'est un peu complexe
        #le fichier zippé s'appelle : swissbuildings3d_3_0_2020_1301-11_2056_5728.gdb.zip
        #et le dossier .gdb dézippé : swissBUILDINGS3D_3-0_1301-11.gdb
        #c'est un peu bricolé mais ça marche !
        pref = 'swissBUILDINGS3D_3-0_'
        suf = '.gdb'
        name_gdb = pref + name[len(pref)+5:-18] +suf
        fn_gdb = os.path.join(pth,name_gdb)

        if not os.path.isdir(fn_gdb):
            x = urllib.request.urlopen(url)
            with open(fn_dst,'wb') as saveFile:
                saveFile.write(x.read())

            #DEZIPPAGE
            with ZipFile(fn_dst, 'r') as zipObj:
                # Extract all the contents of zip file in current directory
                zipObj.extractall(pth)

            #suppression du zip
            os.remove(fn_dst)

    #conversion GDB->SHP
    for f in os.scandir(pth):
        if f.is_dir() and f.path[-4:]=='.gdb':
            fn_gdb = f.path
            dir_shp = os.path.join(pth_shapefile,os.path.basename(fn_gdb[:-4]))
            #on convertit uniquement si le dossier n'existe pas
            if not os.path.isdir(dir_shp):
                os.mkdir(dir_shp)
                req = f'"{path_to_ogr2ogr}" "{dir_shp}" "{fn_gdb}"'
                #print(req)
                output = subprocess.check_output(req,shell=True)

    print('ok')


# Execute main(lst)
if __name__=='__main__':
    main()