import os
import random
import database as db
import utility as utils
import filehandler as fh

card_master=[]
card_master_normal = []
card_master_token = []
card_master_travel = []
card_master_by_id = {}
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

def init_card_ability(ability):
    ability_list = ability.split('\\')
    ability_list = utils.int_list_parser(ability_list, error=True)
    if not ability_list:
        ability_list = []
    return ability_list

def init_card_effect(effect):
    if not effect:
        return '（沒有卡片能力記敘）'

    new_effect = effect.replace('\\', '\n')
    new_effect = utils.replace_dot(new_effect)
    return new_effect

class Card:
    def __init__(self, info):
        self.info = info
        self.info['name'] = init_card_name(self.info['name'])
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
            self.ability = init_card_ability(info['ability'])
            self.ability_name = [db.ability_name[x] for x in self.ability]
            self.cost = int(info['cost'])
            self.atk = int(info['atk'])
            self.life = int(info['life'])
            self.evo_atk = int(info['evoAtk'])
            self.evo_life = int(info['evoLife'])
            self.effect = init_card_effect(info['effect'])
            self.evo_effect = init_card_effect(info['evoEffect'])
            self.token_id = init_card_trait(info['token id'])
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

    def is_normal(self, cygames=True):
        return ((self.id // 100_000_000) == 1) and ((self.pack != 1) or cygames)

    def is_token(self, cygames=True):
        return ((self.id // 100_000_000) == 9) and ((self.pack != 1) or cygames)
    
    def is_in_rotation(self):
        count = db.pack_count
        return ((self.pack == 0) or ((self.pack not in range(1,4)) and (self.pack in range(count - 5, count))))

    def is_in_2pick(self, pack_list=[(db.pack_count - 3 + i) for i in range(3)]):
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
    global card_dir
    path = os.path.join(card_dir, 'card_master.csv')
    content = fh.read(path)
    for card_info in content:
        card_id = card_info['id']
        if not utils.int_parser(card_id, True):
            continue
        
        card = Card(card_info)
        card_master.append(card)
        card_master_by_id[card.id] = card
        card_master_by_name[card.name] = card
        card_master_by_craft[card.craft].append(card)
        if card.is_normal():
            card_master_normal.append(card)
            if card.pack != 1:
                card_master_travel.append(card)
        elif card.is_token():
            card_master_token.append(card)
    return

def search_card(name, option='name'):
    token = name
    if option == 'name':
        token = init_card_name(token)
        if token in card_master_by_name:
            return card_master_by_name[token]
        else:
            card_list = []
            for key in card_master_by_name:
                if token in key:
                    card_list.append(key)
                if len(card_list) > 20:
                    break
            
            if len(card_list) == 1:
                return card_master_by_name[card_list[0]]
            
            def sort_func(name):
                return -(3 * (name == token) + 2 * (('．'+ token) in name) + ((token + '．') in name))
            return sorted(card_list, key=sort_func)
    elif option == 'id':
        if token in card_master_by_id:
            return card_master_by_id[token]
    elif option == 'random':
        card_list = random.sample(card_master, token)
        if len(card_list) == 1:
            return card_list[0]
        return [x.name for x in card_list]
    elif option in ['travel', 'filter']:
        if option == 'travel' and token == 'all':
            return random.choice(card_master_travel)
        else:
            length = len(token)
            card_list = card_master_normal if option == 'filter' else card_master_travel
            for idx in range(0, length, 4):
                if (token[idx] == 'mode') and (idx + 2 < length):
                    mode = token[idx + 2]
                    if mode == 'with_token':
                        card_list = list(set(card_master_token) | set(card_list))
                    elif mode == 'token_only':
                        card_list = card_master_token

            for idx in range(0, length, 4):
                if (token[idx] == 'mode') and (idx + 2 < length):
                    mode = token[idx + 2]
                    if mode in ['rotation', 'rot', 'r', 'R', '指定', '指定系列']:
                        card_list = [x for x in card_list if x.is_in_rotation()]
                    elif mode in ['2pick', '2p']:
                        card_list = [x for x in card_list if x.is_in_2pick()]

            filt_list = set()
            if option == 'travel' and length == 1:
                filt_list = set(filt_card(card_list, 'effect', '=', token[0]))
            elif length % 4 == 3:
                filt_list = set(filt_card(card_list, token[0], token[1], token[2]))
                
                for cur in range(3, length, 4):
                    operator = token[cur]
                    new_list = set(filt_card(card_list, token[cur + 1], token[cur + 2], token[cur + 3]))
                    if operator == 'and':
                        filt_list = filt_list & new_list
                    elif operator == 'or':
                        filt_list = filt_list | new_list
                    else:
                        return []

            filt_list = list(filt_list)
            if filt_list:
                if option == 'travel':
                    return random.choice(filt_list)
                elif option == 'filter':
                    filt_list.sort(key=lambda x: x.pack * 10 + x.craft)
            return filt_list
    return []

def filt_card(card_list, label, compare, target):
    label_list = [
        'id', 'name', 'pack', 'class', 'rarity', 'type',
        'trait', 'cost', 'atk', 'life', 'evoAtk', 'evoLife',
        'countdown', 'ability', 'effect', 'evoEffect',
        'author', 'token_id', 'image_url'
    ]
    if label == 'mode':
        return card_list
    
    if label not in label_list:
        return []
    
    label = utils.concate_content_with_character(label.split('_'), ' ')
    if label == 'name':
        target = init_card_name(target)
    elif label == 'trait':
        trait_id = utils.int_parser(target, error=True)
        if (not isinstance(trait_id, bool)) and trait_id >= 0:
            target = db.trait_name[trait_id]

        if compare == '!=':
            return [x for x in card_list if target not in x.trait_name]
        return [x for x in card_list if target in x.trait_name]
    elif label == 'ability':
        ability_id = utils.int_parser(target, error=True)
        if (not isinstance(ability_id, bool)) and ability_id >= 0:
            target = db.ability_name[ability_id]

        if compare == '!=':
            return [x for x in card_list if (x.ability_name) and (target not in x.ability_name)]
        return [x for x in card_list if (x.ability_name) and (target in x.ability_name)]
    elif label == 'effect':
        return [x for x in card_list if ((target in x.effect) or (target in x.evo_effect))]
    elif label == 'token id':
        card_id = utils.int_parser(target, error=True)
        if card_id:
            if compare == '!=':
                return [x for x in card_list if target[0].id not in x.token_id]    
            return [x for x in card_list if target[0].id in x.token_id]

        card_list = list(set(card_list) | set(card_master_token))
        target = filt_card(card_list, 'name', '=', target)

        if target:
            if compare == '!=':
                return [x for x in card_list if target[0].id not in x.token_id]
            return [x for x in card_list if target[0].id in x.token_id]
    elif label == 'pack':
        if target in db.pack_name:
            target = str(db.pack_name.index(target))
    elif label == 'class':
        if target in db.craft_name:
            target = str(db.craft_name.index(target))
    elif label == 'rarity':
        if target in db.rarity_name:
            target = str(db.rarity_name.index(target) + 1)
    elif label == 'type':   
        if target in db.type_name:
            target = str(db.type_name.index(target) + 1)   
    elif label == 'countdown':
        card_list = filt_card(card_list, 'type', '=', '護符')
    elif label in ['atk', 'life', 'evoAtk', 'evoLife']:
        card_list = filt_card(card_list, 'type', '=', '從者')

    non_numbered_labels = ['name', 'trait', 'ability', 'effect', 'evoEffect', 'author', 'image_url']
    target_int = utils.int_parser(target, error=True)
    if label not in non_numbered_labels and isinstance(target_int, bool) and not target_int:
        return []

    filt_func = lambda x: False
    if compare == '=':
        filt_func = lambda x: (x.info[label] == target) if label in non_numbered_labels \
            else (utils.int_parser(x.info[label]) == utils.int_parser(target))
    elif compare == '>':
        filt_func = lambda x: (x.info[label] > target) if label in non_numbered_labels \
            else (utils.int_parser(x.info[label]) > utils.int_parser(target))
    elif compare == '<':
        filt_func = lambda x: (x.info[label] < target) if label in non_numbered_labels \
            else (utils.int_parser(x.info[label]) < utils.int_parser(target))
    elif compare == '>=':
        filt_func = lambda x: (x.info[label] >= target) if label in non_numbered_labels \
            else (utils.int_parser(x.info[label]) >= utils.int_parser(target))
    elif compare == '<=':
        filt_func = lambda x: (x.info[label] <= target) if label in non_numbered_labels \
            else (utils.int_parser(x.info[label]) <= utils.int_parser(target))
    elif compare == '!=':
        filt_func = lambda x: (x.info[label] != target) if label in non_numbered_labels \
            else (utils.int_parser(x.info[label]) != utils.int_parser(target))
    return [x for x in card_list if filt_func(x)]
