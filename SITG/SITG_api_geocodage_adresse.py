from typing import Optional
import c4d
import urllib.request
from urllib.parse import urlencode
import json
from pprint import pprint
from time import time


def get_adress_SITG(string)->list:
    """renvoie une liste de tuples de 4 éléments (rue, commune, easting, northing)
       ou None si pas fonctioné"""
    t1 = time()
    
    url_base = 'https://geocodage.sitg-lab.ch/api/search?'
    
    params = {'q':string,
              'suggest':'true'}
    params = urllib.parse.urlencode(params)
    
    url = url_base + params 
    res = []
    with urllib.request.urlopen(url) as resp:
        if resp.getcode()==200:
            data = json.loads(resp.read())
            hits = data.get('hits',None)
            if hits:
                for hit in hits:
                    res.append((hit['ADRESSE'],hit['COMMUNE'],hit['easting'],hit['northing']))
    
    return res

doc: c4d.documents.BaseDocument  # The active document
op: Optional[c4d.BaseObject]  # The active object, None if unselected

def main() -> None:
    # Called when the plugin is selected by the user. Similar to CommandData.Execute.
    pprint(get_adress_SITG('rue prairi'))

"""
def state():
    # Defines the state of the command in a menu. Similar to CommandData.GetState.
    return c4d.CMD_ENABLED
"""

if __name__ == '__main__':
    main()