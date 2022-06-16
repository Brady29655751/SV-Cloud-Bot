import random
import cardmaster as cm
import database as db
import game as sv

def init_game(player_1, player_2):
    craft_list_1 = give_craft()
    craft_list_2 = give_craft()
    player_1.data['2pick_craft_list'] = craft_list_1
    player_2.data['2pick_craft_list'] = craft_list_2
    return [craft_list_1, craft_list_2]

def give_craft():
    craft = random.sample(db.craft_name[1:], 3)
    return craft

def set_craft(player, craft):
    player.data['2pick_craft'] = db.craft_name.index(craft)
    return 

def give_pick(player, turn):
    legend = [1, 8, 15]
    bronze = [2, 4, 7, 9, 11, 13]
    silver = [3, 6, 12, 14]
    neutral = [5, 10]

    if turn > 15:
        return

    craft = player.data['2pick_craft']
    pick_list = []
    if turn in legend:
        pick_list = list(filter(lambda x: (x.rarity >= 3), cm.card_master_by_craft[craft]))
        pick_neutral = list(filter(lambda x: x.rarity == 4, cm.card_master_by_craft[0]))
        pick_list.extend(pick_neutral)
    elif turn in bronze:
        pick_list = list(filter(lambda x: (x.rarity == 1), cm.card_master_by_craft[craft]))
    elif turn in silver:
        pick_list = list(filter(lambda x: (x.rarity == 2), cm.card_master_by_craft[craft]))
    elif turn in neutral:
        pick_list = list(filter(lambda x: (x.rarity <= 3), cm.card_master_by_craft[0]))
    
    pick_list = list(filter(lambda x: x.is_in_2pick(), pick_list))
    pick = random.sample(pick_list, 4)
    left = [pick[0].name, pick[1].name]
    right = [pick[2].name, pick[3].name]
    player.data['2pick_左'] = left
    player.data['2pick_右'] = right
    player.data['2pick_turn'] = turn
    return [left, right]

def set_pick(player, pick):
    count = len(player.deck)
    if (count >= 30) or (not pick[0]) or (not pick[1]):
        return
    sv.add_deck(player, [count+1, count+2])
    sv.modify_deck_effect(player, 'add', pick[0], [count+1])
    sv.modify_deck_effect(player, 'add', pick[1], [count+2])
    return


