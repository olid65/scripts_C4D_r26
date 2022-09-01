from typing import Optional
import c4d
import os
import subprocess
from glob import glob


"""Transforme une série d'images jpg ou png en fichier GIF animé dans le même dossier
   Il faut sélectionner le dossier contenant les images"""

DELAY = 10 # Durée d'animation par image en 1/100e de seconde
LOOP = 0 #nombre de boucle (0=>infini)

doc: c4d.documents.BaseDocument  # The active document
op: Optional[c4d.BaseObject]  # The active object, None if unselected

def main() -> None:
    
    exts = ['.jpg','.png']
    
    pth = '/Users/olivierdonze/Documents/TEMP/test_gif_imagemagik'
    pth = c4d.storage.LoadDialog(flags= c4d.FILESELECT_DIRECTORY)
    if not pth : return
    
    ext = None
    name = None
    for e in exts:
        lst = sorted(glob(os.path.join(pth,'*'+e)))
        if lst:
            ext = e
            #pour le nom on prend le nom du premier fichier trouvé
            name = os.path.basename(lst[0][:-4])
            #on enlève tous les chiffres à la fin
            while name[-1].isdigit():
                name = name[:-1]
            fn_dst = os.path.join(pth, name+'.gif')
            break
    if not ext or not name :
        return
    
    if os.path.isfile(fn_dst):
        rep = c4d.gui.QuestionDialog(f"Le fichier {fn_dst} existe déjà, il va être remplacé. Voulez-vous continuer ?")
        if not rep :
            return
    fn_src = os.path.join(pth,f'*{ext}')
    
    cmd = f'/usr/local/bin/convert -delay {DELAY} -loop {LOOP} {fn_src} {fn_dst}'
    print(cmd)
    out = subprocess.run(cmd, shell=True)
    print(out)
"""
def state():
    # Defines the state of the command in a menu. Similar to CommandData.GetState.
    return c4d.CMD_ENABLED
"""

if __name__ == '__main__':
    main()