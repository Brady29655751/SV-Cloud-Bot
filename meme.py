import os
import discord
import random
import database as db
import utility as utils
import filehandler as fh

meme_dir = os.path.join('.', 'meme')

meme_dict = {}
emoji_dict = {}
emoji_translate = {
  'wait what wow': '.think goldship stock',
  '.big bruh': '.rage 10 rage 3 next rage 4 good rage 5 good rage 2 next rage 2 good 5 rage 3 good rage 2 next rage 2 good rage good rage good rage 3 good rage 2 next rage 3 good 3 rage 4 good rage 2 next rage 4 good rage 5 good rage 2 next rage 2 good 5 rage good rage good rage 2 next rage 4 good rage 3 good rage good rage 2 next rage 2 good 5 rage good rage good rage 2 next rage 10 good rage 2 next rage 2 good 5 rage 3 good rage 2 next rage 2 good rage 3 good rage 3 good rage 2 next rage 2 good 5 rage 2 good 2 rage 2 next rage 10 rage 3'
}

garden_id = os.environ['garden_id']
garden = []

def init_dict(filename, target_dict):
    global meme_dir
    path = os.path.join(meme_dir, filename)
    content = fh.read(path)
    for info in content:
        target_dict[info['name']] = info['content']
    return

async def init_meme(bot):
    global meme_dict, emoji_dict, garden, garden_id
    init_dict('meme.csv', meme_dict)
    init_dict('emoji.csv', emoji_dict)
    garden_channel = bot.get_channel(int(garden_id))
    garden = await garden_channel.history(limit=300).flatten()
    garden = [x for x in garden if (x.attachments) and (x.author != bot.user)]

def get_meme(content):
    global meme_dict, meme_dir
    path = os.path.join(meme_dir, 'file')
    if "<@985566260555300934>" in content:
        path = os.path.join(path, meme_dict['who tag me'])
        return discord.File(path)
      
    if not (content.startswith('!') or content.startswith('！')):
        return False
    
    content = content.lower()
    key = content.strip('!！')
    if key == 'meme list':
        return f'meme總表：\n{[x for x in meme_dict]}'    
    elif key == '色圖':
        ret = random.choice(garden)
        ret = random.choice(ret.attachments)
        return f'{ret.url}'
    elif key == '寄':
        return emoji_dict['die']
    elif key in meme_dict:
        path = os.path.join(path, meme_dict[key])
        return discord.File(path)
    return False

def get_emoji(content):
    content = content.lower()
    content = emoji_translate.get(content, content)
  
    msg = content.split()
    for key, values in emoji_dict.items():
        if (msg[0] == ('.' + key)):
            last_emoji = values
            emoji_queue = [values]
            for key in msg[1:]:
                num = utils.int_parser(key, True)
                same_as_last = (not isinstance(num, bool)) and (num in range(11)) and (last_emoji in emoji_dict.values())
                if same_as_last:
                    emoji_queue += [last_emoji for x in range(num-1)]
                    last_emoji = num
                elif key in emoji_dict:
                    emoji_queue.append(emoji_dict[key])
                    last_emoji = emoji_dict[key]
                elif key == 'next':
                    emoji_queue.append('\n')
                    last_emoji = '\n'
                else:
                    cube = key.split('/')
                    if len(cube) == 2:
                        row = utils.int_parser(cube[0], True)
                        col = utils.int_parser(cube[1], True)
                        if utils.is_parsed_int(row, 6) and utils.is_parsed_int(col, 6) and (last_emoji in emoji_dict.values()):
                            if emoji_queue[-1] != '\n':
                                emoji_queue.pop()
                            for i in range(col):
                                emoji_queue += ([last_emoji for j in range(row)] + ['\n'])
                            last_emoji = [row, col]
                  
            value_queue = utils.concate_content_with_character(emoji_queue, ' ', '\n')
            if (not value_queue) or all(emo == '\n' for emo in value_queue):
                return False
            return value_queue
    return False