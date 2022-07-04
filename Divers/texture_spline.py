import c4d
from c4d import gui
#Welcome to the world of Python



def textureSpline(obj,spline,clr = c4d.Vector(1,1,1),nom =None):
    
    #calcul position et taille spline
    pos_spline = spline.GetMg().off
    #TODO comment gérer la rotation ?
    centre_spline = spline.GetMp()+pos_spline
    rad_spline = spline.GetRad()
    
    calque = spline[c4d.ID_LAYER_LINK]
    
    #calcul position et taille objet
    pos_obj = obj.GetMg().off
    centre_obj = obj.GetMp()+pos_obj
    rad_obj = obj.GetRad()
    
    
    #création du materiel avec shader spline
    mat = c4d.BaseMaterial(c4d.Mmaterial)
    if calque :
        mat[c4d.ID_LAYER_LINK] = calque.GetUp() #pour le materiau on assigne le calque parent
    if nom : mat.SetName(nom)
    mat[c4d.MATERIAL_COLOR_COLOR] =clr
    mat[c4d.MATERIAL_USE_SPECULAR] = False
    doc.InsertMaterial(mat)
    shd = c4d.BaseList2D(c4d.Xspline)
    shd[c4d.SLA_SPLINE_OBJECT]=spline
    shd[c4d.SLA_SPLINE_TEXT] = False
    shd[c4d.SLA_SPLINE_SINGLE_PIXEL_WIDTH]=True #Epaisseur : 1 pixel
    shd[c4d.SLA_SPLINE_USE_PLANE] = 0 #Plan XZ
    shd[c4d.SLA_SPLINE_FILL] = True #remplissage
    shd[c4d.SLA_SPLINE_FILL_COLOR] = True #Utiliser la couleur de remplissage
    
    #calcul de la position de la texture
    # 0 correspond au coin en haut à gauche de l'obj
    # 100% = coin en bas à droite et donc 50% centre
    larg_obj = rad_obj.x *2
    haut_obj = rad_obj.z *2
    min_obj = centre_obj -rad_obj #coin en haut à gauche
    max_obj = centre_obj +rad_obj #coin en bas à droite
    
    pos = (pos_spline - min_obj)#/(max_obj-min_obj)
    
    shd[c4d.SLA_SPLINE_X_OFFSET] = pos.x/larg_obj
    shd[c4d.SLA_SPLINE_Y_OFFSET] = 1-(pos.z/haut_obj)
    
    
    #calcul de l'échelle de la texture
    shd[c4d.SLA_SPLINE_X_SCALE] = 100/(rad_obj.x*2)
    shd[c4d.SLA_SPLINE_Y_SCALE] = 100/(rad_obj.z*2)
    
    mat[c4d.MATERIAL_USE_ALPHA]=True
    mat[c4d.MATERIAL_ALPHA_SHADER] = shd
    mat.InsertShader(shd)
    mat.Message(c4d.MSG_UPDATE)
    
    shd_remplissage = c4d.BaseList2D(c4d.Xcolor)
    shd_remplissage[c4d.COLORSHADER_COLOR] = c4d.Vector(1)
    mat.InsertShader(shd_remplissage)
    shd[c4d.SLA_SPLINE_FILLET_COLOR]= shd_remplissage
    
    shd_contour = c4d.BaseList2D(c4d.Xcolor)
    shd_contour[c4d.COLORSHADER_COLOR] = c4d.Vector(1)
    mat.InsertShader(shd_contour)
    shd[c4d.SLA_SPLINE_LINE_COLOR] = shd_contour

    
    mat.Update(True, True)
    
    #création du textureTag
    tag = c4d.TextureTag()
    tag[c4d.ID_LAYER_LINK] = calque
    tag.SetMaterial(doc.GetFirstMaterial())
    tag[c4d.TEXTURETAG_PROJECTION] = 6 #projection UVW -> à remplacer par constante
    obj.InsertTag(tag, pred = obj.GetTags()[-1]) #insertion après le dernier tag -> obj.GetTags()[-1]
    c4d.EventAdd()

def main():
    
    sp = op.GetNext()
    textureSpline(op,sp,clr = c4d.Vector(1,0,0),nom = sp.GetName())

if __name__=='__main__':
    main()
