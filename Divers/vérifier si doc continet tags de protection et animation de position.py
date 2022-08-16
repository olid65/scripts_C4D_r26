from typing import Optional
import c4d

doc: c4d.documents.BaseDocument  # The active document
op: Optional[c4d.BaseObject]  # The active object, None if unselected

CONTAINER_ORIGIN = 1026473

def get_all_objects_with_protection_tags(obj,lst = [])->list:
    """retourne une liste avec des objets ayant un tag de protection avec la position activée"""
    while obj:
        #si on a un tag de protection et ....
        tag = obj.GetTag(c4d.Tprotection)
        if tag:
            #...qu'il a au moins une des cases position activée'
            if tag[c4d.PROTECTION_P_X] or tag[c4d.PROTECTION_P_Y] or tag[c4d.PROTECTION_P_Z]:
                # on le rajoute à la liste
                lst.append(obj)
        get_all_objects_with_protection_tags(obj.GetDown(),lst)
        obj = obj.GetNext()
    return lst

def get_all_objects_with_animation(obj,lst_descid,lst = [])->list:
    """retourne une liste avec les objets ayant au moins une des composantes de position animée"""
    while obj:
        for descid in lst_descid:
            if obj.FindCTrack(descid):
                lst.append(obj)
                break
        get_all_objects_with_animation(obj.GetDown(),lst_descid,lst)
        obj = obj.GetNext()
    return lst



def main() -> None:
    print(get_all_objects_with_protection_tags(doc.GetFirstObject(),lst = []))
    
    id_pos_x=c4d.DescID(c4d.DescLevel(c4d.ID_BASEOBJECT_REL_POSITION,c4d.DTYPE_VECTOR,0),c4d.DescLevel(c4d.VECTOR_X,c4d.DTYPE_REAL,0))
    id_pos_y=c4d.DescID(c4d.DescLevel(c4d.ID_BASEOBJECT_REL_POSITION,c4d.DTYPE_VECTOR,0),c4d.DescLevel(c4d.VECTOR_Y,c4d.DTYPE_REAL,0))
    id_pos_z=c4d.DescID(c4d.DescLevel(c4d.ID_BASEOBJECT_REL_POSITION,c4d.DTYPE_VECTOR,0),c4d.DescLevel(c4d.VECTOR_Z,c4d.DTYPE_REAL,0))
    lst_descid = [id_pos_x,id_pos_y,id_pos_z]
    print(get_all_objects_with_animation(doc.GetFirstObject(),lst_descid,lst = []))
"""
def state():
    # Defines the state of the command in a menu. Similar to CommandData.GetState.
    return c4d.CMD_ENABLED
"""

if __name__ == '__main__':
    main()