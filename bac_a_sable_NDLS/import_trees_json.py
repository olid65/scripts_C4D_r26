from typing import Optional
import c4d
import json
import random

doc: c4d.documents.BaseDocument  # The active document
op: Optional[c4d.BaseObject]  # The active object, None if unselected

FACT_ECHELLE = 10

NB_PX_X = 588
NB_PX_Z = 432

#ATTENTION vérifier si les valeurs du json partent à zéro ou à 1

def main() -> None:
    
    fn = '/Users/olivierdonze/switchdrive/Mandats/Nuit_de_la_science/Programmation_bac_a_sable/tags.json'
    #pour les arbres sources il faut un objet nommé "source_arbres"
    #avec en enfant un objet nommé avec le numéro de ID qui contient 
    #toutes les variantes de l'arbre en enfant (je ne sais pas si je suis clair là !)
    srce_parent = doc.SearchObject('source_arbres')
    
    srce = {int(child.GetName()):child.GetChildren() for child in srce_parent.GetChildren()}
    

    depthmap = doc.SearchObject('depthmap')
    mg_depthmap = depthmap.GetMg()

    res = c4d.BaseObject(c4d.Onull)
    res.SetName('arbres')
    with open(fn)as f:
        data = json.loads(f.read())
        
    for tag in data['tags']:       
        
        inst = c4d.BaseObject(c4d.Oinstance)
        inst[c4d.INSTANCEOBJECT_RENDERINSTANCE_MODE] = c4d.INSTANCEOBJECT_RENDERINSTANCE_MODE_SINGLEINSTANCE

        inst[c4d.INSTANCEOBJECT_LINK] = random.choice(srce[tag['tag_id']])

        #pos = c4d.Vector(tag['position']['x']*FACT_ECHELLE,0,tag['position']['y']*FACT_ECHELLE)
        
        #ATTENTION j'ai inversé le x et le y parce qu'il que sur les valeurs test
        #il y a des valeurs en y de 440 qui est plus grand que 432 ! (à demander à Alexis)
        #si les valeurs partent de zéro enlever les deux -1

        id_pt = (tag['position']['x'])*NB_PX_X + tag['position']['y']
        pos = c4d.Vector(depthmap.GetPoint(id_pt)* mg_depthmap)

        inst.SetAbsPos(pos)
        inst.SetAbsScale(c4d.Vector(FACT_ECHELLE))
        
        #angle  = c4d.utils.DegToRad(tag['rotation'])
        #inst.SetAbsRot(c4d.Vector(angle,0,0))
        
        #nom avec 
        inst.SetName(tag['tag_id'])
        inst.InsertUnderLast(res)
        
        #look at camera tag insertion
        tag_look = c4d.BaseTag(c4d.Tlookatcamera)
        inst.InsertTag(tag_look)
    doc.InsertObject(res)
    c4d.EventAdd()


"""
def state():
    # Defines the state of the command in a menu. Similar to CommandData.GetState.
    return c4d.CMD_ENABLED
"""

if __name__ == '__main__':
    main()