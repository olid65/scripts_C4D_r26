from typing import Optional
import c4d
import os
import shutil


doc: c4d.documents.BaseDocument  # The active document
op: Optional[c4d.BaseObject]  # The active object, None if unselected

def main() -> None:

    #si le document n'est pas enregistré on enregistre
    path_doc = doc.GetDocumentPath()
    while not path_doc:
        rep = c4d.gui.QuestionDialog(NOT_SAVED_TXT)
        if not rep : return
        c4d.documents.SaveDocument(doc, "", c4d.SAVEDOCUMENTFLAGS_DIALOGSALLOWED, c4d.FORMAT_C4DEXPORT)
        c4d.CallCommand(12098) # Enregistrer le projet
        path_doc = doc.GetDocumentPath()

    dir_tex = os.path.join(path_doc,'tex')
    if not os.path.isdir(dir_tex):
        os.mkdir(dir_tex)


    for mat in doc.GetActiveMaterials():
        #print(mat.GetName())
        shd = mat.GetFirstShader()
        while shd:
            if shd.CheckType(c4d.Xbitmap):
                fn_abs = shd[c4d.BITMAPSHADER_FILENAME]
                fn_rel = os.path.basename(shd[c4d.BITMAPSHADER_FILENAME])
                if fn_abs != fn_rel:
                    #if the file exist
                    if os.path.isfile(fn_abs):
                        #make an image copy in tex
                        dst_abs = os.path.join(dir_tex,fn_rel)
    
                        if not os.path.isfile(dst_abs):
                            shutil.copy(fn_abs,dst_abs)
    
                        shd[c4d.BITMAPSHADER_FILENAME] = fn_rel
            shd = shd.GetNext()


        mat.Message(c4d.MSG_UPDATE)
    c4d.EventAdd()
"""
def state():
    # Defines the state of the command in a menu. Similar to CommandData.GetState.
    return c4d.CMD_ENABLED
"""

if __name__ == '__main__':
    main()