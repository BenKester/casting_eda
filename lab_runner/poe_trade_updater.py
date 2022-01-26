# run 1x before the league ends
from collections import UserDict, defaultdict
from urllib.parse import quote
import re
from bs4 import BeautifulSoup

from utils import get_html, get_soup
from data import Aggregated, Config
from list_matcher import match_lists, full_matcher

def get_explicit_mods():
    js = get_html(r'https://poe.trade/static/gen/explicit.9fa0ff78.js')
    html = js.replace('EXPLICIT_TPL = " ', '')[:-2].replace(r'\"', '"')
    soup = BeautifulSoup(html, 'html.parser')
    
    optgroup = soup.find_all('optgroup', {'label': 'enchantments'})[0]
    texts = [og.text for og in optgroup.find_all('option')]
    texts.remove('(enchant) Storm Burst has a 15% chance to create an additional Orb') # dupe
    
    def condenser(s):
        ret = s.replace('(enchant) ', '').strip()
        return re.sub('[0-9.]+', '#', ret)  # replace a series of digits with #    
    
    ret = match_lists(Aggregated().keys(), texts, condenser, no_dupes=True)

    ret[0]['Barrage fires an additional Projectile'] = '(enchant) Barrage fires # additional Projectiles'
    ret[0]['Lacerate deals (14-18) to (20-25) added Physical Damage against Bleeding Enemies'] = '(enchant) Lacerate deals # to # added Physical Damage against Bleeding Enemies'
    ret[0]['Tornado Shot fires an additional secondary Projectile'] = '(enchant) Tornado Shot fires # additional secondary Projectiles'
    ret[0]['Volatile Dead Consumes up to 1 additional corpse'] = '(enchant) Volatile Dead Consumes up to # additional corpses'
    ret[0][r"+8% chance to Suppress Spell Damage if you'vetaken Spell Damage Recently"] = r"(enchant) +#% chance to Suppress Spell Damage if you've taken Spell Damage Recently"
    
    if len([x for x in ret[0] if ret[0][x]==None]) > 0:
        print([x for x in ret[0] if ret[0][x]==None])
        raise Exception('More mismatches than expected')
    
    return ret[0]

def get_query(ordered_keys, dictionary):
    return '&'.join([f'{key}={quote(str(dictionary[key]))}' for key in ordered_keys])

class ExplicitMod(UserDict):
    # list of explicit mods here https://poe.trade/static/gen/explicit.9fa0ff78.js
    # if that doesn't work, pull up poe.trade source and look for the javascript on the first line with the explicit mods list
    # browser search is inefficient, can pull this in vscode for quicker searching
    def __init__(self, **args):
        self.order = ['mod_name', 'mod_min', 'mod_max', 'mod_weight']
        self.data = {key:'' for key in self.order}
        self.data.update(args)
        if len(self.data) > 4:
            raise Exception('invalid argument passed')
    def get_ordered_keys(self):
        return self.order
    def get_ordered_values(self):
        return [self.data[key] for key in self.order]
    def get_url_text(self):
        return get_query(self.order, self.data)
    
class PoeTradeUrlGen:
    def __init__(self, **args):
        self.prefix = 'https://poe.trade/search?'
        self.base_keys = ['league', 'type', 'base', 'name', 'dmg_min', 'dmg_max', 'aps_min', 'aps_max', 'crit_min', 'crit_max', 'dps_min', 'dps_max', 'edps_min', 'edps_max', 
                            'pdps_min', 'pdps_max', 'armour_min', 'armour_max', 'evasion_min', 'evasion_max', 'shield_min', 'shield_max', 'block_min', 'block_max', 
                            'sockets_min', 'sockets_max', 'link_min', 'link_max', 'sockets_r', 'sockets_g', 'sockets_b', 'sockets_w', 'linked_r', 'linked_g', 'linked_b', 'linked_w', 
                            'rlevel_min', 'rlevel_max', 'rstr_min', 'rstr_max', 'rdex_min', 'rdex_max', 'rint_min', 'rint_max', 'group_type', 'group_min', 'group_max', 
                            'group_count', 'q_min', 'q_max', 'level_min', 'level_max', 'ilvl_min', 'ilvl_max', 'rarity', 'progress_min', 'progress_max', 'sockets_a_min', 
                            'sockets_a_max', 'map_series', 'altart', 'identified', 'corrupted', 'crafted', 'enchanted', 'fractured', 'synthesised', 'mirrored', 'veiled', 
                            'shaper', 'elder', 'crusader', 'redeemer', 'hunter', 'warlord', 'replica', 'seller', 'thread', 'online', 'capquality', 'buyout_min', 'buyout_max', 
                            'buyout_currency', 'has_buyout', 'exact_currency']
        self.base_dict = {itm:'' for itm in self.base_keys}
        self.base_dict['group_type'] = 'And'
        self.explicit_mods = []
        self.insert_pos = 44

        size = len(self.base_dict)
        self.base_dict.update(args)
        if len(self.base_dict) > size:
            raise Exception('invalid argument passed')
    def sa_non_explicit(self, key:str, value):
        self.base_dict[key] = value
    def add_explicit_mods(self, obj:ExplicitMod):
        self.explicit_mods.append(obj)
    def get_url(self):
        self.base_dict['group_count'] = len(self.explicit_mods)
        ret = self.prefix
        ret += get_query(self.base_keys[:self.insert_pos], self.base_dict)
        for mod in self.explicit_mods:
            ret += '&' + mod.get_url_text()
        ret += '&' + get_query(self.base_keys[self.insert_pos:], self.base_dict)
        return ret

def get_base_type_from_item_name(item_name):
    return get_first_re_match(item_name, [
        ".+'s ([a-zA-Z]+ [a-zA-Z]+) of .+",            # magic
        "[a-zA-Z]+ [a-zA-Z]+ ([a-zA-Z]+ [a-zA-Z]+)",   # rare
        "([a-zA-Z]+ [a-zA-Z]+)",                       # normal
    ])

def get_first_re_match(text:str, expressions):
    for expression in expressions:
        match = re.match(expression, text)
        if match != None:
            return match.group(1)
        
def parse_row(row, config):
    ret = {}
    ret['item name'] = row['data-name']
    ret['unique'] = 'poewiki.net' in str(row)
    if not ret['unique']:
        ret['base type'] = get_base_type_from_item_name(row['data-name'])
    ret['influences'] = {influence: f'"stat-{influence}"' in str(row) for influence in config['influences']}
    ret['sortable mods'] = [item['data-name'] for item in row.find_all('li', {'class': 'sortable'})]
    ret['implicits'] = [item['data-name'] for item in row.find_all('li', {'class': 'sortable'}) if '(implicit)' in item['data-name']]
    return ret

def get_stats(total_results, row_data):
    ret = {}
    ret['total results'] = total_results
    ret['influence'] = defaultdict(int)
    ret['multi_influence'] = 0
    ret['uniques'] = defaultdict(int)
    ret['implicits'] = defaultdict(int)
    ret['rare base types'] = defaultdict(int)

    for result in row_data:
        influence_count = 0
        for influence in result['influences'].keys():
            if result['influences'][influence]:
                ret['influence'][influence] += 1
                influence_count += 1
        if influence_count >= 2:
            ret['multi_influence'] += 1

        for implicit in result['implicits']:
            ret['implicits'][implicit] += 1
        if result['unique']:
            ret['uniques'][result['item name']] += 1
        else:
            ret['rare base types'][result['base type']] += 1

    return ret

def update_trade_data():
    config = Config()
    mods = get_explicit_mods()
    agg = Aggregated()
    for enchant, explicit_mod in mods.items():
        urlgen = PoeTradeUrlGen(league=config['league'], buyout_min=config['Poe Trade']['Enchant Baseline Chaos'], 
                                    buyout_currency='chaos', online='on')
        urlgen.add_explicit_mods(ExplicitMod(mod_name=explicit_mod))
        soup = get_soup(urlgen.get_url())
        
        try:
            total_results = int(re.search('[0-9]+', soup.find_all('h3', {'class': 'title'})[0].text.split('\n')[3]).group(0))
        except:
            total_results = -1
        results = soup.find_all('div', {'class': 'search-results-block'})
        if len(results) > 0:
            rows = soup.find_all('div', {'class': 'search-results-block'})[0].find_all('tbody')
            row_data = [parse_row(row, config) for row in rows]
            stats = get_stats(total_results, row_data)
        else:
            stats = 'not found'
            print(f'stats not found for enchant {enchant}')
        
        agg[enchant]['poe trade stats'] = stats

    agg.save()
    print('success!')

if __name__ == '__main__':
    update_trade_data()