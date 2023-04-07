import socket
import threading
from constants import *

IP = '0.0.0.0'
PORT = 25252
N_PLAYERS = 8

PASSWORDS = {"a": "pass12345",
             "b": "trollers147",
             "c": "69Pog69"}


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

    def __init__(self, handle, client_socket):
        super().__init__(target=handle, args=(client_socket,))
        self.socket = client_socket
