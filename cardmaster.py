import os
import database as db
import utility as utils
import filehandler as fh

card_master = {}
card_master_by_name = {}
card_master_by_craft = [[] for i in range(db.craft_count)]
card_dir = os.path.join('.', 'card')

def init_card_name(name):
    new_name = utils.strip_quote(name)
    new_name = utils.replace_dot(new_name)
    return new_name

def init_card_trait(trait):
    trait_list = trait.split('\\')
    trait_list = utils.int_list_parser(trait_list)
    return trait_list

def init_card_effect(effect):
    if not effect:
        return '（沒有卡片能力記敘）'

    new_effect = effect.replace('\\', '\n')
    new_effect = utils.replace_dot(new_effect)
    return new_effect

class Card:
    def __init__(self, info):
        self.info = info
        try:
            self.id = int(info['id'])
            self.name = init_card_name(info['name'])
            self.pack = int(info['pack'])
            self.pack_name = db.pack_name[self.pack]
            self.craft = int(info['class'])
            self.craft_name = db.craft_name[self.craft]
            self.rarity = int(info['rarity'])
            self.rarity_name = db.rarity_name[self.rarity-1]
            self.type = int(info['type'])
            self.type_name = db.type_name[self.type-1]
            self.trait = init_card_trait(info['trait'])
            self.trait_name = db.trait_name[self.trait[0]]
            for trait_num in self.trait[1:]:
                self.trait_name += f'．{db.trait_name[trait_num]}'
            self.cost = int(info['cost'])
            self.atk = int(info['atk'])
            self.life = int(info['life'])
            self.evo_atk = int(info['evoAtk'])
            self.evo_life = int(info['evoLife'])
            self.effect = init_card_effect(info['effect'])
            self.evo_effect = init_card_effect(info['evoEffect'])
        except Exception:
            print(self.id)
    
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

    def is_in_2pick(self, pack_list=[(db.pack_count - 4 + i) for i in range(4)]):
        if self.pack == 0:
            card_list = [
                100010001, 100010002, 100010005,
                100020001, 100020002, 100020003,
                100030001, 100030003, 100030004,
                100040001, 100040002, 100040003,
                100050001, 100050003, 100050008,
                100060003, 100060004, 100060006,
                100070004, 100070005, 100070009,
                100080003, 100080005, 100080007
            ]
            return self.id in card_list
        return self.is_normal() and self.pack in pack_list

def init_card_master():
    global card_master, card_dir
    path = os.path.join(card_dir, 'card_master.csv')
    content = fh.read(path)
    for card_info in content:
        card_id = card_info['id']
        if not utils.int_parser(card_id, True):
            continue
        
        card = Card(card_info)
        card_master[card.id] = card
        card_master_by_name[card.name] = card
        card_master_by_craft[card.craft].append(card)
    return

def search_card(name, option='name'):
    token = name
    if option == 'name':
        token = init_card_name(token)
        if token in card_master_by_name:
            return card_master_by_name[token]
    elif option == 'id':
        if token in card_master:
            return card_master[token]
    return None