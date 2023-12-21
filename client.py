import socket

IP = socket.gethostbyname(socket.gethostname())
PORT = 5000
ADDR = (IP, PORT)
FORMAT = "utf-8"
SIZE = 1024

def login(client):
    username = input("Enter username: ")
    password = input("Enter password: ")
    client.send(f"LOGIN\n{username}\n{password}".encode(FORMAT))
    response = client.recv(SIZE).decode(FORMAT)
    print(f"{response}")

    if response.startswith("1030"):
        print("Login successful!")
        return {"username": username}
    else:
        print("Login failed. Please try again.")
        return None

def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(ADDR)
    data = client.recv(SIZE).decode(FORMAT)
    print(f"{data}")

    while True:
        inputCmd = input("Enter Command: ")
        client.send(f"{inputCmd}\nHello".encode(FORMAT))
        
        if inputCmd == "CMD":
            response = client.recv(SIZE).decode(FORMAT)
            print(response)
        elif inputCmd == "BYE":
            response = client.recv(SIZE).decode(FORMAT)
            break
        else:
            print("Command not found, please try again")

    print("Disconnected from the server.")
    client.close()


if __name__ == "__main__":
    main()