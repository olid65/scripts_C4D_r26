import c4d
import os
import json


"""exporte pour chaque objet qui possède un BaseContainer[ID_OD_CALIBRATOR]
   un fichier json contenant le chemin de l'image les points 2D (sur l'image) et
   les points 3D (x et z interverti !!!!) de la scène (nulls en enfant) 
   et la taille de l'image (img_size)"""



ID_OD_CALIBRATOR = 1059348



def main():
    obj = doc.GetFirstObject()
    n = 0
    while obj:
        if obj[ID_OD_CALIBRATOR]:
            bc = obj[ID_OD_CALIBRATOR]
            fn_img = bc[0]
            #print(fn_img)
            pts_uv = [(v.x,v.y) for i,v in bc[1]]
            #print(pts_uv)
            #ATTENTION j'inverse le y et le z'
            t = lambda v : (v.x,v.z,v.y)
            pts_3D = [t(o.GetMg().off) for o in obj.GetChildren()]
            print(pts_3D)
            
            img_size = bc[2][0],bc[2][1]

            if len(pts_uv) != len(pts_3D):
                print("pas le même nombre de points")
                return
            else:
                dico = {'fn_img' : fn_img,
                        'pts_uv' : pts_uv,
                        'pts_3D' : pts_3D,
                        'img_size': img_size
                        }
                fn_json = fn_img[:-4]+'_calibrage.json'
                if os.path.isfile(fn_json):
                    if not c4d.gui.QuestionDialog(f'Le fichier {fn_json} existe déjà voulez vous continuer ?'):
                        break
                with open(fn_json,'w') as f:
                    f.write(json.dumps(dico,indent = 4))
                #print(fn_json)
            n+=1
        obj = obj.GetNext()

    c4d.gui.MessageDialog(f'{n} objets trouvés')


if __name__ == "__main__":
    main()