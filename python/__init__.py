import mysql.connector

from pysamp.player import Player
from pysamp import *

serverdb = mysql.connector.connect(host="localhost", user="root", password="", database="python-db")

from python.account.account_handle import show_main_menu

@on_gamemode_init
def server_init():
    set_game_mode_text("PYProject v1.0.0")

@Player.on_connect
def on_user_connect(player: Player):
    show_main_menu(player)
    
    