from datetime import datetime, timedelta
import os
import re
import sys
from quan_server import check_role

sys.path.append("../")

from config import (
    SERVER_DATA_PATH,
    SESSION_TIMEOUT_MINUTES,
)



def is_valid_password(password):
    if len(password) < 8:
        return False
    if not re.search(r"[A-Z]", password):
        return False
    if not re.search(r"[a-z]", password):
        return False
    if not re.search(r"\d", password):
        return False
    return True


def register(data, cursor, dbconn):
    username, password, name = data[1], data[2], data[3]
    if username == "" or password == "" or name == "":
        send_data = "2011"
    # elif is_valid_password(password) is False:
    #     send_data = "2012"
    elif is_valid_password(password) is False:
        send_data = "2012"
    else:
        cursor.execute("SELECT account FROM Account WHERE account = ?", (username,))
        result = cursor.fetchone()

        if result:
            send_data = "2013"
        else:
            send_data = "1010"
            # hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
            cursor.execute(
                "INSERT INTO Account (account, password, name) VALUES (?, ?, ?)",
                (username, password, name),
            )
            dbconn.commit()

    # conn.send("{send_data}\r\n".encode(FORMAT))
    return send_data


def change_password(data, account, cursor, dbconn):
    password, new_password, cf_password = data[1], data[2], data[3]
    if account is not None:
        cursor.execute(
            "SELECT password FROM Account WHERE account = ?",
            (account,),
        )
        pw_result = cursor.fetchone()

        if pw_result and pw_result[0] == password:
            if pw_result[0] == new_password:
                send_data = "2021"
            elif new_password != cf_password:
                send_data = "2022"
            elif is_valid_password(new_password) is False:
                send_data = "2023"
            else:
                cursor.execute(
                    "UPDATE Account SET password = ? WHERE account = ?",
                    (new_password, account),
                )
                dbconn.commit()
                send_data = "1020"
        else:
            send_data = "2024"

    # conn.send(send_data.encode(FORMAT))
    return send_data


def quit_team(conn, data, account, cursor, dbconn):
    team_name = data[1]

    role = check_role(account, team_name, cursor)

    if role == "Team not exist":
        send_data = "2042"

    elif role is None:
        send_data = "2101"

    elif role == "Leader":
        send_data = "2111"
    else:
        cursor.execute(
            "DELETE FROM Team_member WHERE team_name=? AND account=?",
            (team_name, account),
        )
        send_data = "1110"  # Successfully quit the team
        dbconn.commit()

    # conn.send(send_data.encode(FORMAT))
    return send_data


def remove_member(conn, data, account, cursor, dbconn):
    team_name, member_name = data[1], data[2]

    role = check_role(account, team_name, cursor)
    if role == "Team not exist":
        send_data = "2042"
    elif role is None:
        send_data = "2101"
    elif role == "Member":
        send_data = "2214"
    elif role == "Leader":
        # Remove the member from the team
        cursor.execute(
            "SELECT account FROM Team_member WHERE team_name = ? AND account = ?",
            (team_name, member_name),
        )
        result = cursor.fetchone()
        if result is None:
            send_data = "2122"
        else:
            if result[0] == account:
                send_data = "2123"
            else:
                cursor.execute(
                    "DELETE FROM Team_member WHERE team_name = ? AND account = ?",
                    (team_name, member_name),
                )
                dbconn.commit()
                send_data = "1120"  # Successfully removed the member

    # conn.send(send_data.encode(FORMAT))
    return send_data


def get_all_user(username, cursor):
    cursor.execute("SELECT account FROM Account WHERE account != ?", (username,))
    result = cursor.fetchall()
    user = [row[0] for row in result]
    send_data = "1130\n" + "\n".join(user)
    # conn.send(send_data.encode(FORMAT))
    return send_data


def invite_member(data, account, cursor, dbconn):
    team_name, member_name = data[1], data[2]

    role = check_role(account, team_name, cursor)
    if role == "Team not exist":
        send_data = "2042"
    elif role is None:
        send_data = "2101"
    elif role == "Member":
        send_data = "2214"
    elif role == "Leader":
        cursor.execute("SELECT account FROM Account WHERE account = ?", (member_name,))
        user_result = cursor.fetchone()
        if user_result is None:
            send_data = "2141"
        else:
            # Check if the user is already a member of the team
            cursor.execute(
                "SELECT * FROM Team_member WHERE team_name = ? AND account = ?",
                (team_name, member_name),
            )
            user_existed = cursor.fetchone()

            if user_existed is not None:
                send_data = "2142"
            else:
                cursor.execute(
                    "INSERT INTO Invite_request (receiver, team_name) VALUES (?, ?)",
                    (member_name, team_name),
                )
                dbconn.commit()
                send_data = "1140"  # Invite request sent successfully

    # conn.send(send_data.encode(FORMAT))
    return send_data


def get_all_invitations(account, cursor):
    cursor.execute("SELECT team_name FROM Invite_request WHERE receiver=?", (account,))
    result = cursor.fetchall()

    if result:
        send_data = "1150\n" + "\n".join(row[0] for row in result)
    else:
        send_data = "2151"

    # conn.send(send_data.encode(FORMAT))
    return send_data


def accept_invitation(data, account, cursor, dbconn):
    team_name = data[1]

    cursor.execute(
        "SELECT team_name FROM Invite_request WHERE receiver=? AND team_name=?",
        (account, team_name),
    )
    result = cursor.fetchone()
    if result is None:
        send_data = "2161"
    else:
        cursor.execute(
            "INSERT INTO Team_member (account, team_name) VALUES (?, ?)",
            (account, team_name),
        )
        dbconn.commit()

        cursor.execute(
            "DELETE FROM Invite_request WHERE receiver=? AND team_name=?",
            (account, team_name),
        )
        dbconn.commit()

        cursor.execute(
            "DELETE FROM Join_request WHERE sender=? AND team_name=?",
            (account, team_name),
        )
        dbconn.commit()

        send_data = "1160"
    # conn.send(send_data.encode(FORMAT))
    return send_data


def decline_invitation(data, account, cursor, dbconn):
    team_name = data[1]

    cursor.execute(
        "SELECT team_name FROM Invite_request WHERE receiver=? AND team_name=?",
        (account, team_name),
    )
    result = cursor.fetchone()
    if result is None:
        send_data = "2161"
    else:
        cursor.execute(
            "DELETE FROM Invite_request WHERE receiver=? AND team_name=?",
            (account, team_name),
        )
        dbconn.commit()

        send_data = "1170"
    # conn.send(send_data.encode(FORMAT))
    return send_data


def dir_information(data, account, cursor):
    team_name, dir_path = data[1], data[2]

    role = check_role(account, team_name, cursor)
    if role == "Team not exist":
        send_data = "2042"
    elif role is None:
        send_data = "2101"
    else:
        path = os.path.join(SERVER_DATA_PATH, team_name, dir_path)
        if not os.path.exists(path):
            send_data = "2181"
        else:
            files = os.listdir(path)

            if len(files) == 0:
                send_data = "2182"
            else:
                send_data = "1180\n" + "\n".join(f for f in files)
    # conn.send(send_data.encode(FORMAT))
    return send_data
