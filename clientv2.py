from flask import Flask, render_template, request
import socket
import os
import sys

from config import FORMAT, SIZE

app = Flask(__name__)


def send_request(command, *args):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect(
            (socket.gethostbyname(socket.gethostname()), int(sys.argv[1]))
        )
        msg = client_socket.recv(SIZE).decode(FORMAT)
        print(msg)
        data = (f"{command}\n" + '\n'.join(args)).encode(FORMAT)
        client_socket.send(data)
        response = client_socket.recv(SIZE).decode(FORMAT)
    return response


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/process_request", methods=["POST"])
def process_request():
    data = request.form.get("data", "")
    if len(data) == 0:
        return "Invalid request."

    data = data.split(',')
    cmd = data[0]

    if cmd == "CREATE_TEAM":
        response = send_request(cmd, data[1], data[2])

    elif cmd == "DELETE_FILE":
        response = send_request(cmd, data[1])
    elif cmd == "MOVE_FILE":
        response = send_request(cmd, data[1], data[2])
    elif cmd == "COPY_FILE":
        response = send_request(cmd, data[1], data[2])
    elif cmd == "RENAME_FILE":
        response = send_request(cmd, data[1], data[2])

    elif cmd == "JOIN_TEAM":
        response = send_request(cmd, data[1], data[2])

    elif cmd == "GET_REQUEST":
        response = send_request(cmd, data[1])
    elif cmd == "ACCEPT_REQUEST":
        response = send_request(cmd, data[1], data[2])
    elif cmd == "DECLINE_REQUEST":
        response = send_request(cmd, data[1], data[2])

    else:
        return "Unknown command."

    return response


if __name__ == "__main__":
    app.run(debug=True, port=5001)
