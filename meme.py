import os
import discord
import random
import database as db
import utility as utils
import filehandler as fh

meme_dir = os.path.join('.', 'meme')

meme_dict = {}
emoji_dict = {}

def init_dict(filename, target_dict):
    global meme_dir
    path = os.path.join(meme_dir, filename)
    content = fh.read(path)
    for info in content:
        target_dict[info['name']] = info['content']
    return

def init_meme():
    global meme_dict, emoji_dict
    init_dict('meme.csv', meme_dict)
    init_dict('emoji.csv', emoji_dict)

def get_meme(content):
    global meme_dict, meme_dir
    path = os.path.join(meme_dir, 'file')
    if not (content.startswith('!') or content.startswith('！')):
        return False
    key = content.strip('!！')
    if key == 'meme list':
        return f'meme總表：\n{[x for x in meme_dict]}'
    elif key in meme_dict:
        path = os.path.join(path, meme_dict[key])
        return discord.File(path)
    return False

def get_emoji(content):
    msg = content.split()
    if content.lower() == 'wait what wow':
        msg = ['.think', 'goldship', 'stock']

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