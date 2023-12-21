import socket

IP = socket.gethostbyname(socket.gethostname())
PORT = 5000
ADDR = (IP, PORT)
FORMAT = "utf-8"
SIZE = 1024

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