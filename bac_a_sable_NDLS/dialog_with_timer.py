from typing import Optional
import c4d
import json
import random
import math

doc: c4d.documents.BaseDocument  # The active document
op: Optional[c4d.BaseObject]  # The active object, None if unselected

NAME_OBJ_DEPTHMAP = 'depthmap'
NAME_TAG_ALTS = 'altitudes_initiales'

NAME_OBJ_TREES = 'arbres'
NAME_SOURCE_TREES = 'source_arbres'

NB_PX_X = 588
NB_PX_Z = 432

class DlgBbox(c4d.gui.GeDialog):

    TIME_INTERVAL = 10000 #milliseconds

    TXT_BTON_TIMER_ON = "stop process"
    TXT_BTON_TIMER_OFF = "start process"

    ID_BTON_TEST = 1000

    timer = False

    def __init__(self,sandbox):
        self.sandbox = sandbox

    def CreateLayout(self):

        self.SetTitle("Bac à sable")
        self.GroupBegin(500, flags=c4d.BFH_CENTER, cols=1, rows=1)
        self.AddButton(self.ID_BTON_TEST, flags=c4d.BFH_CENTER, initw=300, inith=50, name=self.TXT_BTON_TIMER_OFF)

        return True

    def Command(self, id, msg):
        if id == self.ID_BTON_TEST:
            if self.timer:
                self.timer = False
                self.SetTimer(0)
                self.SetString(self.ID_BTON_TEST,self.TXT_BTON_TIMER_OFF)
            else:
                self.timer = True
                self.SetTimer(self.TIME_INTERVAL)
                self.SetString(self.ID_BTON_TEST,self.TXT_BTON_TIMER_ON)
        return True

    def Timer(self,msg):
        self.sandbox.update()
        c4d.EventAdd()
        c4d.CallCommand(12163) # Render View

class Sandbox(object):

    FN_ASCII = '/Users/olivierdonze/switchdrive/Mandats/Nuit_de_la_science/Programmation_bac_a_sable/depthmap.asc'
    FN_TREES = '/Users/olivierdonze/switchdrive/Mandats/Nuit_de_la_science/Programmation_bac_a_sable/tags.json'

    SCALE_ALT = 10
    SCALE_TREES = 2

    NB_PX_GRADIENT = 100 #nombre de pixel dans les marges
    SMOOTH = True #True si on veut lisser les marges des bords


    def __init__(self,doc):

        #TODO : gestion des erreurs !
        self.doc = doc

        #depthmap object and tags
        self.depthmap_obj = self.doc.SearchObject(NAME_OBJ_DEPTHMAP)
        self.tag_alts = None
        for tag in self.depthmap_obj.GetTags():
            if tag.CheckType(c4d.Tvertexmap):
                if tag.GetName()==NAME_TAG_ALTS:
                    self.tag_alts = tag
        #trees
        self.trees_objs = self.doc.SearchObject(NAME_OBJ_TREES)
        srce_parent = self.doc.SearchObject(NAME_SOURCE_TREES)

        #dico pour stocker les sources avec l'id en étiquette et la liste des objets (variantes) en clé
        self.trees_srce = {int(child.GetName()):child.GetChildren() for child in srce_parent.GetChildren()}


    def update(self):
        self.doc = c4d.documents.GetActiveDocument()
        self.update_terrain()
        self.update_trees()

    def update_terrain(self):
        pts = self.depthmap_obj.GetAllPoints()
        alts = self.get_alts_from_ascii()
        alts_initial = self.tag_alts.GetAllHighlevelData()

        #pour l'instant alt initial n'est pas utilisée -> pour terrain existant
        for i,(pt,alt,alt_initial) in enumerate(zip(pts,alts,alts_initial)):
            #calcul du facteur dans les bords
            id_row = int(i / NB_PX_X)
            id_col = i % NB_PX_X
            factor = 1
            if self.NB_PX_GRADIENT:
                x1 = id_col/ self.NB_PX_GRADIENT
                x2 = (NB_PX_X-1-id_col)/self.NB_PX_GRADIENT
                z1 = id_row/ self.NB_PX_GRADIENT
                z2 = (NB_PX_Z-1-id_row)/self.NB_PX_GRADIENT
                val = min([x1,x2,z1,z2])
                if self.SMOOTH:
                    factor = c4d.utils.Smoothstep(0, 1, val)
                else:
                    factor = c4d.utils.Clamp( 0, 1,val)

            pt.y = alt_initial + alt*factor

        self.depthmap_obj.SetAllPoints(pts)
        self.depthmap_obj.Message(c4d.MSG_UPDATE)

    def update_trees(self):
        random.seed(123)
        data = self.get_trees_from_json()
        #si l'objet n'existe pas on le crée
        if not self.trees_objs:
            self.trees_objs = c4d.BaseObject(c4d.Onull)
            self.trees_objs.SetName(NAME_OBJ_TREES)
            self.doc.InsertObject(self.trees_objs)
        #sinon on efface les arbres existants
        else:
            for o in self.trees_objs.GetChildren():
                o.Remove()

        for tag in data['tags']:
            inst = c4d.BaseObject(c4d.Oinstance)
            inst[c4d.INSTANCEOBJECT_RENDERINSTANCE_MODE] = c4d.INSTANCEOBJECT_RENDERINSTANCE_MODE_SINGLEINSTANCE

            obj_srce = random.choice(self.trees_srce[tag['tag_id']])

            inst[c4d.INSTANCEOBJECT_LINK] = obj_srce

            #pos = c4d.Vector(tag['position']['x']*FACT_ECHELLE,0,tag['position']['y']*FACT_ECHELLE)

            id_pt = (tag['position']['y'])*NB_PX_X + tag['position']['x']
            pos = c4d.Vector(self.depthmap_obj.GetPoint(id_pt)* self.depthmap_obj.GetMg())

            inst.SetAbsPos(pos)
            inst.SetAbsScale(c4d.Vector(self.SCALE_TREES))

            #Si l'objet à copier est un plan ou un objet polygonal avec 4 points on le tourne vers la caméra
            #sinon on tourne selon les valeurs du tag (QRcode)
            look_at_camera = False

            if obj_srce.CheckType(c4d.Oplane):
                look_at_camera = True
            if obj_srce.CheckType(c4d.Opolygon) and obj_srce.GetPointCount() ==4:
                look_at_camera = True

            if look_at_camera :
                #look at camera tag insertion
                tag_look = c4d.BaseTag(c4d.Tlookatcamera)
                inst.InsertTag(tag_look)
                priority = c4d.PriorityData()
                #priority.SetPriorityValue(c4d.PRIORITYVALUE_MODE,c4d.CYCLE_INITIAL)
                priority.SetPriorityValue(c4d.PRIORITYVALUE_CAMERADEPENDENT,True)
                tag_look[c4d.EXPRESSION_PRIORITY] = priority
                #Je n'arrive pas à rafraichir la vue pour que le tag lookAtCamera fonctionne
                #j'ai été obligé de bricoler ça
                self.look_at_camera(inst)

            else:
                angle  = c4d.utils.DegToRad(tag['rotation'])
                inst.SetAbsRot(c4d.Vector(angle,0,0))



            #nom avec tag_id
            inst.SetName(tag['tag_id'])
            inst.InsertUnderLast(self.trees_objs)
            #inst.Message(c4d.MSG_UPDATE)

    def look_at_camera(self,obj):
        bd = self.doc.GetRenderBaseDraw()
        cp = bd.GetSceneCamera(self.doc)
        local = cp.GetMg().off * (~(obj.GetUpMg() * obj.GetFrozenMln())) - obj.GetRelPos()

        hpb = c4d.utils.VectorToHPB(local)
        hpb.z = obj.GetRelRot().z
        hpb.x += math.pi
        hpb.y = -hpb.y
        obj.SetRelRot(hpb)

    def get_alts_from_ascii(self,header_size = 6):
        """returns a list of heights multiplied by the scale factor
           from an asc file of type Esri grid ascii (with 6 lines header)"""
        alts = []
        with open(self.FN_ASCII) as f:
            for i,line in enumerate(f):
                #we don't need the header (6 lines)
                if i>=header_size:
                    alts += [(float(alt)-0.5)*2*self.SCALE_ALT for alt in line.split()]
        return alts

    def get_trees_from_json(self):
        with open(self.FN_TREES)as f:
            data = json.loads(f.read())
        return data
"""
def state():
    # Defines the state of the command in a menu. Similar to CommandData.GetState.
    return c4d.CMD_ENABLED
"""

if __name__ == '__main__':
    #main()
    sandbox = Sandbox(doc)
    dlg = DlgBbox(sandbox)
    dlg.Open(c4d.DLG_TYPE_ASYNC)