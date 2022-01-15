# run 1x per league
from utils import get_soup
from data import Aggregated, Skills
import json

def get_skill(enchantment_title, skills):
    for skill in skills:
        if enchantment_title.startswith(f'Enchantment {skill} '):
            return skill
        
def get_enchantments(gear, skills):
    url = f'https://poedb.tw/us/mod.php?type=enchantment&an={gear}'
    _id = f'Labyrinthenchantment_mod_listan{gear}'
    soup = get_soup(url)
    rows = soup.find('div', {'id': _id}).findAll('tr')
    ret = {}
    for row in rows[1:]:
        data = row.findAll('td')
        if data[0].text == 'The Eternal Labyrinth' and len(data) > 3 and data[3] != None and data[3].text.strip() != '':
            ret[data[2].text] = {'gear': gear, 'skill': get_skill(data[1].text, skills)}
    return ret

def update_poedb():
    skills = Skills().data

    data = {}
    for g in ['helmet', 'boots', 'gloves']:
        data.update(get_enchantments(g, skills))
        
    aggregated = Aggregated()
    for k, v in data.items():
        if not k in aggregated:
            aggregated[k] = v
            print(f'new {v["gear"]} enchant: {k} for skill {v["skill"]}')

    aggregated.save()
    print('Updated from poedb. Check added helmet enchants to make sure it found a skill.')

if __name__ == '__main__':
    update_poedb()