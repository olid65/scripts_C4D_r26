from typing import Optional
import c4d
import os
from glob import glob

doc: c4d.documents.BaseDocument  # The active document
op: Optional[c4d.BaseObject]  # The active object, None if unselected

def main() -> None:
    
    pth = '/Volumes/My Passport Pro/PNR_VALLEE_TRIENT_rendus_etudiants/AP2/02.Rendu Final S4/01_projet_PNG'
    
    
    lst = [os.path.basename(fn).split('_')[2] for fn in glob(os.path.join(pth,'*.png'))]
    
    lst = list(set(lst))
    lst2 =  [o.GetName().split('_')[2] for o in op.GetChildren()]
    
    for name in lst:
        if name not in lst2:
            print(name)

"""
def state():
    # Defines the state of the command in a menu. Similar to CommandData.GetState.
    return c4d.CMD_ENABLED
"""

if __name__ == '__main__':
    main()