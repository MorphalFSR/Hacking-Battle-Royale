import socket
import threading

APPROVED = 'APPROVED'  # Correct username and password
ICUSER = 'ICUSER'  # InCorrect Username
ICPASS = 'ICPASS'  # InCorrect Password

LOGIN = 'LOGIN'
QUIT = 'QUIT'

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

    message = ICPASS
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
    return message.encode()


def handle_client(client):
    attempts = {user: 0 for user in PASSWORDS.keys()}
    maintain_connection = True
    with client:
        while maintain_connection:
            data = client.recv(1024).decode().split(" ")
            command = data[0]
            args = data[1:]
            # print(args)
            if command == LOGIN:
                username, password = args
                if username in PASSWORDS.keys():
                    if PASSWORDS[username] == password:
                        client.send(APPROVED.encode())
                    else:
                        print("pass")
                        client.send(hint_password(PASSWORDS[username], password))
                        attempts[username] += 1
                else:
                    print("user")
                    client.send(ICUSER.encode())
            elif command == QUIT:
                print(f"Disconnecting from {client}")
                maintain_connection = False


def main():
    threads = []
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind((IP, PORT))
        server.listen(N_PLAYERS)
        while True:
            client, address = server.accept()
            print(f"Connected to {client}")
            new_thread = threading.Thread(target=handle_client, args=(client,))
            threads.append(new_thread)
            new_thread.start()


if __name__ == "__main__":
    main()
