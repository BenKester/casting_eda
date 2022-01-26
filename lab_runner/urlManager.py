# robobrowser fails without this hack
import werkzeug
werkzeug.cached_property = werkzeug.utils.cached_property

from robobrowser import RoboBrowser
import json

with open('data\\urls.json', 'r') as infile:
    urls = json.load(infile)

def triSwitch(val, ifTrue, ifFalse, ifNone=None):
    if val is None:
        return ifNone
    return ifTrue if val == True else ifFalse

class Params:
    def __init__(self, dic):
        self.dic = {k:v for k, v in dic.items() if not v is None}

    def __repr__(self):
        return self.dic.__repr__()

    def __str__(self):
        return self.dic.__str__()

class EnchantParams(Params):
    def __init__(self, enchant_name=None, league=None, min_chaos_buyout=None):
        form = {'league': league, 'abc': enchant_name}
        if min_chaos_buyout > 0:
            form['min_buyout'] = min_chaos_buyout
            form['buyout_currency'] = 'Chaos Orb'
        form['group_type'] = 'And'
        Params.__init__(self, form)


class GemParams(Params):
    def __init__(self, league=None, gemName=None, minQuality=None, maxQuality=None, minLevel=None, maxLevel=None, corrupted=None, online=None):
        Params.__init__(self, {'league': league, 'name': gemName, 'q_min': minQuality, 'q_max': maxQuality, 'level_min': minLevel, 'level_max': maxLevel, 'corrupted': corrupted, 'online': triSwitch(online, 'x', '')})

def pullURL(params):
    browser = RoboBrowser(history=True)
    browser.open('http://poe.trade/')
    form = browser.get_form(action='/search')
    for k, v in params.dic.items():
        if k.lower() == 'base':
            form.fields[k.lower()].options.append(v)
        form[k.lower()] = v
    
    browser.submit_form(form)
    return browser.url

def save():
    global urls
    with open('data\\urls.json', 'w') as outfile:
        json.dump(urls, outfile, indent=4, sort_keys=True)


def getURL(params):
    global urls
    key = params.__repr__()
    if not key in urls:
        urls[key] = pullURL(params)
        save()
    return urls[key]