APPROVED = 'APPROVED'  # Correct username and password
ICUSER = 'ICUSER'  # InCorrect Username
ICPASS = 'ICPASS'  # InCorrect Password
HACKED = 'HACKED'
HACKING = 'HACKING'
LOGIN = 'LOGIN'
LOGOUT = 'LOGOUT'
QUIT = 'QUIT'
BLOCKED = 'BLOCKED'
UNBLOCKED = 'UNBLOCKED'
MONEY = 'MONEY'
TRANSFER = 'TRANSFER'
CREATE = 'CREATE'
TAKEN = 'TAKEN'

BREAK = '-'

LOGIN_RESPONSE_KEYS = [APPROVED, ICUSER, ICPASS]
CLIENT_RESPONSE_KEYS = [APPROVED, ICUSER, ICPASS, HACKED, BLOCKED, UNBLOCKED, LOGOUT, MONEY, HACKING, TAKEN]
SERVER_RESPONSE_KEYS = [LOGIN, QUIT, LOGOUT, CREATE, TRANSFER]


def construct_message(cmd, *args):
    txt = cmd
    for a in args:
        txt += f" {a}"
    txt += BREAK
    return txt.encode()


def deconstruct_message(message):
    split_message = message.split(" ")
    return split_message[0], split_message[1:]
