from typing import Optional
import c4d

doc: c4d.documents.BaseDocument  # The active document
op: Optional[c4d.BaseObject]  # The active object, None if unselected

#ID pour stocker l'échelle du MNT si on veut pouvoir la changer après
ID_BUILDING_SCALE = 1059451

SCALE_MNT = 2.5
SCALE_BUILDINGS = 1.25

def main() -> None:
    # Called when the plugin is selected by the user. Similar to CommandData.Execute.
    for o in op.GetChildren():

        pos = o.GetAbsPos()
        #si l'objet avait déjà une échelle on remet sa pos.y à l'échelle 1
        if o[ID_BUILDING_SCALE]:
            pos.y/= o[ID_BUILDING_SCALE]

        pos.y *= SCALE_MNT
        o.SetAbsPos(pos)
        o[ID_BUILDING_SCALE] = SCALE_MNT


        scale = o.GetAbsScale()
        scale.y = SCALE_BUILDINGS
        o.SetAbsScale(scale)
    c4d.EventAdd()

"""
def state():
    # Defines the state of the command in a menu. Similar to CommandData.GetState.
    return c4d.CMD_ENABLED
"""

if __name__ == '__main__':
    main()