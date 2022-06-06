from typing import Optional
import c4d

doc: c4d.documents.BaseDocument  # The active document
op: Optional[c4d.BaseObject]  # The active object, None if unselected

# Sélectionnez le rectangle pour découper les arbres
# attention l'axe doit bien etre dans le sens du rectangle et au centre
# le script cherche points_arbres_SITG_2018 et les tags weights selection de arbres_SITG_2018_cloneur

id_cloner = 1018544
def main() -> None:
    pts_trees = op
    if not op:
        print('pas op')
    
    cloner = op.GetNext()
    while cloner:
        if cloner.CheckType(id_cloner):
            break
        cloner = cloner.GetNext()

    bs = pts_trees.GetPointS()
    to_remove=[i for i, selected in enumerate(bs.GetAll(pts_trees.GetPointCount())) if selected]

    tags = [tag for tag in cloner.GetTags() if tag.CheckType(c4d.Tmgweight)]
    doc.StartUndo()
    doc.AddUndo(c4d.UNDOTYPE_CHANGE,pts_trees)
    new_pts = [p for i,p in enumerate(pts_trees.GetAllPoints()) if i not in to_remove]
    pts_trees.ResizeObject(len(new_pts),0)
    pts_trees.SetAllPoints(new_pts)
    pts_trees.Message(c4d.MSG_UPDATE)


    for tag in tags:
        doc.AddUndo(c4d.UNDOTYPE_CHANGE,tag)
        weights = c4d.modules.mograph.GeGetMoDataWeights(tag)
        weights = [w for i,w in enumerate(weights) if i not in to_remove]
        c4d.modules.mograph.GeGetMoDataWeights(tag)
        c4d.modules.mograph.GeSetMoDataWeights(tag, weights)
        tag.Message(c4d.MSG_UPDATE)
    doc.EndUndo()
"""
def state():
    # Defines the state of the command in a menu. Similar to CommandData.GetState.
    return c4d.CMD_ENABLED
"""

if __name__ == '__main__':
    main()
    c4d.EventAdd()