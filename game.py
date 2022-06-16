import discord
import random
import datetime as dt
import shutil
import os

import utility as utils
import filehandler as fh
import cardmaster as cm
import twopick

#############
# global variable

data_dir = os.path.join('.', 'running_games')

running_games = {}

#############
# utility

class Game:
    def __init__(self, channel, first, second, mode='normal'):
        self.id = random.randrange(0, 30)
        self.room_num = str(10000 + self.id * 3000 + random.randrange(1, 3000))
        while is_room_exist(self.room_num):
            self.room_num =  str(10000 + self.id * 3000 + random.randrange(1, 3000))
        self.channel = channel
        self.is_quitting = False
        self.player_1 = first
        self.player_2 = second
        self.active_time = dt.datetime.now() + dt.timedelta(hours=8)
        self.save_time = dt.datetime.now() + dt.timedelta(hours=8)
        self.mode = mode

class Player:
    def __init__(self, id, name, first):
        self.id = id
        self.name = name
        self.first = '先手' if first == 0 else '後手'
        self.has_kept = False
        self.deck_effect = {}
        self.deck_pos = 3
        self.deck = [i+1 for i in range(0, 40)]
        random.shuffle(self.deck)
        self.data = {}

def is_game_playing(channel_id):
    global running_games
    
    playing = channel_id in running_games
    if playing:
        running_games[channel_id].active_time = dt.datetime.now() + dt.timedelta(hours=8)
    return playing

def is_room_exist(room_num):
    global data_dir
    path = os.path.join(data_dir, room_num)
    return os.path.exists(path)

def is_room_ready(room_num):
    global data_dir
    if not is_room_exist(room_num):
        return False 
    path = os.path.join(data_dir, room_num)
    game_exist = os.path.exists(os.path.join(path, 'game.csv'))
    player_exist = os.path.exists(os.path.join(path, 'player.csv'))
    deck_effect_exist = os.path.exists(os.path.join(path, 'deck_effect_1.csv')) and os.path.exists(os.path.join(path, 'deck_effect_2.csv'))
    return game_exist and player_exist and deck_effect_exist

def get_player(channel_id, name):
    global running_games

    if not is_game_playing(channel_id):
        return None
    
    player_1 = running_games[channel_id].player_1
    player_2 = running_games[channel_id].player_2
    
    if name == player_1.name:
        return player_1
    elif name == player_2.name:
        return player_2
    else:
        return None

def get_player_from_file(room_num):
    global data_dir

    def deck_reader(deck):
        cards = utils.list_reader(deck)
        cards = utils.int_list_parser(cards)
        return cards
    
    path_player = os.path.join(data_dir, room_num, 'player.csv')
    path_2pick = os.path.join(data_dir, room_num, '2pick.csv')
    path_deck_effect_1 = os.path.join(data_dir, room_num, 'deck_effect_1.csv')
    path_deck_effect_2 = os.path.join(data_dir, room_num, 'deck_effect_2.csv')
    
    content = fh.read(path_player)
    data_2pick = fh.read(path_2pick)
    deck_effect = [fh.read(path_deck_effect_1), fh.read(path_deck_effect_2)]
    player = [None, None]
    for i in range(2):
        player[i] = Player(int(content[i]['id']), content[i]['name'], int(content[i]['first']))
        player[i].has_kept = True if content[i]['has_kept'] == 'True' else False
        player[i].deck_pos = int(content[i]['deck_pos'])
        player[i].deck = deck_reader(content[i]['deck'])
        for info in deck_effect[i]:
            card = utils.int_parser(info['card'])
            player[i].deck_effect[card] = deck_reader(info['effect'])
    
    for i in range(2):
        id_2pick = int(data_2pick[i]['id'])
        for p in player:
            if p.id == id_2pick:
                check_list = {}
                check_list['craft_list'] = (utils.list_reader(data_2pick[i]['craft_list']))
                check_list['craft'] = utils.int_parser(data_2pick[i]['craft'].replace('[', '').replace(']',''))
                check_list['左'] = (utils.list_reader(data_2pick[i]['左']))
                check_list['右'] = (utils.list_reader(data_2pick[i]['右']))
                for key, values in check_list.items():
                    if values:
                        p.data['2pick_' + key] = values
    return player

def save_player_to_file(room_num, players):
    path_player = os.path.join(data_dir, room_num, 'player.csv')
    path_2pick = os.path.join(data_dir, room_num, '2pick.csv')
    path_deck_effect_1 = os.path.join(data_dir, room_num, 'deck_effect_1.csv')
    path_deck_effect_2 = os.path.join(data_dir, room_num, 'deck_effect_2.csv')
    path_deck_effect = [path_deck_effect_1, path_deck_effect_2]
    
    header = ['id', 'name', 'first', 'has_kept', 'deck_pos', 'deck']
    content = []
    for i in range(2):
        subcontent = {}
        player = players[i]
        subcontent['id'] = str(player.id)
        subcontent['name'] = player.name
        subcontent['first'] = '0' if player.first == '先手' else '1'
        subcontent['has_kept'] = str(player.has_kept)
        subcontent['deck_pos'] = str(player.deck_pos)
        subcontent['deck'] = str(player.deck)
        content.append(subcontent)
    fh.write(path_player, content, header)

    header = ['card', 'effect']
    for i in range(2):
        content = []
        for key, values in players[i].deck_effect.items():
            subcontent = {}
            subcontent['card'] = str(key)
            subcontent['effect'] = str(values)
            content.append(subcontent)
        fh.write(path_deck_effect[i], content, header)

    header = ['id', 'craft_list', 'craft', '左', '右']
    content = []
    for i in range(2):
        subcontent = {}
        player = players[i]
        subcontent['id'] = str(player.id)
        for x in header[1:]:
            subcontent[x] = str(player.data['2pick_' + x]) if ('2pick_' + x) in player.data else []
        content.append(subcontent)
    fh.write(path_2pick, content, header)

def get_game(channel_id):
    global running_games
    if not is_game_playing(channel_id):
        return None
    return running_games[channel_id]

def get_outdated_game():
    global running_games
    for key, values in running_games.items():
        diff = dt.datetime.now() + dt.timedelta(hours=8) - values.active_time
        if diff.days >= 3:
            return values
    return None

def delete_game(channel_id):
    global data_dir, running_games
    game = get_game(channel_id)
    if not game:
        return None

    deleted_channel = game.channel
    path = os.path.join(data_dir, game.room_num)
    del running_games[channel_id]
    if os.path.exists(path):
        shutil.rmtree(path, ignore_errors=True)

    save_running_games_to_file()
    return deleted_channel

def create_game(channel, player_1, player_2, mode='normal'):
    global running_games
    deleted_channel_id = None
    if is_game_playing(channel.id):
        return ('Error', '該頻道有其他正在進行的雲對戰')

    if len(running_games) >= 30:
        out = get_outdated_game()
        if not out:
            return ('Error', '有過多的雲對戰正在進行，請稍後再試')
        deleted_channel = delete_game(out.channel.id)
        if not deleted_channel:
            return ('Error', '刪除閒置對戰時發生錯誤')

    game = Game(channel, player_1, player_2, mode)
    running_games[channel.id] = game
    save_running_games_to_file()
    save_game_to_file(game)
    
    if deleted_channel_id:
        return ('Delete Old', (game, deleted_channel))
    return ('Correct', (game, game.channel))

def get_game_from_file(room_num, bot):
    global data_dir, running_games
    path = os.path.join(data_dir, room_num, 'game.csv')
    content = fh.read(path)[0]
    player = get_player_from_file(room_num)
    game = Game(bot.get_channel(int(content['channel_id'])), player[0], player[1])
    game.id = int(content['id'])
    game.room_num = room_num
    game.mode = content['mode']
    game.is_quitting = True if content['is_quitting'] == 'True' else False
    game.active_time = dt.datetime.strptime(content['active_time'], '%Y/%m/%d %H:%M:%S')
    game.save_time = dt.datetime.strptime(content['save_time'], '%Y/%m/%d %H:%M:%S')
    return game

def save_game_to_file(game):
    global data_dir
    game.save_time = dt.datetime.now() + dt.timedelta(hours=8)

    room_num = game.room_num
    path = os.path.join(data_dir, room_num)
    if not os.path.exists(path):
        os.mkdir(path)
    
    save_player_to_file(room_num, [game.player_1, game.player_2])
    header = ['id', 'mode', 'channel_id', 'is_quitting', 'active_time', 'save_time']
    content = []
    subcontent = {}
    subcontent['id'] = str(game.id)
    subcontent['mode'] = game.mode
    subcontent['channel_id'] = str(game.channel.id)
    subcontent['is_quitting'] = str(game.is_quitting)
    subcontent['active_time'] = game.active_time.strftime('%Y/%m/%d %H:%M:%S')
    subcontent['save_time'] = game.save_time.strftime('%Y/%m/%d %H:%M:%S')
    content.append(subcontent)

    path = os.path.join(path, 'game.csv')
    fh.write(path, content, header)

def get_running_games_from_file(bot):
    global running_games, data_dir
    path = os.path.join(data_dir, 'running_games.txt')
    content = fh.read(path)
    flag = False
    for room_num in content:
        if is_room_ready(room_num):
            game = get_game_from_file(room_num, bot)
            running_games[game.channel.id] = game
        else:
            flag = True            
    if flag:
        save_running_games_to_file()

def save_running_games_to_file():
    global running_games, data_dir
    path = os.path.join(data_dir, 'running_games.txt')
    content = []
    for key, values in running_games.items():
        content.append(values.room_num)
    fh.write(path, content)

def save_all_games_to_file():
    global running_games
    save_running_games_to_file()
    for key, values in running_games.items():
        save_game_to_file(values)
    return

###########
# game functions

# .battle name_1 name_2
def init_game(channel, name_1, name_2, mode='normal'):
    first = random.randint(0,1)

    player_1 = Player(1, name_1, first)
    player_2 = Player(2, name_2, 1 - first)

    status = create_game(channel, player_1, player_2, mode)
    if status[0] == 'Error':
        return status

    game = status[1][0]
    if mode == '2pick':
        game.player_1.deck_pos = 0
        game.player_2.deck_pos = 0
        game.player_1.deck = []
        game.player_2.deck = []
        status = (status[0], (status[1][0], status[1][1]), twopick.init_game(player_1, player_2))
        save_game_to_file(game)
    return status

# .keep name [cards]
def keep_cards(player, cards):
    if player.has_kept:
        return ('Error', '已經過了起手換牌階段')
    
    if cards[0] == 'none':
        player.deck = [i+1 for i in range(0, 40)]
        random.shuffle(player.deck)
        player.has_kept = True
        return ('Correct', player.deck[0:3])
    
    if cards[0] == 'all':
        player.has_kept = True
        return ('Correct', player.deck[0:3])
    
    id_list = utils.int_list_parser(cards, error=True)
    if not id_list:
        return ('Error', '卡片序號需為整數')

    new_deck = [i+1 for i in range(0, 40)]

    start_deck = player.deck[0:3]
    for id in id_list:
        if id in start_deck:
            start_deck.remove(id)
            new_deck.remove(id)
        else:
            return ('Error', '手牌中沒有你要保留的卡片')

    random.shuffle(new_deck)
    id_list.extend(new_deck)
    player.deck = id_list
    player.has_kept = True

    return ('Correct', player.deck[0:3])

#.choose name which
def choose(channel_id, player, choice):
    game = get_game(channel_id)
    if not game:
        return ('Error', '該頻道沒有正在進行的雲對戰。')

    item = f'{player.name} 已選擇 {choice}'
    if game.mode == '2pick':
        if '2pick_craft' not in player.data:
            item_list = player.data['2pick_craft_list']
            if choice not in item_list:
                return ('Error', '指定的項目不在清單中。')
            twopick.set_craft(player, choice)
            new_pick = twopick.give_pick(player, 1)
            item = f'{player.name} 第1輪：\n' + f'左：{new_pick[0]}\n' + f'右：{new_pick[1]}' 
        elif ('2pick_左' in player.data) and ('2pick_右' in player.data):
            item_list = ['左', '右']
            if choice not in item_list:
                return ('Error', '指定的項目不在清單中。')
            pick = player.data['2pick_' + choice]
            twopick.set_pick(player, pick)
            count = len(player.deck)
            if count < 30:
                new_pick = twopick.give_pick(player, (count // 2) + 1)
                item = f'{player.name} 第{player.data["2pick_turn"]}輪：\n' + f'左：{new_pick[0]}\n' + f'右：{new_pick[1]}' 
            else:
                del player.data['2pick_左']
                del player.data['2pick_右']
                item = f'{player.name} 選牌結束。'
        else:
            return ('Error', '已經過了選牌階段')
        save_game_to_file(game)
    return ('Correct', item)

# .draw name count
def draw_from_deck(player, count=1):
    count = utils.int_parser(count, True)
    if (not count) or (count < 0):
        return ('Error', '抽牌數量要正整數')

    pos = player.deck_pos
    deck_left = len(player.deck) - pos - count
    if deck_left < 0:
        player.deck_pos = len(player.deck)
        return ('Deck Out', player.deck[pos : ])
    
    player.deck_pos += count
    return (f'Correct', player.deck[pos : pos + count])

# .search count [cards]
def search_from_deck(player, count, cards):
    if '張' not in count:
        return ('Error', '檢索數量需寫"X張"，例如：8張')
    
    count = count.replace('張', '')
    count = utils.int_parser(count, error=True)

    if count <= 0:
        return ('Error', '檢索數量必須為正整數')

    card_list = utils.int_list_parser(cards)
    
    filt_list = list(filter(lambda x: x in player.deck[player.deck_pos:], card_list))
    result_list = random.sample(filt_list, min(len(filt_list), count))

    player.deck.reverse()
    for result in result_list:
        player.deck.remove(result)
    player.deck.reverse()

    return ('Correct', result_list)

# .explore name
def explore_from_deck(player, count=1):
    pos = player.deck_pos
    result = [] if pos >= len(player.deck) else player.deck[pos : min(pos + count, len(player.deck))]
    return ('Correct', result)

# .add name [cards]
def add_deck(player, cards):
    add_deck = utils.int_list_parser(cards)
    
    old_deck = player.deck[0 : player.deck_pos]
    
    new_deck = player.deck[player.deck_pos:]
    new_deck.extend(add_deck)
    random.shuffle(new_deck)

    old_deck.extend(new_deck)
    player.deck = old_deck
    return ('Correct', new_deck)

# .substitute name [cards]
def substitute_deck(player, cards):
    sub_deck = utils.int_list_parser(cards)
    player.deck = sub_deck
    random.shuffle(player.deck)
    player.deck_pos = 0
    return ('Correct', player.deck)

# .effect name mode effect [cards]
def modify_deck_effect(player, mode, effect, cards):
    card_list = utils.int_list_parser(cards)
    
    filt_list = list(filter(lambda x: x in player.deck[player.deck_pos:], card_list))
    if mode == 'add':
        for card in filt_list:
            if card in player.deck_effect:
                player.deck_effect[card].append(effect)
            else:
                player.deck_effect[card] = [effect]
    elif mode == 'delete':
        for card in filt_list:
            if (card in player.deck_effect):
                if effect in player.deck_effect[card]:
                    player.deck_effect[card].remove(effect)
    elif mode == 'substitute':
        for card in filt_list:
            player.deck_effect[card] = [effect]
    else:
        return ('Error', '改變牌堆資訊沒有此項模式')

    return ('Correct', mode)

def portal(name, option='name'):
    return cm.search_card(name, option)

def travel(condition):
    return portal(condition, 'travel')

def save_game(channel_id):
    global running_games
    if not is_game_playing(channel_id):
        return ('Error', '該頻道沒有正在進行的雲對戰')

    save_game_to_file(running_games[channel_id])
    return ('Correct', running_games[channel_id])

# .quit
def quit_game(channel_id):
    global running_games

    if not is_game_playing(channel_id):
        return ('Error', '該頻道沒有正在進行的雲對戰')

    channel = delete_game(channel_id)
    if not channel:
        return ('Error', '結束對戰時發生錯誤')

    return ('Correct', channel)