import socket
import threading
from constants import *
from time import sleep

IP = '0.0.0.0'
PORT = 25252
N_PLAYERS = 8
INIT_MONEY = 500

PASSWORDS = {"a": "pass12345",
             "b": "trollers147",
             "c": "69Pog69"}


def wait_and_send(self, client, message, time):
    sleep(time)
    client.socket.send(message)


def delayed_message(self, client, message, time):
    """sends the pre-constructed message to client after given amount of time (in seconds)"""
    t = threading.Thread(target=wait_and_send, kwargs={"client": client, "message": message, "time": time})


def hint_password(correct, attempt):
    """generates wordle-like packet based on the entered password and the correct one.
    message is in the form of 'ICPASS [character][colors] [character][colors]'...
    where the colors indicate the hints for each characters:
        g = green = correct
        y = yellow = exists in password
        p = purple = adjacent to the correct character in the ASCII table
        r = red = at the end of the string, indicates incorrect length"""

    message = ""
    for i in range(len(attempt)):
        if i == len(correct):
            message += ' ' + attempt[i] + 'r'
            return message.encode()
        message += " " + attempt[i]
        if attempt[i] == correct[i]:
            message += 'g'
        else:
            if attempt[i] in correct:
                message += 'y'
            if abs(ord(attempt[i]) - ord(correct[i])) == 1:
                message += 'p'
    if len(attempt) < len(correct):
        message += " \0r"
    return message


class Client(threading.Thread):

    def __init__(self, handle, client_socket, accounts):
        super().__init__(target=handle, args=(self,))
        self.socket = client_socket
        self.accessible = []
        self.attempts = {user: 0 for user in accounts.keys()}


class Account:

    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.money = INIT_MONEY
