import pandas as pd
from tabulate import tabulate


from ocr import OCR
from data import Aggregated

class Helper:
    def __init__(self):
        self.ocr = OCR()
        self.data = Aggregated()
    
    def refresh(self):
        enchants = self.ocr.get_enchants_from_screenshot()
        return self.to_table_str(enchants)
    
    def flatten(self, enchant):
        record = self.data[enchant]
        print(record)
        if type(record['poe trade stats']) is dict:
            stats = record['poe trade stats']
        else:
            stats = {'total results': 0, 'influence': {}, 'uniques': {}, 'implicits': {}, 'rare base types': {}}
        return {
            'name': enchant[:40],
            'ninja chaos': record.get('ninja_chaos', -1),
            'ninja count': record.get('ninja_listing_count', -1),
            'prev lg trade count': stats['total results'],
            'bases:': self.dict_to_str(stats['rare base types']),
            'influence:': self.dict_to_str(stats['influence']),
            'uniques:': self.dict_to_str(stats['uniques']),
            'implicits:': self.dict_to_str(stats['implicits']),
        }

    def to_table_str(self, enchants):
        rows = [self.flatten(enchant) for enchant in enchants]
        return tabulate(pd.DataFrame(rows), showindex=False, headers='keys')
    
    def dict_to_str(self, d):
        return '\n'.join([f'{str(k)[:40]}: {str(v)[:40]}' for k, v in sorted(d.items(), key=lambda item: item[1], reverse=True)])

    def get_enchant_list(self):
        return list(self.data.keys())

    def get_enchant_data(self, enchant):
        return self.data[enchant]