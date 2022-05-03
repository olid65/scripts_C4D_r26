from typing import Optional
import c4d
import rasterio

doc: c4d.documents.BaseDocument  # The active document
op: Optional[c4d.BaseObject]  # The active object, None if unselected


NBRE_TUILE_X = 5
NBRE_TUILE_Z = 2


def polygonizeMNT(rasterio_object):

    return

def main() -> None:
    # Called when the plugin is selected by the user. Similar to CommandData.Execute.
    fn = '/Users/olivierdonze/Downloads/exportImage(5).tiff'

    with rasterio.open(fn) as mnt:
        print(mnt.width, mnt.height)
        
        taille_tuile = int(mnt.width/NBRE_TUILE_X),int(mnt.height/NBRE_TUILE_Z)
        print(taille_tuile)


        data = mnt.read()
        #print(data)


"""
def state():
    # Defines the state of the command in a menu. Similar to CommandData.GetState.
    return c4d.CMD_ENABLED
"""

if __name__ == '__main__':
    main()