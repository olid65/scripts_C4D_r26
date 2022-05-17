import c4d
import json
import urllib
from pprint import pprint

# Script state in the menu or the command palette
# Return True or c4d.CMD_ENABLED to enable, False or 0 to disable
# Alternatively return c4d.CMD_ENABLED|c4d.CMD_VALUE to enable and check/mark
#def state():
#    return True

CONTAINER_ORIGIN = 1026473

def empriseVueHaut(bd, origine):
    dimension = bd.GetFrame()
    largeur = dimension["cr"] - dimension["cl"]
    hauteur = dimension["cb"] - dimension["ct"]

    mini = bd.SW(c4d.Vector(0, hauteur, 0)) + origine
    maxi = bd.SW(c4d.Vector(largeur, 0, 0)) + origine

    return mini, maxi, largeur, hauteur

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

    #pprint(suppr_doublons_list_ortho(LST))

    origine = doc[CONTAINER_ORIGIN]
    bd = doc.GetActiveBaseDraw()
    camera = bd.GetSceneCamera(doc)

    if not camera[c4d.CAMERA_PROJECTION] == c4d.Ptop:
        c4d.gui.MessageDialog("Activez une vue de haut")
        return True

    mini, maxi, larg, haut = empriseVueHaut(bd, origine)

    xmin,ymin,xmax,ymax = mini.x,mini.z,maxi.x,maxi.z
    #url = 'swissbuildings3d_3_0_2016_1304-42_2056_5728.gdb.zip'
    url = 'https://data.geo.admin.ch/api/stac/v0.9/collections/ch.swisstopo.swissbuildings3d_3_0'
    lst = get_list_from_STAC_swisstopo(url,xmin,ymin,xmax,ymax)
    pprint(lst)


# Execute main(lst)
if __name__=='__main__':
    main()