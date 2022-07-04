from typing import Optional
import c4d
import json
import random

doc: c4d.documents.BaseDocument  # The active document
op: Optional[c4d.BaseObject]  # The active object, None if unselected

FACT_ECHELLE = 1

def main() -> None:
    
    srce = doc.SearchObject('source_arbres')
    if srce :
        srce = [child for child in srce.GetChildren()]
    
    
    fn = '/Users/olivierdonze/switchdrive/Mandats/Nuit_de_la_science/Programmation_bac_a_sable/tags.json'
    res = c4d.BaseObject(c4d.Onull)
    res.SetName('arbres')
    with open(fn)as f:
        data = json.loads(f.read())
        for tag in data['tags']:
            inst = c4d.BaseObject(c4d.Oinstance)
            inst[c4d.INSTANCEOBJECT_RENDERINSTANCE_MODE] = c4d.INSTANCEOBJECT_RENDERINSTANCE_MODE_SINGLEINSTANCE
            if srce:
                inst[c4d.INSTANCEOBJECT_LINK] = random.choice(srce)
            pos = c4d.Vector(tag['position']['x']*FACT_ECHELLE,0,tag['position']['y']*FACT_ECHELLE)
            inst.SetAbsPos(pos)
            angle  = c4d.utils.DegToRad(tag['rotation'])
            inst.SetAbsRot(c4d.Vector(angle,0,0))
            inst.SetName(tag['tag_id'])
            inst.InsertUnderLast(res)
    doc.InsertObject(res)
    c4d.EventAdd()


"""
def state():
    # Defines the state of the command in a menu. Similar to CommandData.GetState.
    return c4d.CMD_ENABLED
"""

if __name__ == '__main__':
    main()