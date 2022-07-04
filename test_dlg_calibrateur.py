#coding: utf-8


from re import I
import c4d, os
#import calibrator_utils.bmp

TAILLE_MIN = 1 # nombre de pixels min pour l'extraction'

DIC_EXT =  { '.tif':c4d.FILTER_TIF,
             '.tga':c4d.FILTER_TGA,
             '.jpg':c4d.FILTER_JPG,
             '.psd':c4d.FILTER_PSD,
             '.psb':c4d.FILTER_PSB,
             '.png':c4d.FILTER_PNG,}



##################################################################################################
#GEUSERAREA
##################################################################################################

class BmpUserArea(c4d.gui.GeUserArea):
    """ Initialisation en deux temps d'abord __init__ puis initBMP """


    TAILLE_CROIX = 10
    RAYON_ACCROCHE = 10 
    VITESSE_ZOOM = 1.1
    SPEED_TRANSLATE = 5
    COLOR_POINTS = c4d.Vector(1,0,1)

    MSG_NOT_RGB = """Attention l'image n'est pas en RVB ou RVBA l'extraction ne fonctionnera pas !
Convertissez l'image avant ! (limitation du SDK de Cinema4D)"""

    def __init__(self, dlg_parent):
        self.dlg_parent = dlg_parent
        self.centre_zoom = None
        #self.bbox = Bbox()
        self.points = []
        self.bmp = None
        self.width, self.height = 0,0

    def initBMP(self, fn_img):
        self.fn_img = fn_img
        self.bmp = c4d.bitmaps.BaseBitmap()
        result, isMovie = self.bmp.InitWith(self.fn_img)
        if result != c4d.IMAGERESULT_OK:
            self.bmp = None
            self.width, self.height = 0,0
            return False

        #si l'image n'est pas en  rvb ou rvba (24 ou 32 bits)
        # le crop ne fonctionnera pas
        # on met simplement en garde !
        color_mode = self.bmp.GetColorMode()
        if color_mode != c4d.COLORMODE_RGB and  color_mode != c4d.COLORMODE_ARGB:
            c4d.gui.MessageDialog(self.MSG_NOT_RGB)

        self.width, self.height = self.bmp.GetSize()
        #self.bbox = Bbox()
        self.LayoutChanged()
        self.dlg_parent.LayoutChanged(self.dlg_parent.ID_SCROLLGRP_BMP)
        return True

    def GetSize(self):
        return self.GetWidth(),self.GetHeight()

    def GetMinSize(self):
        return self.width, self.height

    def DrawMsg(self, x1, y1, x2, y2, msg):

        #self.OffScreenOn()

        #ATTENTION il faut bien mettre la taille de l'image
        #pas self.width, self.height qui après zoom ne correspond plus !

        self.DrawBitmap(self.bmp,
                            0, 0, x2, y2,
                            0, 0, self.bmp.GetBw(), self.bmp.GetBh(),
                            c4d.BMP_NORMAL | c4d.BMP_ALLOWALPHA)
        self.DrawSetPen(self.COLOR_POINTS)
        self.drawPoints()
        #w,l = self.bbox.getSize()
        #if w and l:
            #RECTANGLE
            #xmin,xmax,ymin,ymax = self.bbox.getBox()
            
            #xmin,xmax,ymin,ymax = self.image2local(xmin,xmax,ymin,ymax)
            #self.drawBox(xmin,xmax,ymin,ymax)

    def drawPoints(self):
        for i,(x,y) in enumerate(self.points):
            x,y = self.image2local_pt(x,y)
            #self.DrawRectangle(x-self.TAILLE_CROIX, y-self.TAILLE_CROIX, x+self.TAILLE_CROIX, y+self.TAILLE_CROIX)
            self.DrawLine(x-self.TAILLE_CROIX, y, x+self.TAILLE_CROIX, y)
            self.DrawLine(x,y-self.TAILLE_CROIX, x, y+self.TAILLE_CROIX)
            self.DrawSetFont(c4d.FONT_BOLD)
            self.DrawSetTextCol(self.COLOR_POINTS, c4d.Vector(0)) #fond transparent => c4d.COLOR_TRANS
            x_txt = x+self.TAILLE_CROIX
            y_txt = y - 2*self.TAILLE_CROIX
            self.DrawText(f'{i+1}',x+self.TAILLE_CROIX,y - 2*self.TAILLE_CROIX)

    def Message(self, msg, result):
        # Catch the draw message to cancel it (return True)
        # and call ourself the DrawMsg with the dimension we expect
        if msg.GetId() == c4d.BFM_DRAW:
            self.DrawMsg(0, 0, self.width, self.height, c4d.BaseContainer())
            return True

        return c4d.gui.GeUserArea.Message(self, msg, result)

    def local2image_pt(self,mx,my):
        """ pour adapter la bbox du mode local à la taille de l'image """
        w_img,h_img = self.bmp.GetSize()
        itemDim = self.dlg_parent.GetItemDim(self.dlg_parent.ID_USER_AREA)
        mx = int(round(float(mx)/itemDim['w']*w_img))
        my = int(round(float(my)/itemDim['h']*h_img))

        mx = c4d.utils.Clamp(0, w_img, mx)
        my = c4d.utils.Clamp(0, h_img, my)
        return mx,my

    def image2local_pt(self,mx,my):
        """ pour adapter la bbox à la taille de l'image au mode local"""
        w_img,h_img = self.bmp.GetSize()
        itemDim = self.dlg_parent.GetItemDim(self.dlg_parent.ID_USER_AREA)

        mx = int(round(float(mx)/w_img*itemDim['w']))
        my = int(round(float(my)/h_img*itemDim['h']))
        return mx,my

    def image2local(self,mx1,mx2,my1,my2):
        """ pour adapter la bbox à la taille de l'image au mode local"""
        w_img,h_img = self.bmp.GetSize()
        itemDim = self.dlg_parent.GetItemDim(self.dlg_parent.ID_USER_AREA)

        mx1 = int(round(float(mx1)/w_img*itemDim['w']))
        mx2 = int(round(float(mx2)/w_img*itemDim['w']))
        my1 = int(round(float(my1)/h_img*itemDim['h']))
        my2 = int(round(float(my2)/h_img*itemDim['h']))
        return mx1,mx2,my1,my2

    def InputEvent(self, msg) :
        """par defaut si on n'override pas cette méthode
           il y a un pan par défaut !
           Si on veut conserver il faut à la fin renvoyer return c4d.gui.GeUserArea.InputEvent(self,msg)
           Si on veut courcicuiter un paramètre on renvoie True (ici molette de souris)"""
        key = msg.GetLong(c4d.BFM_INPUT_CHANNEL)

        #TOUCHE ENTER on crop l'image
        if key==c4d.KEY_ENTER:
            #self.cropImage()
            return True

        #TOUCHE DELETE on efface la bbox ATTENTION ça efface dans la scène aussi !
        if key == c4d.KEY_DELETE:
            return True

        #TOUCHES DE DEPLACEMENT
        if key == c4d.KEY_UP:
            #self.bbox.translate(0,-self.SPEED_TRANSLATE)
            self.LayoutChanged()
            self.dlg_parent.LayoutChanged(self.dlg_parent.ID_SCROLLGRP_BMP)
            return True
        if key == c4d.KEY_DOWN:
            #self.bbox.translate(0,self.SPEED_TRANSLATE)
            self.LayoutChanged()
            self.dlg_parent.LayoutChanged(self.dlg_parent.ID_SCROLLGRP_BMP)
            return True
        if key == c4d.KEY_LEFT:
            #self.bbox.translate(-self.SPEED_TRANSLATE,0)
            self.LayoutChanged()
            self.dlg_parent.LayoutChanged(self.dlg_parent.ID_SCROLLGRP_BMP)
            return True
        if key == c4d.KEY_RIGHT:
            #self.bbox.translate(self.SPEED_TRANSLATE,0)
            self.LayoutChanged()
            self.dlg_parent.LayoutChanged(self.dlg_parent.ID_SCROLLGRP_BMP)
            return True

        #SOURIS SOURIS SOURIS
        if msg[c4d.BFM_INPUT_DEVICE] == c4d.BFM_INPUT_MOUSE:
            chn = msg.GetLong(c4d.BFM_INPUT_CHANNEL)
            mx = msg.GetLong(c4d.BFM_INPUT_X)
            my = msg.GetLong(c4d.BFM_INPUT_Y)
            mx1 = mx - self.Local2Global()['x']
            my1 = my - self.Local2Global()['y']

            #on regarde si on survole un point
            mx_img,my_img = self.local2image_pt(mx1,my1)
            pt_mouse = c4d.Vector(mx_img,my_img,0)
            id_pt = c4d.NOTOK
            for i,(x,y) in enumerate(self.points):
                if (c4d.Vector(x,y,0)-pt_mouse).GetLength()< self.RAYON_ACCROCHE:
                    id_pt = i
                    print(id_pt)
                    break

            #IMAGE CROP IMAGE CROP IMAGE CROP
            if msg[c4d.BFM_INPUT_DOUBLECLICK]:
                pass
                #self.cropImage()

            #ZOOM AVEC MOLETTE
            if chn == c4d.BFM_INPUT_MOUSEWHEEL:

                    inp = msg.GetLong(c4d.BFM_INPUT_VALUE)
                    echelle = self.VITESSE_ZOOM
                    if inp<0 :
                        echelle = 1./self.VITESSE_ZOOM

                    self.zoom_selon_point(mx,my,echelle)
                    return True

            

            #BOUTON GAUCHE
            if chn == c4d.BFM_INPUT_MOUSELEFT:

                #SUPPRESSION DE POINT si on appuie sur CTRL/CMD et qu'on survole un point
                if id_pt!= c4d.NOTOK and msg[c4d.BFM_INPUT_QUALIFIER] & c4d.QCTRL:
                    del self.points[id_pt]
                    self.LayoutChanged()
                    self.dlg_parent.LayoutChanged(self.dlg_parent.ID_SCROLLGRP_BMP)
                    #print(f'effacer n°{id_pt}')
                    id_pt= c4d.NOTOK 


                #MODIFICATION D'UN POINT si on le survole
                if id_pt!= c4d.NOTOK :
                    c4d.gui.SetMousePointer(c4d.MOUSE_HIDE)
                    while self.GetInputState(c4d.BFM_INPUT_MOUSE, c4d.BFM_INPUT_MOUSELEFT, msg) and msg.GetLong(c4d.BFM_INPUT_VALUE):
                        mx = msg.GetLong(c4d.BFM_INPUT_X)
                        my = msg.GetLong(c4d.BFM_INPUT_Y)
                        mx2 = mx - self.Local2Global()['x']
                        my2 = my - self.Local2Global()['y']
                        self.points[id_pt] = self.local2image_pt(mx2,my2)
                        self.LayoutChanged()
                        self.dlg_parent.LayoutChanged(self.dlg_parent.ID_SCROLLGRP_BMP)


                #is_in_corner = self.bbox.isInCorner(mx_img,my_img, self.TAILLE_CROIX+self.RAYON_ACCROCHE_POIGNEES)
                #is_on_perimetre = self.bbox.isOnPerimeter(mx_img,my_img,self.TAILLE_CROIX+self.RAYON_ACCROCHE_POIGNEES)

                # AJOUT DE POINT si on appuie sur SHIFT
                if msg[c4d.BFM_INPUT_QUALIFIER] & c4d.QSHIFT:
                    mx1 = mx - self.Local2Global()['x']
                    my1 = my - self.Local2Global()['y']
                    id_pt_new = len(self.points)
                    self.points.append(self.local2image_pt(mx1,my1))
                    
                    c4d.gui.SetMousePointer(c4d.MOUSE_HIDE)
                    while self.GetInputState(c4d.BFM_INPUT_MOUSE, c4d.BFM_INPUT_MOUSELEFT, msg) and msg.GetLong(c4d.BFM_INPUT_VALUE):

                        mx = msg.GetLong(c4d.BFM_INPUT_X)
                        my = msg.GetLong(c4d.BFM_INPUT_Y)
                        mx2 = mx - self.Local2Global()['x']
                        my2 = my - self.Local2Global()['y']
                        self.points[id_pt_new] = self.local2image_pt(mx2,my2)
                        self.LayoutChanged()
                        self.dlg_parent.LayoutChanged(self.dlg_parent.ID_SCROLLGRP_BMP)

                c4d.gui.SetMousePointer(c4d.MOUSE_SHOW)

        return c4d.gui.GeUserArea.InputEvent(self,msg)


    def zoom_selon_point(self,mx,my,echelle):
        #mx et my sont les valeurs de position du point axe
        #en valeur écran
        #échelle le facteur d'échelle (1.1 pour agrndir 10%)

        self.width  *= echelle
        self.height *= echelle

        #calcul de la nouvelle définition d'image
        #attention cette valeur n'est pas la définition de self.bmp
        #qui conserve sa taille d'origine'
        self.width = int(round(self.width))
        self.height = int(round(self.height))

        #on récupère les ancienne valeurs avant le chagement d'échelle pour
        #le calcul du zoom pas depuis l'angle en haut à gauche
        old_item_dim =  self.dlg_parent.GetItemDim(self.dlg_parent.ID_USER_AREA)


        #ancienne position de la souris sur l'image en proportion depuis le coin en haut à gauche
        old_pos_img_sur_largeur = (mx-old_item_dim['x'])/float(old_item_dim['w'])
        old_pos_img_sur_hauteur = (my-old_item_dim['y'])/float(old_item_dim['h'])

        #on envoie le changement d'échelle pour que cela redessine
        #aussi au niveau du dialogue parent
        self.LayoutChanged()
        self.dlg_parent.LayoutChanged(self.dlg_parent.ID_SCROLLGRP_BMP)

        #on recalcule les nouvelles valeurs pour trouver la translation à effecture sur le nouveau zoom
        vis_area = self.dlg_parent.GetVisibleArea(self.dlg_parent.ID_SCROLLGRP_BMP)
        new_item_dim =  self.dlg_parent.GetItemDim(self.dlg_parent.ID_USER_AREA)

        #nouvelle position de la souris sur l'image en proportion depuis le coin en haut à gauche
        new_pos_img_sur_largeur = (mx-new_item_dim['x'])/float(new_item_dim['w'])
        new_pos_img_sur_hauteur = (my-new_item_dim['y'])/float(new_item_dim['h'])

        #différence en pixel -> translation
        trans_x = int(round((old_pos_img_sur_largeur-new_pos_img_sur_largeur) * self.width))
        trans_y = int(round((old_pos_img_sur_hauteur-new_pos_img_sur_hauteur) *self.height))

        x1 = vis_area['x1']+trans_x
        x2 = vis_area['x2']+trans_x
        y1 = vis_area['y1']+trans_y
        y2 = vis_area['y2']+trans_y
        #et on translate la zone d'affichage de l'image
        self.dlg_parent.SetVisibleArea(self.dlg_parent.ID_SCROLLGRP_BMP, x1, y1, x2, y2)

class DlgBitmap(c4d.gui.GeDialog):

    ID_SCROLLGRP_BMP = 1000
    ID_USER_AREA = 1001


    def __init__(self, fn_bmp):
        self.fn_bmp = fn_bmp
        self.bmp_area = BmpUserArea(self)
        res = self.bmp_area.initBMP(self.fn_bmp)
        if not res :
            self.bmp_area = None

    def CreateLayout(self):
        if self.bmp_area:
            if self.ScrollGroupBegin(self.ID_SCROLLGRP_BMP,
                                     c4d.BFH_SCALEFIT|c4d.BFV_SCALEFIT,
                                     scrollflags=c4d.SCROLLGROUP_VERT | c4d.SCROLLGROUP_HORIZ, initw=200, inith=200) :
               self.AddUserArea(self.ID_USER_AREA, c4d.BFH_CENTER | c4d.BFV_CENTER)
               self.AttachUserArea(self.bmp_area, self.ID_USER_AREA)

            self.GroupEnd()

        else:
            c4d.gui.MessageDialog("Problème avec le fichier image")
            return False

        return True


# Execute main()
if __name__=='__main__':
    fn_img = '/Users/olivierdonze/Documents/TEMP/canvas.png'
    #fn_img = '/Users/donzeo/Documents/TEMP/image_test_calage.jpg'
    dlg = DlgBitmap(fn_img)
    dlg.Open(c4d.DLG_TYPE_ASYNC)