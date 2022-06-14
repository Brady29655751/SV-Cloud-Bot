import random
import cardmaster as cm
import database as db

def init_game():
    return [give_craft(), give_craft()]

def give_craft():
    craft = random.sample(db.craft_name[1:], 3)
    return craft

def give_choice():
    return

def choose(deck):
    return


