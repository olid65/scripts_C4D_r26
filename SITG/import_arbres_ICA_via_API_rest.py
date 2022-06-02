from typing import Optional
import c4d
import urllib.request
import urllib.parse
import json
from pprint import pprint

doc: c4d.documents.BaseDocument # The active document
op: Optional[c4d.BaseObject] # The active object, None if unselected

CONTAINER_ORIGIN = 1026473

class ICA_tree(object):

    def __init__(self,data, origin = c4d.Vector(0)):
        self.dic = data
        x,y = data['geometry']['coordinates']
        self.pos = c4d.Vector(x,0,y)-origin
        self.name = data['properties']['NOM_COMPLET']
        self.classe = data['properties']['CLASSE']
        self.diam = data['properties']['DIAMETRE_COURONNE']
        self.haut = data['properties']['HAUTEUR_TOTALE']
        """
        exemple data si besoin plus paramètres
        {   'geometry': {'coordinates': [2500302.09, 1119227.6400000006], 'type': 'Point'},
            'id': 147937,
            'properties': {'CIRCONFERENCE_1M': 72,
                        'CLASSE': 'Dicotylédone',
                        'CONDUITE': 'Semi-libre',
                        'DATE_OBSERVATION': 1336003200000,
                        'DATE_PLANTATION': 1009843200000,
                        'DATE_PLANTATION_ESTIMEE': 1,
                        'DIAMETRE_1M': 23,
                        'DIAMETRE_COURONNE': 6,
                        'ESPERANCE_VIE': 2100,
                        'FORME': 'Tige',
                        'HAUTEUR_TOTALE': 7,
                        'HAUTEUR_TRONC': 3,
                        'ID_ACTEUR': 'HENCHOZ',
                        'ID_ARBRE': 222574,
                        'NOMBRE_TRONCS': '1',
                        'NOM_COMPLET': 'Acer campestre',
                        'NO_INVENTAIRE': 'SEVE_222574',
                        'OBJECTID': 147937,
                        'RAYON_COURONNE': 3,
                        'REMARQUABLE': None,
                        'SITUATION': 'Parking',
                        'SOUCHE': 'Non',
                        'STADE_DEVELOPPEMENT': 'Adulte',
                        'STATUT': 'Relevé',
                        'TYPE_PLANTATION': 'Alignement',
                        'TYPE_SOL': 'Mélange standard',
                        'TYPE_SURFACE': 'Plante tapissante/Arbustes',
                        'VITALITE': 'Bon'},
            'type': 'Feature'}
        """



    def __repr__(self):
        return self.name


def importICA(xmin,ymin,xmax,ymax, origin = c4d.Vector(0)):
    server = 'SITG_OPENDATA_04'
    id_lyr = '4571'
    url_base = f'https://ge.ch/sitgags1/rest/services/VECTOR/{server}/MapServer/{id_lyr}/query?'
    params = {
        "inSR" :'2056',
        "outSR" :'2056',
        "geometry": f"{xmin},{ymin},{xmax},{ymax}",
        "geometryType":"esriGeometryEnvelope",
        "returnGeometry": "true",
        "returnZ":"true",
        "outfields": "*",
        "f": "geojson"
    }

    query_string = urllib.parse.urlencode( params )
    url = url_base+query_string

    req = urllib.request.Request(url=url)
    resp = urllib.request.urlopen(req)
    data = json.loads(resp.read().decode("utf-8"))
    #pprint(data['features'])
    arbres = [ICA_tree(feat,origin) for feat in data['features']]
    #on retourne seulement ceux qui ont des attributs (ici diamètre)
    #les arbres historiques n'ont pas les infos
    return [arbre for arbre in arbres if arbre.diam]



def main() -> None:
    origin = doc[CONTAINER_ORIGIN]
    xmin,ymin,xmax,ymax = 2501637.2622879897,1126351.1442178185,2501987.2622879897,1126701.1442178185
    arbres = importICA(xmin,ymin,xmax,ymax,origin)

    res = c4d.BaseObject(c4d.Onull)
    res.SetName('arbres_ICA')

    coniferes = c4d.BaseObject(c4d.Onull)
    coniferes.SetName('gymnosperme')
    coniferes.InsertUnder(res)

    feuillus = c4d.BaseObject(c4d.Onull)
    feuillus.SetName('dicotyledone')
    feuillus.InsertUnder(res)

    for arbre in arbres:
        inst = c4d.BaseObject(c4d.Oinstance)
        inst.SetName(arbre.name)
        inst.SetAbsPos(arbre.pos)

        scale = c4d.Vector(arbre.diam/10,arbre.haut/10,arbre.diam/10)
        inst.SetAbsScale(scale)
        if arbre.classe == 'Gymnosperme':
            inst.InsertUnderLast(coniferes)
        else:
            inst.InsertUnderLast(feuillus)

    doc.InsertObject(res)







if __name__ == '__main__':
    main()
    c4d.EventAdd()