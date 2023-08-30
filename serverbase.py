import socket
import threading
from constants import *
from time import sleep
from protocol import *

IP = '0.0.0.0'
PORT = 25252
MAX_ATTEMPTS = 5
BLOCK_TIME = 10

MINUSERLEN = 4
MAXUSERLEN = 8
MINPASSLEN = 8
MAXPASSLEN = 12
ALLOWED_IN_USER = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'


def user_is_valid(username, minlen, maxlen, allowed_chars):
    if not (minlen <= len(username) <= maxlen):
        return False, f"Username must be between {minlen} and {maxlen} characters."
    if not all([c in allowed_chars for c in username]):
        return False, f"Only the characters: " + ','.join(allowed_chars) + " are allowed in the username."
    return True, None


def pass_is_valid(password, minlen, maxlen, allowed_chars):
    if not (minlen <= len(password) <= maxlen):
        return False, f"Password must be between {minlen} and {maxlen} characters."
    if not all([c in allowed_chars for c in password]):
        return False, f"Only the characters: " + ','.join(allowed_chars) + " are allowed in the password."
    return True, None


def check_user_pass(username, password, lobby, client=None):
    """Check if given username and password are valid. if not, send respective message.
    Returns True if both valid, otherwise return False."""
    isvalid, message = user_is_valid(username, MINUSERLEN, MAXUSERLEN, ALLOWED_IN_USER)
    if not isvalid:
        if client:
            client.socket.send(construct_message(IVUSER, message))
        return False
    isvalid, message = pass_is_valid(password, lobby.minpasslen, lobby.maxpasslen, lobby.allowed_in_pass)
    if not isvalid:
        if client:
            client.socket.send(construct_message(IVPASS, message))
        return False
    return True


def multi_func(*args):
    return lambda: [f() for f in args]


def hint_password(correct, attempt):
    """generates wordle-like packet based on the entered password and the correct one.
    message is in the form of 'ICPASS [character][colors] [character][colors]'...
    where the colors indicate the hints for each characters:
        g = green = correct
        y = yellow = exists in password
        p = purple = adjacent to the correct character in the ASCII table
        r = red = at the end of the string, indicates incorrect length"""

    print(attempt)
    message = ""
    for i in range(len(attempt)):
        if i == len(correct):
            message += SPACE + attempt[i] + 'r'
            return message
        message += SPACE + attempt[i]
        if attempt[i] == correct[i]:
            message += 'g'
        else:
            if attempt[i] in correct:
                message += 'y'
            if abs(ord(attempt[i]) - ord(correct[i])) == 1:
                message += 'p'
    if len(attempt) < len(correct):
        message += SPACE + "\0r"
    print("AAAAAAAAAAAAAAAAAAA", message)
    return message[1:]


def get_lobby_data_message(lobby):
    data = []
    for client in lobby.clients:
        data.append(client.original_name)
        data.append('-')
        data.extend(client.accessible)
    return construct_message(LOBBYDATA, *data)


class Client(threading.Thread):

    def __init__(self, handle, client_socket):
        super().__init__(target=handle, args=(self,))
        self.original_name = None
        self.socket = client_socket
        self.lobby = None
        self.accessible = []
        self.attempts = dict()
        self.block_times = dict()
        self.in_game = True

    def clear_attempts(self, username):
        self.attempts[username] = 0

    def inc_attempts(self, username):
        if username in self.attempts.keys():
            self.attempts[username] += 1
        else:
            self.attempts[username] = 1

    def get_attempts(self, username):
        if username in self.attempts.keys():
            return self.attempts[username]
        else:
            return 0

    def set_name(self, name):
        self.original_name = name

    def exit_lobby(self):
        self.original_name = None
        self.lobby = None
        self.accessible = []
        self.attempts = dict()
        self.block_times = dict()
        self.in_game = True


class Account:

    def __init__(self, username, password):
        self.username = username
        self.password = password


class Lobby:

    def __init__(self, name):
        self.name = name
        self.is_open = False
        self.started = False
        self.game_started = False
        self.clients = []
        self.max_clients = N_PLAYERS
        self.accounts = dict()
        self.minpasslen = MINPASSLEN
        self.maxpasslen = MAXPASSLEN
        self.allowed_in_pass = '1234567890'
        self.init_players = None

        self.admin = None

    def add_client(self, client):
        self.clients.append(client)
        if len(self.clients) == 1:
            self.admin = client
            return True
        return False

    def remove_client(self, client):
        self.clients.remove(client)
        if not self.started:
            self.accounts.pop(client.original_name)
        if len(self.clients) == 1:
            self.admin = self.clients[0]
            return True
        return False

    def get_active_players(self):
        return [client for client in self.clients if client.in_game]

    def update(self):
        active_players = len(self.get_active_players())
        self.minpasslen = MINPASSLEN - (self.init_players - active_players)
        self.maxpasslen = MAXPASSLEN - (self.init_players - active_players)

    def get_data(self):
        return [(client.original_name, '-', *client.accessible) for client in self.clients]

    def open(self):
        self.is_open = True

    def start(self):
        self.started = True
        self.init_players = len(self.clients)
