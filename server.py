# TODO: add logged in users for each client + log out message when hacked

import socket
import threading
from constants import *
from serverbase import *


class Server(threading.Thread):

    def __init__(self):
        super().__init__(target=self.handle_server)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients = []
        self.start()
        while True:
            username = input("Enter username: ")
            password = input("Enter password: ")
            PASSWORDS[username] = password

    def handle_server(self):
        with self.socket:
            self.socket.bind((IP, PORT))
            self.socket.listen(N_PLAYERS)
            while True:
                client_socket, address = self.socket.accept()
                print(f"Connected to {client_socket}")
                new_client = Client(handle=self.handle_client, client_socket=client_socket)
                self.clients.append(new_client)
                new_client.start()

    def handle_client(self, client_socket):
        attempts = {user: 0 for user in PASSWORDS.keys()}
        accessible = []
        maintain_connection = True
        while maintain_connection:
            data = client_socket.recv(1024).decode().split(" ")
            command = data[0]
            args = data[1:]
            if command == LOGIN:
                username, password = args
                if username in PASSWORDS.keys():
                    if username in accessible and password == "":
                        client_socket.send(f"{APPROVED} {username}".encode())
                    elif PASSWORDS[username] == password:
                        accessible.append(username)
                        client_socket.send(f"{APPROVED} {username}".encode())
                        for other_client in self.clients:
                            other_client.socket.send(f"{HACKED} {username}".encode())
                    else:
                        print("pass")
                        client_socket.send((f"{ICPASS} {username}" + hint_password(PASSWORDS[username], password)).encode())
                        attempts[username] += 1
                else:
                    print("user")
                    client_socket.send(f"{ICUSER} {username}".encode())
            elif command == QUIT:
                print(f"Disconnecting from {client_socket}")
                maintain_connection = False
        client_socket.close()
        self.clients.pop([client.socket for client in self.clients].index(client_socket))


if __name__ == "__main__":
    server = Server()
