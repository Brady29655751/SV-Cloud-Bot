import discord
import random
import datetime as dt

#############
# global variable

running_games = {}

#############
# utility

class Game:
    def __init__(self, channel, first, second):
        global running_games
        self.id = len(running_games)
        self.room_num = str(10000 + self.id * 3000 + random.randrange(1, 3000)) 
        self.channel = channel
        self.is_quitting = False
        self.player_1 = first
        self.player_2 = second
        self.active_time = dt.datetime.now() + dt.timedelta(hours=8)

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

def is_game_playing(channel_id):
    global running_games
    playing =  channel_id in running_games
    if playing:
        running_games[channel_id].active_time = dt.datetime.now() + dt.timedelta(hours=8)
    return playing

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

###########
# game functions

# .battle name_1 name_2
def init_game(channel, name_1, name_2):
    global running_games

    first = random.randint(0,1)

    player_1 = Player(1, name_1, first)
    player_2 = Player(2, name_2, 1 - first)

    game = None
    id = len(running_games)
    if id < 30:
        if is_game_playing(channel.id):
            return ('Error', '該頻道有其他正在進行的雲對戰')
        
        game = Game(channel, player_1, player_2)
        running_games[channel.id] = game
    else:
        deleted_channel = None
        deleted_room = None
        for key, values in running_games.items():
            diff = dt.datetime.now() - values.active_time
            if diff.days >= 3:
                deleted_channel = values.channel
                deleted_room = (values.id, values.room_num)
                break
        
        if (deleted_channel != None) and (deleted_room != None):
            deleted_key = deleted_channel.id
            del running_games[deleted_key]
            game = Game(channel, player_1, player_2)
            game.id = deleted_room[0]
            game.room_num = deleted_room[1]
            running_games[channel.id] = game
            return ('Delete Old', (game, deleted_channel))
        else:
            return ('Error', '有過多的雲對戰正在進行，請稍後再試')

    return ('Correct', (game, game.channel))

# .keep name [cards]
def keep_cards(player, cards):
    if player.has_kept:
        return ('Error', '已經過了起手換牌階段')
    
    if cards[0] == 'none':
        player.deck = [i+1 for i in range(0, 40)]
        random.shuffle(player.deck)
        player.has_kept = True
        return ('Correct', player.deck[0:3])
    
    id_list = cards
    try:
        id_list = [int(x) for x in cards]
    except Exception:
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

# .draw name count
def draw_from_deck(player, count=1):
    try:
        count = int(count)
    except Exception:
        return ('Error', '抽牌數量要正整數')
    
    if count <= 0:
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
    try:
        count = int(count)
    except Exception:
        return ('Error', '檢索數量需寫"X張"，例如：8張')

    if count <= 0:
        return ('Error', '檢索數量必須為正整數')

    card_list = cards[:]
    for i, card in enumerate(cards):
        try:   
            id = int(card)
            card_list[i] = id
        except Exception:
            id = card
    
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
    add_deck = cards[:]
    for i, card in enumerate(cards):
        try:
            id = int(card)
            add_deck[i] = id
        except Exception:
            id = card
    
    old_deck = player.deck[0 : player.deck_pos]
    
    new_deck = player.deck[player.deck_pos:]
    new_deck.extend(add_deck)
    random.shuffle(new_deck)

    old_deck.extend(new_deck)
    player.deck = old_deck
    return ('Correct', new_deck)

# .substitute name [cards]
def substitute_deck(player, cards):
    sub_deck = cards[:]
    for i, card in enumerate(cards):
        try:
            id = int(card)
            sub_deck[i] = id
        except:
            id = card
    
    player.deck = sub_deck
    random.shuffle(player.deck)
    player.deck_pos = 0
    return ('Correct', player.deck)

# .effect name mode effect [cards]
def modify_deck_effect(player, mode, effect, cards):
    card_list = cards[:]
    for i, card in enumerate(cards):
        try:
            id = int(card)
            card_list[i] = id
        except:
            id = card
    
    filt_list = list(filter(lambda x: x in player.deck[player.deck_pos:], card_list))
    effect = effect + ' '
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

# .quit
def quit_game(room_num):
    global running_games

    if not is_game_playing(room_num):
        return ('Error', '該頻道沒有正在進行的雲對戰')

    game = running_games[room_num]
    game.player_1 = None
    game.player_2 = None
    game.is_quitting = False
    del running_games[room_num]
    return ('Correct', room_num)