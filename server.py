import socket
import threading


IP = '0.0.0.0'
PORT = 25252
N_PLAYERS = 8


def handle_client(client):
    with client:
        while True:
            data = client.recv(1024)
            print(data.decode())
            client.send(data)


def main():
    threads = []
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind((IP, PORT))
        server.listen(N_PLAYERS)
        while True:
            client, address = server.accept()
            print(f"Connected to {client}.")
            new_thread = threading.Thread(target=handle_client, args=(client,))
            threads.append(new_thread)
            new_thread.start()


if __name__ == "__main__":
    main()
