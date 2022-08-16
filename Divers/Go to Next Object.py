from typing import Optional
import c4d

doc: c4d.documents.BaseDocument  # The active document
op: Optional[c4d.BaseObject]  # The active object, None if unselected

def main() -> None:
    if op:
        nxt = op.GetNext()
        if not nxt:
            if op.GetUp():
                nxt = op.GetUp().GetDown()
            else:
                nxt = doc.GetFirstObject()
        doc.SetActiveObject(nxt)    
        c4d.EventAdd()
"""
def state():
    # Defines the state of the command in a menu. Similar to CommandData.GetState.
    return c4d.CMD_ENABLED
"""

if __name__ == '__main__':
    main()