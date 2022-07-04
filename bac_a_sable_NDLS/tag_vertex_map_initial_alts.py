from typing import Optional
import c4d

doc: c4d.documents.BaseDocument  # The active document
op: Optional[c4d.BaseObject]  # The active object, None if unselected

def main() -> None:
    # Called when the plugin is selected by the user. Similar to CommandData.Execute.
    tag = c4d.VariableTag(c4d.Tvertexmap, op.GetPointCount())
    tag.SetName('altitudes_initiales')
    data = tag.GetAllHighlevelData()
    
    for i,pt in enumerate(op.GetAllPoints()):
        data[i] = pt.y
    tag.SetAllHighlevelData(data)
    op.InsertTag(tag)
    c4d.EventAdd()

"""
def state():
    # Defines the state of the command in a menu. Similar to CommandData.GetState.
    return c4d.CMD_ENABLED
"""

if __name__ == '__main__':
    main()