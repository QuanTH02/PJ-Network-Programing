import socket
import os
import sys

import sys
sys.path.append('../')

from config import SIZE, FORMAT, FILE_BLOCK_SIZE

def responseFromServer(client):
    # print("Go to responseFromServer")
    requests = client.recv(SIZE).decode(FORMAT)

    # Sửa
    responses = [request for request in requests.split('\r\n') if request]

    for response in responses:
        # SIGNUP
        if response.startswith("1010"):
            print("Đăng ký thành công")
        elif response.startswith("2012"):
            print("Trường thông tin nhập chưa đúng định dạng")
        elif response.startswith("2013"):
            print("Tài khoản đã tồn tại")
        
        # CHANGE_PASSWORD
        elif response.startswith("1020"):
            print("Đổi mật khẩu thành công")
        elif response.startswith("2021"):
            print("2 mật khẩu trùng nhau")
        elif response.startswith("2022"):
            print("Mật khẩu mới nhập lại không trùng khớp")
        elif response.startswith("2023"):
            print("Mật khẩu mới không đúng định dạng")
        elif response.startswith("2024"):
            print("Nhập mật khẩu cũ sai") 

        # LOGIN
        elif response.startswith("1030"):
            print("Đăng nhập thành công")
        elif response.startswith("2011"):
            print("Chưa nhập đủ các trường thông tin")
        elif response.startswith("2031"):
            print("Tài khoản không tồn tại")
        elif response.startswith("2032"):
            print("Mật khẩu không đúng")
        
        #CREATE_TEAM
        elif response.startswith("1040"):
            print("Tạo nhóm thành công")
        elif response.startswith("2041"):
            print("Tên nhóm đã tồn tại")
        elif response.startswith("2042"):
            print("Tên nhóm không tồn tại")
        
        # SHOW_MY_TEAMS
        elif response.startswith("1050"):
            print("Show my teams successfully")
            lines = response.split("\n")
            result = "\n".join(lines[1:])
            print(result)
        elif response.startswith("1051"):
            print("Chưa tham gia nhóm nào")

        #JOIN_TEAM
        elif response.startswith("1060"):
            print("Tham gia nhóm thành công")
        elif response.startswith("2061"):
            print("Nhập sai Team code")
        elif response.startswith("2062"):
            print("Đã tham gia nhóm rồi")

        #GET_JOIN_REQUEST
        elif response.startswith("1070"):
            print("Danh sách yêu cầu:")
            lines = response.split("\n")
            result = "\n".join(lines[1:])
            print(result)

        #ACCEPT_JOIN_REQUEST
        elif response.startswith("1080"):
            print("Chấp nhận yêu cầu thành công")
        elif response.startswith("2081"):
            print("Không tồn tại request")

        #DECLINE_JOIN_REQUEST
        elif response.startswith("1090"):
            print("Từ chối yêu cầu thành công")

        # GET_MEMBER
        elif response.startswith("1100"):
            print("Show team member successfully")
            lines = response.split("\n")
            result = "\n".join(lines[1:])
            print(result)
        elif response.startswith("2101"):
            print("Account không nằm trong team")

        # QUIT_TEAM
        elif response.startswith("1110"):
            print("Quit team successfully")
        elif response.startswith("2111"):
            print("Bạn là Leader không được rời nhóm")

        # REMOVE_MEMBER
        elif response.startswith("1120"):
            print("Remove member successfully")
        elif response.startswith("2122"):
            print("Tài khoản không tồn tại")
        elif response.startswith("2123"):
            print("Không thể xóa chính mình")

        # GET_ALL_USER
        elif response.startswith("1130"):
            print("Get all user successfully")
            lines = response.split("\n")
            result = "\n".join(lines[1:])
            print(result)

        # INVITE_MEMBER
        elif response.startswith("1140"):
            print("Invite member successfully")
        elif response.startswith("2141"):
            print("Tài khoản không tồn tại")
        elif response.startswith("2142"):
            print("Tài khoản đã tồn tại trong nhóm")

        # GET_ALL_INVITATIONS
        elif response.startswith("1150"):
            print("Get all invitations successfully")
            lines = response.split("\n")
            result = "\n".join(lines[1:])
            print(result)
        elif response.startswith("2151"):
            print("Không có lời mời nào")

        # ACCEPT_INVITATION
        elif response.startswith("1160"):
            print("Accept invitation successfully")
        elif response.startswith("2161"):
            print("Bạn không có lời mời này")

        # DECLINE_INVITATION
        elif response.startswith("1170"):
            print("Decline invitation successfully")

        # FOLDER_INFORMATION
        elif response.startswith("1180"):
            print("Folder information successfully")
            lines = response.split("\n")
            result = "\n".join(lines[1:])
            print(result)
        elif response.startswith("2181"):
            print("Folder không tồn tại")
        elif response.startswith("2182"):
            print("Folder rỗng")

        # UPLOAD
        elif response.startswith("1190"):
            print("Upload file successfully")

        # DOWNLOAD
        elif response.startswith("1200"):
            print("Download file successfully")
        elif response.startswith("2201"):
            print("File không tồn tại")

        #RENAME_FILE
        elif response.startswith("1210"):
            print("Đổi tên file thành công")
        elif response.startswith("2211"):
            print("Tên file trùng với file khác")
        elif response.startswith("2212"):
            print("Tên file không hợp lệ")
        elif response.startswith("2213"):
            print("Tên file có phần mở rộng không trùng khớp với phần mở rộng của file gốc")
        elif response.startswith("2215"):
            print("Không tìm thấy file trong thư mục gốc")

        #DELETE_FILE
        elif response.startswith("1220"):
            print("Delete file successfully")
        
        #COPY_FILE
        elif response.startswith("1230"):
            print("Copy file thành công")
        elif response.startswith("2231"):
            print("File đã tồn tại ở thư mục đích")
        elif response.startswith("2232"):
            print("Không tồn tại thư mục đích")
        #MOVE_FILE
        elif response.startswith("1240"):
            print("Move file thành công")  

        # CREATE_FOLDER
        elif response.startswith("1250"):
            print("Create folder successfully")
        elif response.startswith("2251"):
            print("Thư mục đã tồn tại")
        elif response.startswith("2252"):
            print("Tên thư mục không hợp lệ")

        # RENAME_FOLDER
        elif response.startswith("1260"):
            print("Rename folder successfully")
        elif response.startswith("2261"):
            print("Folder không tồn tại")
        elif response.startswith("2214"):
            print("Bạn không có quyền")

        # DELETE_FOLDER
        elif response.startswith("1270"):
            print("Delete folder successfully")

        # COPY_FOLDER
        elif response.startswith("1280"):
            print("Copy folder successfully") 
        elif response.startswith("2281"):
            print("Đã tồn tại folder ở thư mục đích")

        # MOVE_FOLDER
        elif response.startswith("1290"):
            print("Move folder successfully")
    
        # END
        elif response.startswith("3000"):
            print("Thông điệp không xác định")
        elif response.startswith("3001"):
            print("Thông điệp không đúng định dạng giao thức")

        elif response.startswith("2321"):
            print("Bạn đã đăng nhập rồi")
        elif response.startswith("2322"):
            print("Bạn chưa đăng nhập")
        elif response.startswith("1320"):
            print("Đăng xuất thành công")

        # elif response.startswith(""):
        #     print("")
            
        # print(response)
        # return response


def show_my_teams(client):
    client.send(f"SHOW_MY_TEAMS\r\n".encode(FORMAT))
    # response = client.recv(SIZE).decode(FORMAT)
    # return response
    # responseFromServer(client)

def upload_file(client, path, team_name, des_path):
    filename = os.path.basename(path)
    file_size = os.path.getsize(path)
    client.send(f"UPLOAD\n{filename}\n{team_name}\n{des_path}\n{file_size}\r\n".encode(FORMAT))
    print("To recv")
    response = client.recv(SIZE).decode(FORMAT)
    print("To respond")
    if response == "3001" or response == "2101" or response == "2042":
        return

    print("To open")
    with open(path, "rb") as f:
        print("Uploading file...")
        while True:
            chunk = f.read(FILE_BLOCK_SIZE)
            if not chunk:
                break
            client.send(chunk)

    # response = client.recv(SIZE).decode(FORMAT)
    # print(response)

def download_file(client, team_name, src_path, des_path):
    client.send(f"DOWNLOAD\n{team_name}\n{src_path}\r\n".encode(FORMAT))
    file_path = os.path.join(des_path, os.path.basename(src_path))

    response = client.recv(SIZE).decode(FORMAT)
    if response == '2042' or response == '2101' or response == '2201':
        return

    if os.path.exists(file_path):
        file_name = os.path.basename(src_path)
        new_file_name = file_name.split('.')[0] + '(1).' + file_name.split('.')[1]
        file_path = os.path.join(des_path, new_file_name)

    file_size = int(client.recv(SIZE).decode(FORMAT))
    with open(file_path, "wb") as f:
        while file_size > 0:
            chunk = client.recv(FILE_BLOCK_SIZE)
            f.write(chunk)
            file_size -= len(chunk)

def show_team_member(client, team_name):
    print("Show team member")
    client.send(f"GET_MEMBER\n{team_name}\r\n".encode(FORMAT))
    # response = client.recv(SIZE).decode(FORMAT)
    # print(response)

def create_directory(client, team_name, dir_path, dir_name):
    client.send(f"CREATE_FOLDER\n{team_name}\n{dir_path}\n{dir_name}\r\n".encode(FORMAT))
    # response = client.recv(SIZE).decode(FORMAT)
    # print(response)

def rename_directory(client, team_name, dir_path, dir_name, dir_new_name):
    client.send(f"RENAME_FOLDER\n{team_name}\n{dir_path}\n{dir_name}\n{dir_new_name}\r\n".encode(FORMAT))
    # response = client.recv(SIZE).decode(FORMAT)
    # print(response)

def delete_directory(client, team_name, dir_path, dir_name):
    client.send(f"DELETE_FOLDER\n{team_name}\n{dir_path}\n{dir_name}\r\n".encode(FORMAT))
    # response = client.recv(SIZE).decode(FORMAT)
    # print(response)

def copy_directory(client, team_name, src_path, dir_name, des_path):
    client.send(f"COPY_FOLDER\n{team_name}\n{src_path}\n{dir_name}\n{des_path}\r\n".encode(FORMAT))
    # response = client.recv(SIZE).decode(FORMAT)
    # print(response)

def move_directory(client, team_name, src_path, dir_name, des_path):
    client.send(f"MOVE_FOLDER\n{team_name}\n{src_path}\n{dir_name}\n{des_path}\r\n".encode(FORMAT))
    # response = client.recv(SIZE).decode(FORMAT)
    # print(response)


####################################################################
####################################################################
####################################################################
def login(client, username, password):
    client.send(f"LOGIN\n{username}\n{password}\r\n".encode(FORMAT))
    
def signup(client, username, password, name):
    client.send(f"SIGNUP\n{username}\n{password}\n{name}\r\n".encode(FORMAT))
    # response = client.recv(SIZE).decode(FORMAT)
    # print(f"{response}")

def change_password(client, password, new_password, cf_password):
    client.send(f"CHANGE_PASSWORD\n{password}\n{new_password}\n{cf_password}\r\n".encode(FORMAT))
    # response = client.recv(SIZE).decode(FORMAT)
    # print(response)

def logout(client):
    client.send(f"LOGOUT\r\n".encode(FORMAT))
    # response = client.recv(SIZE).decode(FORMAT)
    # print(f"{response}")

def quit_team(client, team_name):
    client.send(f"QUIT_TEAM\n{team_name}\r\n".encode(FORMAT))
    # response = client.recv(SIZE).decode(FORMAT)
    # print(response)

def remove_member(client, team_name, member_name):
    client.send(f"REMOVE_MEMBER\n{team_name}\n{member_name}\r\n".encode(FORMAT))
    # response = client.recv(SIZE).decode(FORMAT)
    # print(response)

def get_all_user(client):
    client.send(f"GET_ALL_USER\r\n".encode(FORMAT))
    # response = client.recv(SIZE).decode(FORMAT)
    # print(response)

def invite_member(client, team_name, member_name):
    client.send(f"INVITE_MEMBER\n{team_name}\n{member_name}\r\n".encode(FORMAT))
    # response = client.recv(SIZE).decode(FORMAT)
    # print(response)

def get_all_invitations(client):
    client.send(f"GET_ALL_INVITATIONS\r\n".encode(FORMAT))
    # response = client.recv(SIZE).decode(FORMAT)
    # return response

def accept_invitation(client, team_name):
    client.send(f"ACCEPT_INVITATION\n{team_name}\r\n".encode(FORMAT))
    # response = client.recv(SIZE).decode(FORMAT)
    # print(response)


def decline_invitation(client, team_name):
    client.send(f"DECLINE_INVITATION\n{team_name}\r\n".encode(FORMAT))
    # response = client.recv(SIZE).decode(FORMAT)
    # print(response)

def dir_information(client, team_name, path):
    client.send(f"FOLDER_INFORMATION\n{team_name}\n{path}\r\n".encode(FORMAT))
    # response = client.recv(SIZE).decode(FORMAT)
    # print(response)
####################################################################
####################################################################
####################################################################
# NAM
####################################################################
####################################################################
####################################################################
    
def create_team(client, team_name):
    client.send(f"CREATE_TEAM\n{team_name}\r\n".encode(FORMAT))
    # response = client.recv(SIZE).decode(FORMAT)
    # print(response)

def join_team(client, team_code):
    client.send(f"JOIN_TEAM\n{team_code}\r\n".encode(FORMAT))
    # response = client.recv(SIZE).decode(FORMAT)
    # print(response)
    
def get_join_request(client, team_name):
    client.send(f"GET_JOIN_REQUEST\n{team_name}\r\n".encode(FORMAT))
    # response = client.recv(SIZE).decode(FORMAT)
    # print(f"{response}")

def accept_join_request(client, team_name, sender):
    client.send(f"ACCEPT_JOIN_REQUEST\n{team_name}\n{sender}\r\n".encode(FORMAT))
    # response = client.recv(SIZE).decode(FORMAT)
    # print(f"{response}")

def decline_join_request(client, team_name, sender):
    client.send(f"DECLINE_JOIN_REQUEST\n{team_name}\n{sender}\r\n".encode(FORMAT))
    # response = client.recv(SIZE).decode(FORMAT)
    # print(f"{response}")
    
def delete_file(client, team_name, dir_path, filename):
    client.send(f"DELETE_FILE\n{team_name}\n{dir_path}\n{filename}\r\n".encode(FORMAT))
    # response = client.recv(SIZE).decode(FORMAT)
    # print(f"{response}")

def rename_file(client, team_name, dir_path, old_file_name, new_file_name):
    client.send(f"RENAME_FILE\n{team_name}\n{dir_path}\n{old_file_name}\n{new_file_name}\r\n".encode(FORMAT))
    # response = client.recv(SIZE).decode(FORMAT)
    # print(f"{response}")

def copy_file(client, team_name, src_dir, filename, dest_dir):
    client.send(f"COPY_FILE\n{team_name}\n{src_dir}\n{filename}\n{dest_dir}\r\n".encode(FORMAT))
    # response = client.recv(SIZE).decode(FORMAT)
    # print(f"{response}")
    
def move_file(client, team_name, src_dir, filename, dest_dir):
    client.send(f"MOVE_FILE\n{team_name}\n{src_dir}\n{filename}\n{dest_dir}\r\n".encode(FORMAT))
    # response = client.recv(SIZE).decode(FORMAT)
    # print(f"{response}")

####################################################################
####################################################################
####################################################################
def main():
    global client
    if len(sys.argv) != 2:
        print("Usage: python server.py <port>")
        return
    IP = socket.gethostbyname(socket.gethostname())
    PORT = int(sys.argv[1])
    ADDR = (IP, PORT)
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(ADDR)
    data = client.recv(SIZE).decode(FORMAT)
    print(f"{data}")

    while True:
        data = input("> ")
        if len(data) == 0:
            break
        data = data.split("|")
        cmd = data[0]

        if cmd == "LOGIN":
            if len(data) != 3:
                print("Usage: LOGIN|<account>|<password>")
                continue
            else:
                login(client, data[1], data[2])
        elif cmd == "SIGNUP":
            if len(data) != 4:
                print("Usage: SIGNUP|<account>|<password>|<name>")
                continue
            else:
                signup(client, data[1], data[2], data[3])
        elif cmd == "CHANGE_PASSWORD":
            if len(data) != 4:
                print("Usage: CHANGE_PASSWORD|<password>|<new_password>|<cf_password>")
                continue
            else:
                change_password(client, data[1], data[2], data[3])
        elif cmd == "LOGOUT":
            if len(data) != 1:
                print("Usage: LOGOUT")
                continue
            else:
                logout(client)
        elif cmd == "SHOW_MY_TEAMS":
            if len(data) != 1:
                print("Usage: SHOW_MY_TEAMS")
                continue
            else:
                show_my_teams(client)
        elif cmd == "UPLOAD":
            if len(data) != 4:
                print("Usage: UPLOAD|<src_path>|<team_name>|<des_path>")
                continue
            else:
                upload_file(client, data[1], data[2], data[3])
        elif cmd == "DOWNLOAD":
            if len(data) != 4:
                print("Usage: DOWNLOAD|<team_name>|<src_path>|<des_path>")
                continue
            else:
                download_file(client, data[1], data[2], data[3])
        elif cmd == "GET_MEMBER":
            if len(data) != 2:
                print("Usage: GET_MEMBER|<team_name>")
                continue
            else:
                show_team_member(client, data[1])
        elif cmd == "CREATE_FOLDER":
            if len(data) != 4:
                print("Usage: CREATE_FOLDER|<team_name>|<des_path>|<name_folder>")
                continue
            else:
                create_directory(client, data[1], data[2], data[3])
        elif cmd == "RENAME_FOLDER":
            if len(data) != 5:
                print("Usage: RENAME_FOLDER|<team_name>|<des_path>|<name_folder>|<new_name_folder>")
                continue
            else:
                rename_directory(client, data[1], data[2], data[3], data[4])
        elif cmd == "DELETE_FOLDER":
            if len(data) != 4:
                print("Usage: DELETE_FOLDER|<team_name>|<dir_path>|<dir_name>")
                continue
            else:
                delete_directory(client, data[1], data[2], data[3])
        elif cmd == "COPY_FOLDER":
            if len(data) != 5:
                print("Usage: COPY_FOLDER|<team_name>|<src_path>|<dir_name>|<des_path>")
                continue
            else:
                copy_directory(client, data[1], data[2], data[3], data[4])
        elif cmd == "MOVE_FOLDER":
            if len(data) != 5:
                print("Usage: MOVE_FOLDER|<team_name>|<src_path>|<dir_name>|<des_path>")
                continue
            else:
                move_directory(client, data[1], data[2], data[3], data[4])
        elif cmd == "QUIT_TEAM":
            if len(data) != 2:
                print("Usage: QUIT_TEAM|<team_name>")
                continue
            else:
                quit_team(client, data[1])
        elif cmd == "REMOVE_MEMBER":
            if len(data) != 3:
                print("Usage: REMOVE_MEMBER|<team_name>|<member_name>")
                continue
            else:
                remove_member(client, data[1], data[2])
        elif cmd == "GET_ALL_USER":
            if len(data) != 1:
                print("Usage: GET_ALL_USER")
                continue
            else:
                get_all_user(client)
        elif cmd == "INVITE_MEMBER":
            if len(data) != 3:
                print("Usage: INVITE_MEMBER|<team_name>|<member_name>")
                continue
            else:
                invite_member(client, data[1], data[2])
        elif cmd == "GET_ALL_INVITATIONS":
            if len(data) != 1:
                print("Usage: GET_ALL_INVITATIONS")
                continue
            else:
                get_all_invitations(client)
        elif cmd == "ACCEPT_INVITATION":
            if len(data) != 2:
                print("Usage: ACCEPT_INVITATION|<team_name>")
                continue
            else:
                accept_invitation(client, data[1])
        elif cmd == "DECLINE_INVITATION":
            if len(data) != 2:
                print("Usage: DECLINE_INVITATION|<team_name>")
                continue
            else:
                decline_invitation(client, data[1])
        elif cmd == "FOLDER_INFORMATION":
            if len(data) != 3:
                print("Usage: FOLDER_INFORMATION|<team_name>|<path>")
                continue
            else:
                dir_information(client, data[1], data[2])
        elif cmd == "JOIN_TEAM":
            if len(data) != 2:
                print("Usage: JOIN_TEAM|<team_code>")
                continue
            else:
                join_team(client, data[1])
        elif cmd == "CREATE_TEAM":
            if len(data) != 2:
                print("Usage: CREATE_TEAM|<team_name>")
                continue
            else:
                create_team(client, data[1])
        elif cmd == "GET_JOIN_REQUEST":
            if len(data) != 2:
                print("Usage: GET_JOIN_REQUEST|<team_name>")
                continue
            else:
                get_join_request(client, data[1])
        elif cmd == "ACCEPT_JOIN_REQUEST":
            if len(data) != 3:
                print("Usage: ACCEPT_JOIN_REQUEST|<team_name>|<sender>")
                continue
            else:
                accept_join_request(client, data[1], data[2])
        elif cmd == "DECLINE_JOIN_REQUEST":
            if len(data) != 3:
                print("Usage: DECLINE_JOIN_REQUEST|<team_name>|<sender>")
                continue
            else:
                decline_join_request(client, data[1], data[2])
        elif cmd == "DELETE_FILE":
            if len(data) != 4:
                print("Usage: DELETE_FILE|<team_name>|<dir_path>|<filename>")
                continue
            else:
                delete_file(client, data[1], data[2], data[3])
        elif cmd == "RENAME_FILE":
            if len(data) != 5:
                print("Usage: RENAME_FILE|<team_name>|<dir_path>|<old_file_name>|<new_file_name>")
                continue
            else:
                rename_file(client, data[1], data[2], data[3], data[4])
        elif cmd == "COPY_FILE":
            if len(data) != 5:
                print("Usage: COPY_FILE|<team_name>|<src_dir>|<filename>|<dest_dir>")
                continue
            else:
                copy_file(client, data[1], data[2], data[3], data[4])
        elif cmd == "MOVE_FILE":
            if len(data) != 5:
                print("Usage: MOVE_FILE|<team_name>|<src_dir>|<filename>|<dest_dir>")
                continue
            else:
                move_file(client, data[1], data[2], data[3], data[4])
        elif cmd == "QUIT":
            if len(data) != 1:
                print("Usage: QUIT")
                continue
            else:
                client.send(f"QUIT\r\n".encode(FORMAT))
                break
        else:
            send_data = '\n'.join(data) + '\r\n'
            client.send(send_data.encode(FORMAT))

        responseFromServer(client)

    print("Disconnected from the server.")
    client.close()

if __name__ == "__main__":
    main()

