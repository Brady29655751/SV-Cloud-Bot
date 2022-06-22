import discord
import random
import datetime as dt
import game as sv
import utility as utils

#######
# global

filter_result = None
repeat_message = [0, None]

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

async def idle(content, channel):
    await repeat(content, channel)

async def repeat(content, channel):
    global repeat_message
    msg = content
    if repeat_message[1] != msg:
        repeat_message = [1, msg]
    else:
        repeat_message[0] += 1
        if repeat_message[0] == 3:
            await channel.send(msg)
            return

async def repeat_after_me(content, channel):
    msg = content.split()
    if msg[0] == '.me':
        await channel.send(content.strip('.me '))
    return

async def prepare_battle(content, channel):
    players = content.split()
    if (len(players) != 3):
        await channel.send('對戰人數不是2位')
        return

    await channel.send('バトル！シャドバース！')

    mode = 'normal'
    if players[0].startswith('.2pick'):
        mode = '2pick'

    status = sv.init_game(channel, players[1], players[2], mode)
    if (status[0] == 'Correct') or (status[0] == 'Delete Old'):
        room_num = status[1][0].room_num
        player_1 = status[1][0].player_1
        player_2 = status[1][0].player_2

        await channel.send(f'對戰房號：{room_num}')
        if mode == 'normal':
            await channel.send(f'{player_1.name}：{player_1.first}。{player_2.name}：{player_2.first}。')
            await channel.send(f'{player_1.name}的起手：{player_1.deck[0:3]}')
            await channel.send(f'{player_2.name}的起手：{player_2.deck[0:3]}')
        elif mode == '2pick':
            await channel.send(f'{player_1.name} 請選擇職業：{status[2][0]}')
            await channel.send(f'{player_2.name} 請選擇職業：{status[2][1]}')

        if status[0] == 'Delete Old':
            deleted_channel = status[1][1]
            await deleted_channel.send(f'**【系統公告】**\n' + '\t該對戰已閒置過久。系統自動刪除該頻道的對戰。')
    elif status[0] == 'Error':
        await channel.send(status[1])
    else:
        await channel.send('創建對戰時遇到未知錯誤')

async def battle_cmd(content, channel, game):
    msg = content.split()
    if len(msg) != 2:
        await channel.send('對戰指令格式錯誤')
        return
    cmd = msg[1]
    mode = game.mode
    player_1 = game.player_1
    player_2 = game.player_2
    if mode == 'normal':
        await channel.send('該頻道有其他正在進行的雲對戰。')
        return
    elif mode == '2pick':
        if cmd == 'ready':
            first_deck_ready = len(player_1.deck) == 30
            second_deck_ready = len(player_2.deck) == 30
            deck_ready = first_deck_ready and second_deck_ready
            is_init = player_1.deck_pos == 0 and player_2.deck_pos == 0
            if deck_ready and is_init:
                save_game_to_file(game.channel.id)
                await channel.send(f'房號：{game.room_num}')
                await channel.send(f'{player_1.name}：{player_1.first}。' + 
                    f'{player_2.name}：{player_2.first}。')
                await channel.send('對戰開始。請雙方使用draw指令抽取3張卡片，並進行換牌。')
                return
            else:
                if not is_init:
                    await channel.send('2pick對戰已經開始，不可使用ready指令。')
                    return
                if not deck_ready:
                    who = '雙方都'
                    if first_deck_ready and (not second_deck_ready):
                        who = f'{player_2.name}'
                    elif (not first_deck_ready) and second_deck_ready:
                        who = f'{player_1.name}'
                    await channel.send(f'{who}尚未完成選牌。')
                    return
    return

async def battle(content, channel):
    game = sv.get_game(channel.id)
    if not game:
        await prepare_battle(content, channel)
    else:
        await battle_cmd(content, channel, game)


async def dice(content, channel):
    msg = content.replace('.dice', '')
    msg = msg.split('d') if 'd' in msg else msg.split('D')
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

async def game_info(content, channel):
    if not is_game_playing(channel.id):
        await channel.send('該頻道沒有正在進行的雲對戰')
        return
    
    game = sv.running_games[channel.id]
    player_1 = game.player_1
    player_2 = game.player_2

    last_save_time = game.save_time.strftime('%Y/%m/%d %H:%M:%S')
    await channel.send(f'數據儲存時間：{last_save_time}')
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

async def choose(content, channel):
    game = sv.get_game(channel.id)
    if not game:
        await channel.send('該頻道沒有正在進行的雲對戰')
        return

    msg = content.split()
    if len(msg) < 3:
        await channel.send('選擇格式錯誤')
        return

    name = msg[1]
    choice = msg[2]
    player = get_player(channel.id, name)
    if player == None:
        await channel.send('名字寫錯')
        return
    
    status = sv.choose(channel.id, player, choice)
    if status[0] == 'Correct':
        await channel.send(status[1])
    elif status[0] == 'Error':
        await channel.send(status[1])
    else:
        await channel.send('選擇時遇到未知錯誤')


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

async def portal(content, channel):
    msg = content.split()
    if len(msg) < 2:
        await channel.send('查詢卡片格式錯誤')
        return

    card = None
    if msg[1] == 'random':
        if len(msg) == 2:
            card = sv.portal(1, 'random')    
        else:
            count = utils.int_parser(msg[2])
            if count <= 0 or count > 20:
                await channel.send('隨機數量需為1到20之間')
                return
            
            card = sv.portal(count, 'random')
    elif msg[1] == 'travel':
        if len(msg) == 2:
            card = sv.portal('all', 'travel')
        else:
            card = sv.portal(msg[2:], 'travel')
    elif msg[1] == 'filter':
        global filter_result
        if len(msg) == 2:
            await channel.send('需指定搜索條件。')
        elif len(msg) == 3:
            if msg[2] in ['back', 'next']:
                if not filter_result:
                    await channel.send('沒有超過50張卡的搜索紀錄。')
                else:
                    page = filter_result[0]
                    if msg[2] == 'back':
                        if page == 0:
                            await channel.send('沒有上一頁了。')
                            return
                        else:
                            page -= 1
                    elif msg[2] == 'next':
                        if filter_result[0] == (len(filter_result[1]) - 1) // 50:
                            await channel.send('沒有下一頁了。')
                            return
                        else:
                            page += 1
                    filter_result[0] = page
                    start = 50 * page 
                    stop = min(50 * (page + 1), len(filter_result[1]))
                    await channel.send(f'【第{page+1}頁】(總計 {len(filter_result[1])} 張)：\n{filter_result[1][start:stop]}')
            else:
                await channel.send('搜尋指令格式錯誤。')
        else:
            card = sv.portal(msg[2:], 'filter')
            card_name = [x.name for x in card]
            if len(card) <= 50:
                await channel.send(f'符合條件的卡片如下，總共 {len(card_name)} 張：\n{card_name}')
            else:
                filter_result = [0, card_name]
                await channel.send(f'符合條件的卡片總共 {len(card_name)} 張，僅顯示前50張。\n' + 
                    '請使用.filter back或.filter next以查看上一頁/下一頁\n' +
                    f'第1頁：\n{card_name[0:50]}')
        return
    else:
        name = utils.concate_content_with_character(msg[1:], ' ')
        count = utils.int_parser(name, error=True)
        if count > 100_000_000:
            card = sv.portal(count, 'id')
        else:
            card = sv.portal(name)
    
    if not card:
        await channel.send('未發現該卡片')
        return
    
    if isinstance(card, list):
        if msg[1] == 'random':
            await channel.send(f'隨機結果：{card}')
        else:
            if len(card) > 20:
                await channel.send('搜尋結果超過20張，建議縮小搜尋範圍。\n')
                await channel.send(f'搜尋結果（僅顯示前20張）：\n{card[0:21]}')
            else:
                await channel.send(f'搜尋結果：\n{card}')
        return

    card_info = [card.name]
    card_info.append(f'消費 {card.cost}｜{card.craft_name}｜{card.rarity_name}｜{card.type_name}｜{card.trait_name}')
    if card.type == 1:
        card_info.append(f'進化前（{card.atk} / {card.life}）')
        card_info.append(f'```{card.effect}```')
        card_info.append(f'進化後（{card.evo_atk} / {card.evo_life}）')
        card_info.append(f'```{card.evo_effect}```')
    else:
        card_info.append(f'```{card.effect}```')

    card_info.append(f'卡包：《{card.pack_name}》')
    if not card.is_normal():
        card_info.append(f'※這張卡片為特殊卡。')
    card_info = utils.concate_content_with_newline(card_info)
    await channel.send(f'{card_info}')

async def travel(content, channel):
    msg = content.split()
    if len(msg) == 1:
        await portal('.portal travel', channel)
        return
    else:
        if msg[1] == 'all':
            await portal('.portal travel', channel)
        else:
            target = utils.concate_content_with_character(msg[1:], ' ')
            await portal('.portal travel ' + target, channel)
        return

async def filter_portal(content, channel):
    msg = content.split()
    target = utils.concate_content_with_character(msg[1:], ' ')
    await portal('.portal filter ' + target, channel)
    return

async def save(content, channel):
    status = sv.save_game(channel.id)
    if status[0] == 'Correct':
        await channel.send(f'已儲存對戰數據。\n' + 
            f'儲存時間：{status[1].save_time.strftime("%Y/%m/%d %H:%M:%S")}')
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
            '2. 2pick\n' +
            '3. portal\n' +
            '4. travel\n' +
            '5. filter\n' +
            '6. dice\n' +
            '7. player\n' +
            '8. deck\n' +
            '9. choose\n' +
            '10. keep\n' +
            '11. draw\n' +
            '12. search\n' +
            '13. explore\n' +
            '14. add\n' +
            '15. substitute\n' +
            '16. effect\n' +
            '17. save\n' +
            '18. quit')
    elif len(msg) == 2:
        if msg[1] == 'battle':
            await channel.send('指令格式：.battle 玩家1名字 玩家2名字')
            await channel.send('指令範例：.battle 頭痛鯊 資工鯊')
            await channel.send('指令說明：開啟一場兩人的雲對戰。目前此Bot最多只能同時進行30場對戰。\n' + 
                '\t※ 注意：Bot可能會因為突發狀況或維護需要而導致數據損失或遭到刪除。')
        elif msg[1] == '2pick':
            await channel.send('指令格式：.2pick 玩家1名字 玩家2名字')
            await channel.send('指令範例：.2pick 頭痛鯊 資工鯊')
            await channel.send('指令說明：開啟一場兩人的雲對戰【2pick模式】。請搭配choose指令來選牌。\n' + 
                '\t※選完牌之後，輸入.2pick ready即可開始對戰。')
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
        elif msg[1] == 'choose':
            await channel.send('指令格式：.choose 玩家名字 選擇')
            await channel.send('指令範例：.choose 頭痛鯊 左')
            await channel.send('指令說明：選擇對應的選項。\n' + 
                '\t※ 此功能目前只適用於2pick模式選牌。')
        elif msg[1] == 'keep':
            await channel.send('指令格式：.keep 玩家名字 卡片序號1 (卡片序號2) (卡片序號3)')
            await channel.send('指令範例：.keep 頭痛鯊 23 35')
            await channel.send('指令說明：起手留牌。輸入的卡片序號是**【要保留的牌】**。\n' + 
                '\t※ 卡片序號1若輸入none則會**【三張全換】**。\n' +
                '\t※ 卡片序號1若輸入all則會**【全部保留】**。')
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
        elif msg[1] == 'portal':
            await channel.send('指令格式：.portal 要查詢的卡片')
            await channel.send('指令範例：.portal 水之妖精')
            await channel.send('指令說明：顯示該卡片的詳細資訊。目前只能查詢至《虛實境界》卡包。\n' +
                '\t※ 要查詢的卡片可填入卡片id，此時portal會依照該id搜尋對應卡片。\n' + 
                '\t※ 要查詢的卡片若填入random，則會指定數量隨機搜尋卡片。未填寫數量則默認為1。\n' + 
                '\t※ 要查詢的卡片若填入travel，則會將此指令視作travel指令。\n' +
                '\t※ 要查詢的卡片若填入filter，則會將此指令視作filter指令。')
        elif msg[1] == 'travel':
            await channel.send('指令格式：.travel (條件式1) and/or (條件式2) and/or ...')
            await channel.send('指令範例：.travel cost > 3 and type = 從者')
            await channel.send('指令說明：漫遊。從官方卡片以外的卡片資料庫中，隨機搜尋1張符合指定條件的卡片。\n' +
                '\t※ 條件式格式：標籤 大於/小於/等於 目標。中間需要空格。\n' + 
                '\t※ 標籤：id, name, pack, class, rarity, type, trait, cost, atk, life, evoAtk, evoLife, \n' +
                '\t\tcountdown, ability, effect, evoEffect, author, token_id, image_url, mode\n' + 
                '\t※ 若不填入任何條件，則默認全部隨機。')
        elif msg[1] == 'filter':
            await channel.send('指令格式：.filter (條件式1) and/or (條件式2) and/or ...')
            await channel.send('指令範例：.filter cost > 3 and type = 從者')
            await channel.send('指令說明：從卡片資料庫中搜索所有符合指定條件的卡片。\n' +
                '\t※ 條件式格式：標籤 大於/小於/等於 目標。中間需要空格。\n' + 
                '\t※ 標籤：id, name, pack, class, rarity, type, trait, cost, atk, life, evoAtk, evoLife, \n' +
                '\t\tcountdown, ability, effect, evoEffect, author, token_id, image_url, mode\n' + 
                '\t※ 在搜尋結果過多時，條件式1 若填入 back 或 next 可查看上一頁或下一頁。')    
        elif msg[1] == 'save':
            await channel.send('指令格式：.save')
            await channel.send('指令範例：.save')
            await channel.send('指令說明：儲存該頻道正在進行的對戰數據，但不會記錄手牌資訊。')
        elif msg[1] == 'quit':
            await channel.send('指令格式：.quit')
            await channel.send('指令範例：.quit')
            await channel.send('指令說明：結束該頻道的對戰。Bot會再要求你輸入.quit yes以確認結束對戰。')
        else:
            await channel.send('未發現此項指令。')
    else:
        await channel.send('help指令格式錯誤')