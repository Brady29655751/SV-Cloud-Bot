import os
import discord
import random
import database as db
import utility as utils
import filehandler as fh

cheat_dir = os.path.join('.', 'cheat')

n_thinking = []
cheat_sheet = []
cheat_sheet_by_craft = [[] for i in range(db.craft_count)]
cheat_sheet_by_title = {}

class Cheat:
    def __init__(self, info, craft):
        self.info = info
        self.craft = craft
        self.title = info['title']
        self.content = info['content']
        self.effect = info['effect']

def init_N_thinking():
    global cheat_dir, n_thinking
    path = os.path.join(cheat_dir, 'N-thinking.txt')
    content = fh.read(path)
    n_thinking = [x.replace('\\n', '\n') for x in content]

def init_cheat_sheet():
    global cheat_dir
    init_N_thinking()
    for craft in db.craft_name_en:
        craft_index = db.craft_name_en.index(craft)
        path = os.path.join(cheat_dir, craft + '.csv')
        content = fh.read(path)
        for cheat_info in content:
            cheat = Cheat(cheat_info, craft_index)
            cheat_sheet.append(cheat)
            cheat_sheet_by_craft[craft_index].append(cheat)
            cheat_sheet_by_title[cheat.title] = cheat
    return
            




