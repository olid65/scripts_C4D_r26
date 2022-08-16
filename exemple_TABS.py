from typing import Optional
import c4d

doc: c4d.documents.BaseDocument  # The active document
op: Optional[c4d.BaseObject]  # The active object, None if unselected


class Dlg(c4d.gui.GeDialog):
    def CreateLayout(self):
        if self.TabGroupBegin(1000, c4d.BFH_SCALEFIT | c4d.BFV_SCALEFIT, tabtype=c4d.TAB_TABS):
            
            if self.GroupBegin(1001, c4d.BFH_SCALEFIT | c4d.BFV_SCALEFIT, 0, title="Géoréférencemnt", groupflags=c4d.BFV_BORDERGROUP_FOLD_OPEN):
                self.GroupEnd()
                
            if self.GroupBegin(1002, c4d.BFH_SCALEFIT | c4d.BFV_SCALEFIT, 0, title="SITG", groupflags=c4d.BFV_BORDERGROUP_FOLD_OPEN):
                self.GroupEnd()
            
            if self.GroupBegin(1003, c4d.BFH_SCALEFIT | c4d.BFV_SCALEFIT, 0, title="swisstopo", groupflags=c4d.BFV_BORDERGROUP_FOLD_OPEN):
                self.GroupEnd()
            
            if self.GroupBegin(1004, c4d.BFH_SCALEFIT | c4d.BFV_SCALEFIT, 0, title="ESRI", groupflags=c4d.BFV_BORDERGROUP_FOLD_OPEN):
                self.GroupEnd()

        self.GroupEnd()
        self.AddButton(1003, c4d.BFH_SCALEFIT | c4d.BFV_SCALEFIT, name="Activate second Tab")
        
        return True
    
    
    def Command(self, id, msg):
        # Id of the TabGroupBegin
        if id == 1000:
            print (self.GetInt32(1000))
            
        # Id of the Button
        if id == 1003:
            self.SetInt32(1000, 1002)
        
        return True
    
# Main function
def main():
    dlg = Dlg()
    dlg.Open(c4d.DLG_TYPE_MODAL_RESIZEABLE)

# Execute main()
if __name__=='__main__':
    main()