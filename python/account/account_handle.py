import bcrypt

from pysamp.player import Player
from pysamp.dialog import Dialog
from python import serverdb

player_default_posx = 2215.5181
player_default_posy = -2627.8174
player_default_posz = 13.5469
player_default_rot = 273.7786

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

        player.set_spawn_info(255, 5, player_default_posx, player_default_posy, player_default_posz, player_default_rot, 0, 0, 0, 0, 0, 0)
        player.spawn()
    else:
        player.kick()

def login_response(player: Player, response: int, list_item: int, input_text: str):
    if response:
        result = get_player_password(player)
        user_input = input_text.encode("utf-8")
        password_match = bcrypt.checkpw(user_input, result[0].encode("utf-8"))

        if password_match:
            load_player_data()
        else:
            player.send_client_message(-1, "Password incorrect!")
            show_login_menu(player)

def show_main_menu(player: Player):
    found = is_player_found(player)

    if not found:
        register_dialog = Dialog.create(3, "Registration", "Please enter your desired password for your account", "Continue", "Exit", on_response=register_response)
        register_dialog.show(player)
    else:
        show_login_menu(player)

def is_player_found(player: Player):
    check_user = serverdb.cursor()
    check_user.execute(f"SELECT user_name FROM player_accounts WHERE user_name='{player.get_name()}'")
    return check_user.fetchone()

def get_player_password(player: Player):
    set_cursor = serverdb.cursor()
    set_cursor.execute(f"SELECT user_password FROM player_accounts WHERE user_name='{player.get_name()}'")
    return set_cursor.fetchone()

def show_login_menu(player: Player):
    login_dialog = Dialog.create(3, "Login", "Please enter your account password to continue", "Spawn", "Exit", on_response=login_response)
    login_dialog.show(player)

def load_player_data(player: Player):
    set_cursor = serverdb.cursor()
    set_cursor.execute(f"SELECT * FROM player_accounts WHERE user_name='{player.get_name}'")
    data = set_cursor.fetchone()

    player.set_spawn_info(255, 5, data[3], data[4], data[5], data[6], 0, 0, 0, 0, 0, 0)
    player.spawn()
    player.send_client_message(-1, "Welcome back to the server")