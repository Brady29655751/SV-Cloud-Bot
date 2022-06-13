import discord
import datetime as dt

import game as sv

########
# admin command

def get_room(room_num):
    for key, values in sv.running_games.items():
        if values.room_num == room_num:
            return values
    return None    

async def game_count(content, channel):
    await channel.send(f'正在運行的雲對戰數量：{len(sv.running_games)}')
    await channel.send(f'正在運行的雲對戰房間：{[values.room_num for key, values in sv.running_games.items()]}')

async def check_active_time(content, channel):
    msg = content.split()
    if len(msg) != 4:
        await channel.send(f'指令格式錯誤')
        return
    
    room_num = msg[3]
    game = get_room(room_num)
    if game == None:
        await channel.send(f'房間號碼不存在')
        return
    await channel.send(f'房號 {room_num} 上次活動時間：{game.active_time}')

async def check_player(content, channel):
    msg = content.split()
    if len(msg) != 4:
        await channel.send(f'指令格式錯誤')
        return
    
    room_num = msg[3]
    game = get_room(room_num)
    if game == None:
        await channel.send(f'房間號碼不存在')
        return

    await channel.send(f'房號 {room_num} 的玩家：\n' +
        f'\t1號：{game.player_1.name}\n' +
        f'\t2號：{game.player_2.name}')

async def game_quit(content, channel):
    msg = content.split()
    if len(msg) != 4:
        await channel.send(f'指令格式錯誤')
        return
    
    room_num = msg[3]
    if room_num == 'all':
        channel_list = []
        for key, values in sv.running_games.items():
            channel_list.append(values.channel)
        sv.running_games = {}
        for game_channel in channel_list:
            await game_channel.send(f'**【系統公告】**\n為了減輕BOT負擔，管理員已刪除此頻道的對戰。')
        await channel.send(f'已刪除所有房間')
        return

    game = get_room(room_num)
    if game == None:
        await channel.send(f'房間號碼不存在')
        return

    game_channel_id = game.channel.id
    game_channel = game.channel
    del sv.running_games[game_channel_id]
    await channel.send(f'已刪除房間 {room_num}')
    await game_channel.send(f'**【系統公告】**\n為了減輕BOT負擔，管理員已刪除此頻道的對戰。')

async def game_announce(content, channel):
    msg = content.split()
    if len(msg) < 4:
        await channel.send(f'指令格式錯誤')
        return
    
    announcement = '**【系統公告】**\n' + msg[3]
    if len(msg) >= 5:
        for text in msg[4:]:
            announcement = announcement + '\n' + text
    
    channel_list = []
    for key, values in sv.running_games.items():
        channel_list.append(values.channel)

    for game_channel in channel_list:
        await game_channel.send(announcement)

    await channel.send(f'已發送系統公告。\n\n'+ f'{announcement}')

