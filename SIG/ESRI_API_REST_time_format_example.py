from typing import Optional
import c4d
from datetime import datetime, timezone

doc: c4d.documents.BaseDocument  # The active document
op: Optional[c4d.BaseObject]  # The active object, None if unselected



def year2utc(year):
    #time=1199145600000 (1 Jan 2008 00:00:00 GMT) 
    # date in string format
   
    # convert to datetime instance
    date_time = datetime.strptime(year, '%Y')
    
    # get UTC timestamp
    utc_timestamp = date_time.replace(tzinfo=timezone.utc).timestamp()
    
    # timestamp in milliseconds
    return utc_timestamp*1000





def main() -> None:
    an = "2019"
    ts = year2utc(an)
    print(ts)
        
    
    #print('000000'+str(int(d.timestamp()*1000000))+'000')



"""
def state():
    # Defines the state of the command in a menu. Similar to CommandData.GetState.
    return c4d.CMD_ENABLED
"""

if __name__ == '__main__':
    main()