from typing import Optional
import c4d

"""Sélectionner le neutre contenant les batiments ,
   l'objet point qui définit la bbox doit etre juste après"""

doc: c4d.documents.BaseDocument  # The active document
op: Optional[c4d.BaseObject]  # The active object, None if unselected

class Bbox(object):
    def __init__(self,mini,maxi):

        self.min = mini
        self.max = maxi
        self.centre = (self.min+self.max)/2
        self.largeur = self.max.x - self.min.x
        self.hauteur = self.max.z - self.min.z
    def __str__(self):
        return ('X : '+str(self.min.x)+'-'+str(self.max.x)+'->'+str(self.max.x-self.min.x)+'\n'+
                'Y : '+str(self.min.z)+'-'+str(self.max.z)+'->'+str(self.max.z-self.min.z))
    def xInside(self,x):
        """retourne vrai si la variable x est entre xmin et xmax"""
        return x>= self.min.x and x<= self.max.x

    def zInside(self,y):
        """retourne vrai si la variable x est entre xmin et xmax"""
        return y>= self.min.z and y<= self.max.z

    def isInsideX(self,bbox2):
        """renvoie 1 si la bbox est complètement à l'intérier
           renoive 2 si elle est à cheval
           et 0 si à l'extérieur"""
        minInside = self.xInside(bbox2.xmin)
        maxInside = self.xInside(bbox2.xmax)
        if minInside and maxInside : return 1
        if minInside or maxInside : return 2
        #si bbox1 est plus grand
        if bbox2.xmin < self.min.x and bbox2.xmax > self.max.x : return 2
        return 0

    def isInsideZ(self,bbox2):
        """renvoie 1 si la bbox est complètement à l'intérier
           renoive 2 si elle est à cheval
           et 0 si à l'extérieur"""
        minInside = self.zInside(bbox2.ymin)
        maxInside = self.zInside(bbox2.ymax)
        if minInside and maxInside : return 1
        if minInside or maxInside : return 2
        #si bbox1 est plus grand
        if bbox2.ymin < self.min.z and bbox2.ymax > self.max.z : return 2
        return 0

    def ptIsInside(self,pt):
        """renvoie vrai si point c4d est à l'intérieur"""
        return  self.xInside(pt.x) and self.zInside(pt.z)

    def get_pts(self):
        """renvoie les 4 points de la bbox"""
        p1 = self.min
        p2 = c4d.Vector(self.min.x,0,self.max.z)
        p3 = self.max
        p4 = c4d.Vector(self.max.x,0,self.min.z)
        return [p1,p2,p3,p4]

    def touch(self,bbox2):
        """si un des 4 points de la bbox est à l'intérieur renvoie true"""
        for pt in self.get_pts():
            if bbox2.ptIsInside(pt):
                return True
        return False

    @staticmethod
    def fromObj(obj,origine = c4d.Vector()):
        """renvoie la bbox 2d de l'objet"""
        mg = obj.GetMg()

        rad = obj.GetRad()
        centre = obj.GetMp()

        #4 points de la bbox selon orientation de l'objet
        pts = [ c4d.Vector(centre.x+rad.x,centre.y+rad.y,centre.z+rad.z) * mg,
                c4d.Vector(centre.x-rad.x,centre.y+rad.y,centre.z+rad.z) * mg,
                c4d.Vector(centre.x-rad.x,centre.y-rad.y,centre.z+rad.z) * mg,
                c4d.Vector(centre.x-rad.x,centre.y-rad.y,centre.z-rad.z) * mg,
                c4d.Vector(centre.x+rad.x,centre.y-rad.y,centre.z-rad.z) * mg,
                c4d.Vector(centre.x+rad.x,centre.y+rad.y,centre.z-rad.z) * mg,
                c4d.Vector(centre.x-rad.x,centre.y+rad.y,centre.z-rad.z) * mg,
                c4d.Vector(centre.x+rad.x,centre.y-rad.y,centre.z+rad.z) * mg]

        mini = c4d.Vector(min([p.x for p in pts]),min([p.y for p in pts]),min([p.z for p in pts])) + origine
        maxi = c4d.Vector(max([p.x for p in pts]),max([p.y for p in pts]),max([p.z for p in pts])) + origine

        return Bbox(mini,maxi)

def main() -> None:

    bbox_mnt = Bbox.fromObj(op.GetNext())
    del_lst = []
    for o in op.GetChildren():
        #axe = o.GetMg().off
        #if bbox_mnt.ptIsInside(axe):
            #cnt+=1
        bbox = Bbox.fromObj(o)
        if not bbox.touch(bbox_mnt):
            del_lst.append(o)
    #on efface
    doc.StartUndo()
    for o in del_lst:
        doc.AddUndo(c4d.UNDOTYPE_DELETEOBJ,o)
        o.Remove()
    doc.EndUndo()
    c4d.EventAdd()



"""
def state():
    # Defines the state of the command in a menu. Similar to CommandData.GetState.
    return c4d.CMD_ENABLED
"""

if __name__ == '__main__':
    main()