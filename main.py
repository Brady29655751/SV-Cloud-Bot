import os
import discord
import random
import datetime as dt

import keep_alive

import client
import admin


bot_token = os.environ['bot_token']
admin_id = os.environ['admin_id']

#############
# commands

client_command = {
    'battle': client.battle,
    'dice': client.dice,
    'player': client.players,
    'deck': client.deck_info,
    'keep': client.keep,
    'draw': client.draw,
    'search': client.search,
    'explore': client.explore,
    'add': client.add,
    'substitute': client.substitute_deck,
    'effect': client.modify_deck_effect,
    'quit': client.quit,
    'help': client.help
}

admin_command = {
    'count': admin.game_count,
    'active': admin.check_active_time,
    'player': admin.check_player,
    'quit': admin.game_quit,
    'announce': admin.game_announce
}

########
bot = discord.Client()

@bot.event
async def on_ready():
    print('目前登入身分：', bot.user)


@bot.event
async def on_message(message):
    global running_games

    channel = message.channel
    content = message.content
    if message.author == bot.user:
        return

    # admin cmd
    if str(message.author.id) == admin_id:
        for key, values in admin_command.items():
            if content.startswith('.admin game ' + key):
                await values(content, channel)
                return

    # client cmd
    #print(message.author.id)
    if content == '.quit':
        await client.quit(content, channel, bot)
        return
    
    for key, values in client_command.items():
        if content.startswith('.' + key):
            await values(content, channel)
            return

keep_alive.keep_alive()
bot.run(bot_token)