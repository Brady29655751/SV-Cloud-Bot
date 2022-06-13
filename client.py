import discord
import random
import datetime as dt
import game as sv

########
# lazy functions

def is_game_playing(channel_id):
    return sv.is_game_playing(channel_id)

def get_player(channel_id, name):
    return sv.get_player(channel_id, name)

def get_card_effect(player, card_list):
    info = ''
    for card in card_list:
        if card in player.deck_effect:
            info += f'{card}：{player.deck_effect[card]}\n'
    return info

########
# client function. send message to channel.

async def battle(content, channel):
    players = content.split()
    if len(players) != 3:
        await channel.send('對戰人數不是2位')
        return
    await channel.send('バトル！シャドバース！')
    
    status = sv.init_game(channel, players[1], players[2])
    if (status[0] == 'Correct') or (status[0] == 'Delete Old'):
        room_num = status[1][0].room_num
        player_1 = status[1][0].player_1
        player_2 = status[1][0].player_2

        await channel.send(f'對戰房號：{room_num}')
        await channel.send(f'{player_1.name}：{player_1.first}。{player_2.name}：{player_2.first}。')
        await channel.send(f'{player_1.name}的起手：{player_1.deck[0:3]}')
        await channel.send(f'{player_2.name}的起手：{player_2.deck[0:3]}')

        if status[0] == 'Delete Old':
            deleted_channel = status[1][1]
            await deleted_channel.send(f'**【系統公告】**\n' + '\t該對戰已閒置過久。系統自動刪除該頻道的對戰。')

    elif status[0] == 'Error':
        await channel.send(status[1])
    else:
        await channel.send('創建對戰時遇到未知錯誤')

async def dice(content, channel):
    msg = content.replace('.dice', '')
    msg = msg.split('d')
    if len(msg) != 2:
        await channel.send('擲骰格式錯誤')
        return

    times = msg[0]
    dice = msg[1]
    try:
        times = int(times)
        dice = int(dice)
    except Exception:
        await channel.send('擲骰次數與範圍需為正整數')
        return

    if times <= 0 or dice <= 0:
        await channel.send('擲骰次數與範圍需為正整數')
        return

    if times > 100 or dice > 100_0000:
        await channel.send('擲骰次數請不要超過100次。擲骰範圍請不要超過100萬。')
        return

    result = []
    for i in range(times):
        rng = random.randrange(dice) + 1
        result.append(rng)
    
    if times == 1:
        await channel.send(f'{times}d{dice}：{result[0]}')
    else:
        await channel.send(f'{times}d{dice}：{result}')

async def players(content, channel):
    if not is_game_playing(channel.id):
        await channel.send('該頻道沒有正在進行的雲對戰')
        return
    
    game = sv.running_games[channel.id]
    player_1 = game.player_1
    player_2 = game.player_2

    await channel.send(f'房間號碼：{game.room_num}')
    if player_1.first == '先手':
        await channel.send(f'先手玩家：{player_1.name}。後手玩家：{player_2.name}')
    else:
        await channel.send(f'先手玩家：{player_2.name}。後手玩家：{player_1.name}')

async def deck_info(content, channel):
    if not is_game_playing(channel.id):
        await channel.send('該頻道沒有正在進行的雲對戰')
        return

    msg = content.split()
    if len(msg) != 3:
        await channel.send('查看牌組資訊格式錯誤')
        return

    name = msg[1]
    cmd = msg[2]
    player = get_player(channel.id, name)

    if cmd == 'count':
        await channel.send(f'{player.name}的牌堆有 {len(player.deck) - player.deck_pos} 張卡片。')
    elif cmd == 'show':
        await channel.send(f'{player.name}的牌堆為：{player.deck[player.deck_pos:]}')
        await channel.send(f'總計 {len(player.deck) - player.deck_pos} 張。')
    elif cmd == 'used':
        await channel.send(f'{player.name}已抽取的卡片為：{player.deck[0:player.deck_pos]}')
        await channel.send(f'總計 {player.deck_pos} 張。')
    else:
        await channel.send(f'沒有此項指令。')
    
async def keep(content, channel):
    if not is_game_playing(channel.id):
        await channel.send('該頻道沒有正在進行的雲對戰')
        return

    msg = content.split()
    length = len(msg)
    if (length < 3) or (length > 5):
        await channel.send('留牌格式錯誤')
        return

    name = msg[1]
    cards = msg[2:]
    player = get_player(channel.id, name)
    if player == None:
        await channel.send('名字寫錯')
        return

    status = sv.keep_cards(player, cards)
    if status[0] == 'Correct':
        await channel.send(f'{player.name}換完牌之後的起手：{status[1]}')
    elif status[0] == 'Error':
        await channel.send(status[1])
    else:
        await channel.send('留牌時遇到未知錯誤')

async def draw(content, channel):
    if not is_game_playing(channel.id):
        await channel.send('該頻道沒有正在進行的雲對戰')
        return

    msg = content.split()
    if len(msg) != 2 and len(msg) != 3:
        await channel.send('抽牌格式錯誤')
        return

    name = msg[1]
    player = get_player(channel.id, name)
    if player == None:
        await channel.send('名字寫錯')
        return

    count = 1
    if len(msg) == 3:
        try:
            count = int(msg[2])
        except Exception:
            await channel.send('抽取數量需為正整數')
            return
    
    if count <= 0:
        await channel.send('抽取數量需為正整數')
        return

    status = sv.draw_from_deck(player, count)
    if status[0] == 'Correct':
        await channel.send(f'{player.name}抽{count}張卡：{status[1]}')
        
        info = get_card_effect(player, status[1])
        if info:
            await channel.send(f'{info}')

    elif status[0] == 'Deck Out':
        await channel.send(f'{player.name}抽{count}張卡：{status[1]}')
        
        info = get_card_effect(player, status[1])
        if info:
            await channel.send(f'{info}')

        await channel.send(f'牌堆已抽乾～結算勝敗吧！')
    elif status[0] == 'Error':
        await channel.send(f'{status[1]}')
    else:
        await channel.send('抽牌時遇到未知錯誤')

async def search(content, channel):
    if not is_game_playing(channel.id):
        await channel.send('該頻道沒有正在進行的雲對戰')
        return

    msg = content.split()
    if len(msg) < 4:
        await channel.send('檢索格式錯誤')
        return

    name = msg[1]
    condition = msg[2]
    cards = msg[3:]
    player = get_player(channel.id, name)
    if player == None:
        await channel.send('名字寫錯')
        return

    status = sv.search_from_deck(player, condition, cards)
    if status[0] == 'Correct':
        info = get_card_effect(player, status[1])
        await channel.send(f'{player.name}檢索{len(status[1])}張卡：{status[1]}')

        if info:
            await channel.send(f'{info}')
    elif status[0] == 'Error':
        await channel.send(f'{status[1]}')
    else:
        await channel.send('檢索時遇到未知錯誤')

async def explore(content, channel):
    if not is_game_playing(channel.id):
        await channel.send('該頻道沒有正在進行的雲對戰')
        return

    msg = content.split()
    if len(msg) != 2 and len(msg) != 3:
        await channel.send('探索格式錯誤')
        return

    name = msg[1]
    player = get_player(channel.id, name)
    if player == None:
        await channel.send('名字寫錯')
        return

    count = 1
    if len(msg) == 3:
        try:
            count = int(msg[2])
        except Exception:
            await channel.send('探索數量需為正整數。')
            return
    
    if count <= 0:
        await channel.send('探索數量需為正整數。')
        return

    status = sv.explore_from_deck(player, count)
    if status[0] == 'Correct':
        result = status[1][0] if len(status[1]) == 1 else status[1]
        info = get_card_effect(player, status[1])

        await channel.send(f'{player.name}的牌堆頂部{len(status[1])}張卡是：{result}')
        if info:
            await channel.send(f'{info}')

    elif status[0] == 'Error':
        await channel.send(f'{status[1]}')
    else:
        await channel.send('探索時遇到未知錯誤')

async def add(content, channel):
    if not is_game_playing(channel.id):
        await channel.send('該頻道沒有正在進行的雲對戰')
        return

    msg = content.split()
    if len(msg) < 3:
        await channel.send('塞牌格式錯誤')
        return

    name = msg[1]
    cards = msg[2:]
    player = get_player(channel.id, name)
    if player == None:
        await channel.send('名字寫錯')
        return

    status = sv.add_deck(player, cards)
    if status[0] == 'Correct':
        await channel.send(f'{player.name}已新增下列卡片進入牌堆：{cards}')
    elif status[0] == 'Error':
        await channel.send(f'{status[1]}')
    else:
        await channel.send('塞牌時遇到未知錯誤')
    
async def substitute_deck(content, channel):
    if not is_game_playing(channel.id):
        await channel.send('沒有正在進行中的對戰！')
        return

    msg = content.split()
    if len(msg) < 3:
        await channel.send('置換牌堆格式錯誤')
        return

    name = msg[1]
    cards = msg[2:]
    player = get_player(channel.id, name)
    if player == None:
        await channel.send('名字寫錯')
        return

    status = sv.substitute_deck(player, cards)
    if status[0] == 'Correct':
        await channel.send(f'{player.name}的牌堆已轉變為下列卡片：{cards}')
    elif status[0] == 'Error':
        await channel.send(f'{status[1]}')
    else:
        await channel.send('置換牌堆時遇到未知錯誤')

async def modify_deck_effect(content, channel):
    if not is_game_playing(channel.id):
        await channel.send('沒有正在進行中的對戰！')
        return
    
    msg = content.split()
    if len(msg) < 5:
        await channel.send('改變牌堆資訊格式錯誤')
        return
    
    name = msg[1]
    mode = msg[2]
    effect = msg[3]
    cards = msg[4:]
    player = get_player(channel.id, name)
    if player == None:
        await channel.send('名字寫錯')
        return
    
    description = {'add': '新增', 'delete': '刪除', 'substitute': '置換'}
    status = sv.modify_deck_effect(player, mode, effect, cards)
    if status[0] == 'Correct':
        await channel.send(f'{player.name}牌堆中的指定卡片已{description[mode]}下列資訊：{effect}')
    elif status[0] == 'Error':
        await channel.send(f'{status[1]}')
    else:
        await channel.send('改變牌堆資訊時遇到未知錯誤')
    

async def quit(content, channel, bot=None):
    room_num = channel.id

    if not is_game_playing(room_num):
        await channel.send('該頻道沒有正在進行的雲對戰')
        return
    
    game = sv.running_games[room_num]

    if game.is_quitting:
        await channel.send(f'請回復".quit yes"以確認結束對戰。')
        return
    
    if (not game.is_quitting) and (bot != None):
        game.is_quitting = True
        await channel.send(f'請回復".quit yes"以確認結束對戰。')
        msg = await bot.wait_for('message', check = lambda x: x.content == '.quit yes' and x.channel == channel)
        if msg.content == '.quit yes':
            sv.quit_game(channel.id)
            await channel.send('The battle fucked up.')
            return

async def help(content, channel):
    msg = content.split()

    if len(msg) == 1:
        await channel.send('歡迎使用SV Cloud！')
        await channel.send('請輸入 ".help 指令" 來查看各項指令用途！')
        await channel.send('目前的指令有：\n' +
            '1. battle\n' +
            '2. dice\n' +
            '3. player\n' +
            '4. deck\n' +
            '5. keep\n' +
            '6. draw\n' +
            '7. search\n' +
            '8. explore\n' +
            '9. add\n' +
            '10. substitute\n' +
            '11. effect\n' +
            '12. quit')
    elif len(msg) == 2:
        if msg[1] == 'battle':
            await channel.send('指令格式：.battle 玩家1名字 玩家2名字')
            await channel.send('指令範例：.battle 頭痛鯊 資工鯊')
            await channel.send('指令說明：開啟一場兩人的雲對戰。目前此Bot最多只能同時進行30場對戰。\n' + 
                '\t※ 注意：Bot可能會因為突發狀況或維護需要而導致數據損失或遭到刪除。')
        elif msg[1] == 'dice':
            await channel.send('指令格式：.dice 次數d範圍')
            await channel.send('指令範例：.dice 2d6')
            await channel.send('指令說明：骰子。次數不能超過100、範圍不能超過100萬。')
        elif msg[1] == 'player':
            await channel.send('指令格式：.player')
            await channel.send('指令範例：.player')
            await channel.send('指令說明：查看該頻道正在進行雲對戰的玩家。')
        elif msg[1] == 'deck':
            await channel.send('指令格式：.deck 玩家名字 count/show/used')
            await channel.send('指令範例：.deck 頭痛鯊 show')
            await channel.send('指令說明：\n' +
                '\tcount會查看該玩家牌堆中的卡片張數。\n' +
                '\tshow會完整查看該玩家的牌堆。\n' +
                '\tused會查看該玩家已抽取的卡片。')
        elif msg[1] == 'keep':
            await channel.send('指令格式：.keep 玩家名字 卡片序號1 (卡片序號2) (卡片序號3)')
            await channel.send('指令範例：.keep 頭痛鯊 23 35')
            await channel.send('指令說明：起手留牌。輸入的卡片序號是**【要保留的牌】**。卡片序號1若輸入none則會全換。')
        elif msg[1] == 'draw':
            await channel.send('指令格式：.draw 玩家名字 (數量)')
            await channel.send('指令範例：.draw 頭痛鯊 2')
            await channel.send('指令說明：由該玩家的牌堆中抽取指定數量的卡片。未填寫數量則默認為1。')
        elif msg[1] == 'search':
            await channel.send('指令格式：.search 玩家名字 數量+"張" 檢索範圍')
            await channel.send('指令範例：.search 頭痛鯊 2張 4 5 6 10 11 12 R0 R1 R2')
            await channel.send('指令說明：由該玩家的牌堆中檢索指定範圍內的卡片。\n' +
                '\t※ 若該玩家的牌堆沒有檢索範圍所聲稱的卡片，則不會抽取該卡片。使用此項指令請仔細確認檢索範圍有沒有寫錯。\n' +
                '\t※ Ex: 若頭痛鯊的牌堆沒有R0, R1, R2，則上述指令只會從 4, 5, 6, 10, 11, 12 之中，隨機檢索2張。')
        elif msg[1] == 'explore':
            await channel.send('指令格式：.explore 玩家名字 (數量)')
            await channel.send('指令範例：.explore 頭痛鯊')
            await channel.send('指令說明：探索。查看該玩家牌堆頂部指定數量的卡片。未填寫數量則默認為1。')
        elif msg[1] == 'add':
            await channel.send('指令格式：.add 玩家名字 新增卡片1 (新增卡片2) (新增卡片3) ...')
            await channel.send('指令範例：.add 頭痛鯊 41 R7 R8 42 43 R9')
            await channel.send('指令說明：增加指定的卡片到該玩家的牌堆中，隨後進行1次洗牌。')
        elif msg[1] == 'substitute':
            await channel.send('指令格式：.substitute 玩家名字 置換卡片1 (置換卡片2) (置換卡片3) ...')
            await channel.send('指令範例：.substitute 頭痛鯊 41 R7 R8 42 43 R9')
            await channel.send('指令說明：使該玩家牌堆中的卡片轉變為指定的卡片，隨後進行1次洗牌。\n' +
                '\t※ Ex: 上述指令會使頭痛鯊牌堆中的卡片轉變為 41, 42, 43, R7, R8, R9（順序隨機）')
        elif msg[1] == 'effect':
            await channel.send('指令格式：.effect 玩家名字 add/delete/substitute 效果 牌堆卡片1 (牌堆卡片2) (牌堆卡片3) ...')
            await channel.send('指令範例：.effect 頭痛鯊 add 增幅+1 R6')
            await channel.send('指令說明：為該玩家牌堆中的指定卡片新增/刪除/置換資訊。\n' +
                '\t※ Ex: 上述指令會使頭痛鯊牌堆中的R6卡片新增【增幅+1】資訊。')
        elif msg[1] == 'quit':
            await channel.send('指令格式：.quit')
            await channel.send('指令範例：.quit')
            await channel.send('指令說明：結束該頻道的對戰。Bot會再要求你輸入.quit yes以確認結束對戰。')
        else:
            await channel.send('未發現此項指令。')
    else:
        await channel.send('help指令格式錯誤')