import os
import discord
from discord.ext import tasks, commands
import random
import datetime as dt

import keep_alive

import client
import admin


bot_token = os.environ['bot_token']
admin_id = os.environ['admin_id']
content = None
channel = None

#############
# commands

client_command = {
    'me': client.repeat_after_me,
    'repeat': client.repeat_after_me,

    'battle': client.battle,
    '2pick': client.battle,
    'dice': client.dice,
    'player': client.game_info,
    'deck': client.deck_info,
    'choose': client.choose,
    'shuffle': client.shuffle,
    'keep': client.keep,
    'draw': client.draw,
    'search': client.search,
    'explore': client.explore,
    'add': client.add,
    'substitute': client.substitute_deck,
    'effect': client.modify_deck_effect,
    'portal': client.portal,
    'travel': client.travel,
    'filter': client.filter_portal,
    'cheat': client.cheat,
    'nn': client.n_thinking,
    'gacha': client.gacha,
    'save': client.save,
    'quit': client.quit,
    'help': client.help
}

admin_command = {
    'channel': admin.check_channel_id,
    'count': admin.game_count,
    'active': admin.check_active_time,
    'player': admin.check_player,
    'save': admin.game_save,
    'quit': admin.game_quit,
    'announce': admin.game_announce,
    'repeat': admin.admin_repeat
}

########
bot = discord.Client()

@bot.event
async def on_ready():
    playing_game = discord.Game(name='雲SV')
    await bot.change_presence(activity=playing_game)
    admin.on_ready(bot)
    print('目前登入身分：', bot.user)

@bot.event
async def on_message(message):
    global running_games
    try:
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

        await client.idle(content, channel)
    except Exception as e:
        await admin.error_report(content, channel, e)

keep_alive.keep_alive()
bot.run(bot_token)
  