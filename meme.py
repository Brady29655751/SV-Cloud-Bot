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
    global meme_dict
    if not (content.startswith('!') or content.startswith('！')):
        return False
    key = content.strip('!！')
    if key == 'meme list':
        return f'meme總表：\n{[x for x in meme_dict]}'
    return meme_dict.get(key, False)

def get_emoji(content):
    msg = content.split()
    if content.lower() == 'wait what wow':
        msg = ['.think', 'goldship', 'stock']

    for key, values in emoji_dict.items():
        if (msg[0] == ('.' + key)):
            emoji_queue = [values] + [emoji_dict[key] for key in msg[1:] if key in emoji_dict]
            value_queue = utils.concate_content_with_character(emoji_queue, ' ')
            return value_queue
    return False