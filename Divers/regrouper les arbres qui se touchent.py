from typing import Optional
import c4d

from collections import deque

doc: c4d.documents.BaseDocument  # The active document
op: Optional[c4d.BaseObject]  # The active object, None if unselected

""" Opération booléenne Union sur les arbres qui se touchent
    Sélectionner l'ojet parent contenant tous les arbres individuels.
    Utilise le rayon (x et z) de l'objet, il faut donc des éléments plus ou moins ciruclaire en plan
    L'axe doit bein ^être au centre de chaque objet en x et z (->TODO tenir compte si l'axe n'est pas centré)
    
    ATTENTION1 peut prendre du temps ne pas hésiter à faire par groupes
    
    ATTENTION2 les éléments d'origines seront effacés pas d'annulation possible ! (->TODO)
    
    ATTENTION3 il semble qu'il y ait une limite dans le nombre de récursivité, 
    faire en plusieurs groupes si cela ne fonctionne pas"""


class Tree(object):
    """classe pour contenir tous les noeuds qui se touchent
       Attention il s'agit d'un arbre au sens algorithmique
       pas au niveau botanique !"""
   
    def __init__(self,root_node,doc):
        self.root = root_node
        self.doc = doc

    def find_touch(self,node,nodes):
        res = []
        for n in nodes:
            if n.touch(node):
                res.append(n)
        node.add_children(res)
        for n in res:
            nodes.remove(n)
        for n in res:
            self.find_touch(n,nodes)

    def parse(self, node):
        print(node)
        for child in node.children:
            self.parse(child)
    
    def union(self,node1,obj2 = None):
        """méthode recursive pour l'opération booléenne sur les objets"""
        
        #si on n'a pas l'obj2 on est à la racine, donc pas d'union
        # on passe l'objet du noeud à obj2 pour l'opération suivante dans la récursivité
        if not obj2:
                obj2 = node1.obj
        else:
            obj2 = union_objects(node1.obj,obj2, self.doc, name = 'union')
        
        for child in node1.children:
            obj2 = self.union(child, obj2)
        
        return obj2


class Node(object):
    """classe pour les nooeuds de l'arbre"""
    def __init__(self,obj):
        self.obj = obj
        self.pt = obj.GetMg().off
        rad = obj.GetRad()
        self.rayon = max((rad.x,rad.z))*obj.GetAbsScale()[0]
        self.children = []

    def add_children(self,children):
        self.children.extend(children)

    def touch(self,other):
        dist = self.rayon+ other.rayon
        if (self.pt-other.pt).GetLength() <= dist:
            return True
        return False

    def __eq__(self, other):
        return self.obj == other.obj

    def __repr__(self):
        return str(self)

    def __str__(self):
        return self.obj.GetName()
    
    
def union_objects(op1,op2, doc, name = None):
    """renvoie l'objet' résultat d'une opération booléenne union"""
    boolobj = c4d.BaseObject(c4d.Oboole)
    boolobj[c4d.BOOLEOBJECT_SINGLE_OBJECT] = True
    
    boolobj[c4d.BOOLEOBJECT_TYPE] = c4d.BOOLEOBJECT_TYPE_UNION
    mg1 = op1.GetMg()
    mg2 = op2.GetMg()
    op1.InsertUnder(boolobj)
    op2.InsertUnder(boolobj)
    
    op1.SetMg(mg1)
    op2.SetMg(mg2)
    
    doc.InsertObject(boolobj)
    
    res = c4d.utils.SendModelingCommand(command=c4d.MCOMMAND_MAKEEDITABLE,  
                                    list=[boolobj],
                                    mode=c4d.MODELINGCOMMANDMODE_ALL,   
                                    bc=c4d.BaseContainer(),    
                                    doc=doc)
    
    if res:
        resobj = res[0].GetDown() 
        if name and resobj:
            resobj.SetName(name)
        doc.InsertObject(resobj)
        return resobj
    return None





def main() -> None:

    # Called when the plugin is selected by the user. Similar to CommandData.Execute.
    res = c4d.BaseObject(c4d.Onull)
    
    #stockage des noeuds (deque est apparemment plus efficace pour les piles)
    objs = deque([Node(o) for o in op.GetChildren()])
    i = 0
    res = c4d.BaseObject(c4d.Onull)
    res.SetName(op.GetName())
    #création des arbres (sorte de graphe)
    while objs:
        #on prend le premier objet de la pile
        obj = objs.popleft()
        tree = Tree(obj,doc)
        #méthode récursive qui prend tous les éléments qui se touchent
        #et les enlève de la pile
        tree.find_touch(obj,objs)
        #opération booléenne sur les élément de l'arbre'
        poly_union = tree.union(tree.root,obj2 = None)
        poly_union.InsertUnderLast(res)
    doc.InsertObject(res)
    
    #suppression de l'objet parentsi vide
    if not op.GetChildren():
        op.Remove()
    
    #Connecter et supprimer
    doc.SetActiveObject(res)
    for o in res.GetChildren():
        o.SetBit(c4d.BIT_ACTIVE)
    c4d.CallCommand(16768) # Connect Objects + Delete
    c4d.EventAdd()
    
    return



"""
def state():
    # Defines the state of the command in a menu. Similar to CommandData.GetState.
    return c4d.CMD_ENABLED
"""

if __name__ == '__main__':
    main()