import socket
import threading
import sqlite3

IP = socket.gethostbyname(socket.gethostname())
PORT = 5000
ADDR = (IP, PORT)
SIZE = 1024
FORMAT = "utf-8"

DB_CONNECTIONS = {}
DB_CONNECTIONS_LOCK = threading.Lock()
ACTIVE_SESSIONS = {}
ACTIVE_SESSIONS_LOCK = threading.Lock()


def get_database_connection():
    thread_id = threading.current_thread().ident
    with DB_CONNECTIONS_LOCK:
        if thread_id not in DB_CONNECTIONS:
            DB_CONNECTIONS[thread_id] = sqlite3.connect("file_share.db")
        else:
            try:
                # Try a simple query to check if the connection is still alive
                DB_CONNECTIONS[thread_id].execute("SELECT 1").fetchone()
            except sqlite3.ProgrammingError:
                # Reconnect if the connection is closed
                DB_CONNECTIONS[thread_id] = sqlite3.connect("file_share.db")
        return DB_CONNECTIONS[thread_id]


def close_connection(dbconn):
    dbconn.close()

def handle_client(conn, addr):

    print(f"[NEW CONNECTION] {addr} connected.")
    conn.send("OK\nWelcome to the File Server.".encode(FORMAT))

    while True:
        data = conn.recv(SIZE).decode(FORMAT)
        data = data.split("\n")
        cmd = data[0]

        if cmd == "CMD":
            print("Successfully")
            conn.send("CMD Successfully".encode(FORMAT))
        elif cmd == "BYE":
            print("Bye")
            conn.send("BYE".encode(FORMAT))
            break
    print(f"[DISCONNECTED] {addr} disconnected")
    conn.close()

def main():
    print("[STARTING] Server is starting")
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)
    server.listen()
    print(f"[LISTENING] Server is listening on {IP}:{PORT}.")

    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")


if __name__ == "__main__":
    main()