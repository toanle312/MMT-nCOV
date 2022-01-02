from tkinter.constants import NO
import database as db
import threading
import socket
import api

HOST = socket.gethostbyname(socket.gethostname())
# HOST = "127.0.0.1"
SERVER_PORT = 52467
FORMAT = "utf8"

live_account = []


def recvList(connection, option):
    '''
    Hàm nhận danh sách từ phía client theo một option cho trước
    - connection: kết nối mà server đã mở với client
    - option: tùy chọn loại thông tin
    '''

    list = []
    item = None
    msgServer = "deny"
    while(item != "end"):
        item = connection.recv(1024).decode(FORMAT)
        if(item != "end"):
            list.append(item)
        else:
            # In để kiểm tra
            print(list)
            # Nếu option = 1 thì đi đến hàm login
            if(option == 1):
                if(db.checkAccount(list) == True):
                    msgServer = "accept"
            # nếu option = 0 thì đi đến hàm regis
            elif(option == 2):
                if(db.createAccount(list) == True):
                    msgServer = "accept"
            # Lây thông tin tỉnh thành Việt Nam
            elif(option == 3):
                str = list[0]
                if(api.covidDictToString(api.getProvinceData(str), 2)):
                    msgServer = api.covidDictToString(
                        api.getProvinceData(str), 2)
            # Lấy thông tin thế giới
            elif(option == 4):
                str = list[0]
                date = list[1]
                if(api.covidDictToString(api.getCountryData(str, date), 1)):
                    msgServer = api.covidDictToString(
                        api.getCountryData(str, date), 1)

        # Gửi hồi đáp cho bên client
        connection.sendall(msgServer.encode(FORMAT))


def removeAccount(connection, address):
    for address in live_account:
        live_account.remove(str(address))
        connection.sendall("True".encode(FORMAT))


def handleClient(connection, address):  # Xử lý đa luồng
    '''
    Hàm xử lý đa luồng cho mỗi kết nối của client
    - connection: kết nối của client
    - address: địa chỉ IP và port của client
    '''

    print("Client ", address, " connected !!!")
    print("Connection", connection.getsockname())
    temp = "running"
    live_account.append(str(address))

    # msgClient = None

    try:
        while(temp == "running"):

            msgClient = connection.recv(1024).decode(FORMAT)
            # print("Client", address, "says: ", msgClient)
            connection.sendall(msgClient.encode(FORMAT))

            if(msgClient == "1"):
                # Chỉ gửi tin mà không dừng vòng lặp này
                recvList(connection, 1)
            elif(msgClient == "2"):
                recvList(connection, 2)
            elif(msgClient == "3"):
                recvList(connection, 3)
            elif(msgClient == "4"):
                recvList(connection, 4)
            elif(msgClient == "check"):
                pass
            else:
                temp = "stop"

        print("Client: ", address, " is disconnected !!!")
        print(connection.getsockname(), " closed !!!")
        removeAccount(connection, address)
        connection.close()

    except:
        connection.close()


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


def updateDB():
    check = False

    while(1):
        if(db.isUpdated() == -1):
            api.fetchData()
            check = False
        elif(db.isUpdated == 0):
            if(check == False):
                print("Datetime file is error")
            check = True
        else:
            if(check == False):
                print("Database is already updated")
            check = True


def openServer():

    print("SERVER SIDE")
    print("Server: ", HOST, SERVER_PORT)
    print("Waiting for Client ...")

    try:
        s.bind((HOST, SERVER_PORT))
        s.listen()

        # Cập nhật cơ sở dữ liệu
        thrApi = threading.Thread(target=updateDB)
        thrApi.start()

        while(1):
            try:
                global address
                global connection

                connection, address = s.accept()
                thr = threading.Thread(target=handleClient,
                                       args=(connection, address))
                thr.daemon = True
                thr.start()
            except:
                print("Server is closed !!!")
                break

    except:
        print("Server is already opened")


def closeServer(s):
    print("\t--- END SERVER ---")
    s.close()
