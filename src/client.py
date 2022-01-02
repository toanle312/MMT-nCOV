import time
import socket

HOST = "127.0.0.1"
SERVER_PORT = 52467
FORMAT = "utf8"

def checkServer(client):
    '''
    Hàm kiểm tra xem server có bị mất kết nối đột ngột hay không
    - client: connection của client
    - return: True nếu server còn sống, False nếu bị ngắt
    '''
    try:
        client.sendall("check".encode(FORMAT))
        client.recv(1024).decode(FORMAT)
        return True
    except:
        print("Server is not running")
        return False


def sendList(client, list):
    '''
    Hàm gửi danh sách
    - client: kết nối của client
    - list: danh sách cần gửi
    - return: "no-err" hoặc "err"
    '''
    msgServer = None
    list.append("end")
    for item in list:
        client.sendall(item.encode(FORMAT))
        # Chờ phản hồi từ server
        try:
            msgServer = client.recv(1024).decode(FORMAT)
        except:
            pass
   # msgServer = client.recv(1024).decode(FORMAT)
    return msgServer


def sendOption(client, msgClient, list):
    '''
    Hàm gửi một yêu cầu cụ thể đến server
    - client: kết nối của client
    - msgClient: yêu cầu (option) của client
    - list: danh sách gửi kèm nếu có, không có thì truyền vào rỗng
    '''

    # Kiểm tra xem server có bị mất kết nối đột ngột không
    if(checkServer(client) == False):
        return "stop"

    # Gửi option và kiểm tra có gửi được không
    client.sendall(msgClient.encode(FORMAT))
    msgServer = client.recv(1024).decode(FORMAT)

    # Server phản hồi lại khác thì chưa gửi được
    if(msgServer != msgClient):
        return "stop"

    # Xử lý các option
    # option 1 là login
    if(msgClient == "1" and list != []):
        check = sendList(client, list)
        if(check == "accept"):
            print("Login successed !!!")
            return check

        else:
            print("Login failed !!!")
            return check

    # option 2 is register
    elif(msgClient == "2" and list != []):
        check = sendList(client, list)
        if(check == "accept"):
            print("Register successed !!!")
            return check

        else:
            print("Register failed !!!")
            return check
    # option 3 là tỉnh thành Việt Nam
    elif(msgClient == "3" and list != []):
        check = sendList(client, list)
        if(check != "deny"):
            print(check)
            return check

        else:
            print("Not found !!!")
            return check
    # option 4 là thế giới
    elif(msgClient == "4" and list != []):
        check = sendList(client, list)
        if(check != "deny"):
            print(check)
            return check

        else:
            print("Not found !!!")
            return check


def waitTO(client):
    '''
    Hàm chờ server mở kết nối
    - client: kết nối đã mở của client
    - return: 0 nếu kết nối thành công, 1 nếu quá timeout
    '''

    connectTime = 0
    # client.settimeout(1.0)
    check = client.connect_ex((HOST, SERVER_PORT))

    # Vòng lặp chờ Server mở kết nối
    if(check != 0):
        print("Waiting for Server open the connection ...")
        while(connectTime <= 10 and check != 0):
            check = client.connect_ex((HOST, SERVER_PORT))
            connectTime += 1
            time.sleep(1)

    return check


def connectToServer():
    '''
    Hàm mở kết nối đến server
    - return: một kết nối nếu kết nối thành công đến server
    '''

    print("CLIENT SIDE")

    # Tạo kết nối
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # Chờ time out
        check = client.connect_ex((HOST, SERVER_PORT))
        if(check != 0):
            print("Server is not available !!!")
            return None
        else:
            print("Client address: ", client.getsockname())
            return client
    except:
        print("ERROR !!!")
        print("Server is not opened !!!")
        closeConnection(client)


def closeConnection(client):
    '''
    Hàm đóng kết nối bên phía client
    - client: kết nối của client
    '''

    print("out")
    option = "x"
    client.sendall(option.encode(FORMAT))
    client.close()
