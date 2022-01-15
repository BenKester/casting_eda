# run daily
import json

from utils import get_soup
from data import Aggregated
from list_matcher import full_matcher, get_chr_remover_function

# filter this one because it's ambiguous with the uber lab
FILTER_OUT = ['Lacerate deals 4 to 15 added Physical Damage against Bleeding Enemies']

FIELDS = {
    'chaosValue': 'ninja_chaos', 
    'listingCount': 'ninja_listing_count'
}

def get_economy_data(exclude, fields_to_grab):
    url = 'https://poe.ninja/api/data/ItemOverview?league=Scourge&type=HelmetEnchant&language=en'
    soup = get_soup(url, method='old')
    data = json.loads(soup.text)['lines']
    ret = {line['name']: {k:v for k, v in line.items() if k in fields_to_grab} 
                     for line in data
                     if not 'Allocates' in line['name']}
    
    for idx, line in enumerate(data):
        if line['name'] in ret:
            ret[line['name']]['ninja_rank'] = idx

    for e in exclude:
        ret.pop(e, None)
    
    return ret

def update_economy_data():
    economy = get_economy_data(exclude=FILTER_OUT, fields_to_grab = FIELDS.keys())
    agg = Aggregated()

    a = agg.keys_by_gear('helmet')
    b = economy.keys()

    funcs = [str.lower, 
         get_chr_remover_function('()1234567890-')
        ]
    matches = full_matcher(a, b, funcs, no_dupes=True)
    
    # make sure each helm enchant in our system has an economy item
    # some economy items won't have helm enchants because non-uber versions are included
    if len(matches[2]) > 0:
        print(matches[2])
        raise Exception(f'no match for {len(matches[2])} enchant(s)')    
        
    for agg_name, econ_name in matches[0].items():
        for econ_field, agg_field in FIELDS.items():
            agg[agg_name][agg_field] = economy[econ_name][econ_field]
        agg[agg_name]['ninja_rank'] = economy[econ_name]['ninja_rank']
    
    agg.save()
    print('Economy updates cached')

if __name__ == '__main__':
    update_economy_data()