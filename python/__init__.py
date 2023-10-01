# This is currently running in samp server if you are planning to port it to openmp
# Please dont forget to make a pull request

import mysql.connector
import bcrypt

from pysamp.player import Player
from pysamp import *
from pysamp.dialog import Dialog

serverdb = mysql.connector.connect(host="localhost", user="root", password="", database="python-db")

player_default_posx = 2215.5181
player_default_posy = -2627.8174
player_default_posz = 13.5469
player_default_rot = 273.7786

@on_gamemode_init
def server_init():
    set_game_mode_text("PYProject v1.0.0")

@Player.on_connect
def on_user_connect(player: Player):
    check_user = serverdb.cursor()
    user_name = player.get_name()
    query = "SELECT user_name FROM player_accounts WHERE user_name='{}'".format(user_name)
    check_user.execute(query)

    result = check_user.fetchone()

    is_user_registered(player, result)

def get_user_password(player: Player):
    get_password_cursor = serverdb.cursor()
    get_password_query = "SELECT user_password FROM player_accounts WHERE user_name='{}'".format(player.get_name())
    get_password_cursor.execute(get_password_query)
    return get_password_cursor.fetchone()

def register_response(player: Player, response: int, list_item: int, input_text: str):
    if response:
        password_in_bytes = input_text.encode("utf-8")
        password_salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password_in_bytes, password_salt)

        insert_new_user = serverdb.cursor()
        query = "INSERT INTO player_accounts (user_name, user_password) VALUES (%s, %s)"
        query_val = (player.get_name(), hashed_password,)
        insert_new_user.execute(query, query_val)

        serverdb.commit()

        player_spawn(player)
    else:
        player.kick()

def login_response(player: Player, response: int, list_item: int, input_text: str):
    if response:
        select_cursor = serverdb.cursor()
        query = "SELECT user_password FROM player_accounts WHERE user_name='{}'".format(player.get_name())
        select_cursor.execute(query)

        result = select_cursor.fetchone()

        user_input = input_text.encode("utf-8")

        result = bcrypt.checkpw(user_input, result[0].encode("utf-8"))

        if not result:
            player.send_client_message(0xFF0000FF, "Password incorrect!")
            show_login_menu(player)
        else:
            load_player_data(player)

def is_user_registered(player: Player, user_found):
    if not user_found:
        register_dialog = Dialog.create(3, "Registration", "Please enter your desired password for your account", "Continue", "Exit", on_response=register_response)
        register_dialog.show(player)
    else:
        show_login_menu(player)

def show_login_menu(player: Player):
    login_dialog = Dialog.create(3, "Login", "Please enter your account password to continue", "Spawn", "Exit", on_response=login_response)
    login_dialog.show(player)

def player_spawn(player: Player):
    player.set_spawn_info(255, 3, player_default_posx, player_default_posy, player_default_posz, player_default_rot, 0, 0, 0, 0, 0, 0)
    player.spawn()

    player.send_client_message(-1, "Your account has been succesfully registered")

def load_player_data(player: Player):
    select_cursor = serverdb.cursor()
    select_cursor.execute(f"SELECT * FROM player_accounts WHERE user_name='{player.get_name()}'")
    result = select_cursor.fetchone()

    player.set_spawn_info(255, 3, result[3], result[4], result[5], result[6], 0, 0, 0, 0, 0, 0)
    player.spawn()
    player.send_client_message(-1, f"Welcome back to the server! {player.get_name()}")
    
    