from typing import Optional
import c4d

doc: c4d.documents.BaseDocument  # The active document
op: Optional[c4d.BaseObject]  # The active object, None if unselected

def get_alts_from_ascii(fn_ascii,scale = 200, header_size = 6):
    """returns a list of heights multiplied by the scale factor
       from an asc file of type Esri grid ascii (with 6 lines header)"""
    alts = []
    with open(fn_ascii) as f:
        for i,line in enumerate(f):
            #we don't need the header (6 lines)
            if i>=header_size:
                alts += [float(alt)*scale for alt in line.split()]
    return alts

def main() -> None:
    # Called when the plugin is selected by the user. Similar to CommandData.Execute.
    
    fn = '/Users/olivierdonze/switchdrive/Mandats/Nuit_de_la_science/Programmation_bac_a_sable/depthmap.asc'
    alts = get_alts_from_ascii(fn)
    print(alts[0:10])
    #
    grid_object = op   
    change_alt = lambda v,alt: c4d.Vector(v.x,alt,v.z) 
    pts = [change_alt(v,alt) for v,alt in zip(op.GetAllPoints(),alts)]
    op.SetAllPoints(pts)
    op.Message(c4d.MSG_UPDATE)
    c4d.EventAdd()
    

    

"""
def state():
    # Defines the state of the command in a menu. Similar to CommandData.GetState.
    return c4d.CMD_ENABLED
"""

if __name__ == '__main__':
    main()