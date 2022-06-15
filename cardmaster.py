import os
import database as db
import utility as utils
import filehandler as fh

card_master = {}
card_master_by_name = {}
card_master_by_craft = [[] for i in range(db.craft_count)]
card_dir = os.path.join('.', 'card')

class Card:
    def __init__(self, info):
        self.info = info
        self.id = int(info['id'])
        self.name = utils.strip_quote(info['name'])
        self.pack = int(info['pack'])
        self.pack_name = db.pack_name[self.pack]
        self.craft = int(info['craft'])
        self.craft_name = db.craft_name[self.craft]
        self.rarity = int(info['rarity'])
        self.rarity_name = db.rarity_name[self.rarity-1]
        self.type = int(info['type'])
        self.type_name = db.type_name[self.type-1]
        self.trait = utils.int_list_parser(info['trait'], use_list_reader=True)
        self.trait_name = db.trait_name[0]
        for trait_num in self.trait[1:]:
            self.trait_name += f'．{db.trait_name[trait_num]}'
        self.cost = int(info['cost'])
        self.atk = int(info['atk'])
        self.life = int(info['life'])
        self.evo_atk = int(info['evo_atk'])
        self.evo_life = int(info['evo_life'])
        self.effect = utils.concate_content_with_newline(utils.list_reader(info['effect']))
        if self.effect == '\n':
            self.effect = '（沒有卡片能力記敘）'
        self.evo_effect = utils.concate_content_with_newline(utils.list_reader(info['evo_effect']))
    
    def get_status(self, cost=True, atk=True, life=True, evo_atk=False, evo_life=False):
        status = []
        if cost:
            status.append(self.cost)
        if atk:
            status.append(self.atk)
        if life:
            status.append(self.life)
        if evo_atk:
            status.append(self.evo_atk)
        if evo_life:
            status.append(self.evo_life)
        return status

    def is_normal(self):
        return ((self.id // 100_000_000) == 1)
    
    def is_in_rotation(self):
        count = db.pack_count
        return self.is_normal() and ((self.pack == 0) or ((self.pack not in range(1,4)) and (self.pack in range(count - 5, count))))

    def is_in_2pick(self):
        return self.is_in_rotation()

def init_card_master():
    global card_master, card_dir
    path = os.path.join(card_dir, 'card_master.csv')
    content = fh.read(path)
    for card_info in content:
        card = Card(card_info)
        card_master[card.id] = card
        card_master_by_name[card.name] = card
        card_master_by_craft[card.craft].append(card)
    return

def search_by_name(name):
    if name in card_master_by_name:
        return card_master_by_name[name]
    return None