from tkinter.constants import ANCHOR, BOTH, CENTER, INSERT, LEFT, RIGHT, TRUE
from tkinter import StringVar, messagebox
from calendar import calendar, month
from tkcalendar import DateEntry
from datetime import datetime
from tkinter import ttk
import re
import tkinter as tk
import client as cl
import server as se


global window
window = tk.Tk()

window.title("nCovi_client")
window.geometry("720x480")
window.resizable(width=False, height=False)

frame2 = tk.Frame(window)
frame1 = tk.Frame(window)
frame3 = tk.Frame(window)
frame4 = tk.Frame(window)


def check_login(connect):
    '''
    kiểm tra đăng nhập
    - connect: kết nối của client
    '''
    
    account = []

    username = entry_username.get()
    password = entry_password.get()

    account.append(username)
    account.append(password)

    if(username == "" or password == ""):
        messagebox.showinfo("Warning", "Blank not allowed")
    elif (len(username) >= 30) or (len(password) >= 30):
        messagebox.showinfo("Warning", "Too much character" + "\n" +
                            "The username or password must less than 30 character")
    elif not (re.match("^[a-zA-Z0-9]*$", username) and re.match("^[a-zA-Z0-9]*$", password)):
        messagebox.showinfo("Warning", "Error! Only letters a-z allowed!")
    else:
        check = cl.sendOption(connect, "1", account)
        if check == "stop":
            messagebox.showinfo("Warning", "server is not running")
        elif check == "accept":
            homePage(connect)
        else:
            messagebox.showinfo("Warning", "username or password is incorrect")

def create_Account(connect):
    '''
    Đăng kí tài khoản
    - connect: kết nối của client
    '''
    
    account_send = []

    username = sign_up_usn.get()
    password = sign_up_psw.get()
    confirm_password = pws_confirm.get()

    if(username == "" or password == ""):
        messagebox.showinfo("Warning", "Blank not allowed")
    elif (len(username) >= 30) or (len(password) >= 30):
        messagebox.showinfo("Warning", "Too much character" + "\n" +
                            "The username or password must less than 30 character")
    elif not (re.match("^[a-zA-Z0-9]*$", username) and re.match("^[a-zA-Z0-9]*$", password)):
        messagebox.showinfo("", "Error! Only letters a-z allowed!")
    else:
        if confirm_password == password:
            account_send.append(username)
            account_send.append(password)
            check = cl.sendOption(connect, "2", account_send)
            if check == "stop":
                messagebox.showinfo("Warning", "server is not running")
            elif check == "accept":
                homePage(connect)
            else:
                messagebox.showinfo("Warning", "The account already exists")
                startPage(connect)
        else:
            messagebox.showinfo("Warning", "Incorrect password !")


def registerPage(connect):
    '''
    Trang đăng ký
    - connect: kết nối của client
    '''
    
    hide_frame()

    global sign_up_psw
    global sign_up_usn
    global pws_confirm

    sign_up_psw = StringVar()
    sign_up_usn = StringVar()
    pws_confirm = StringVar()

    label_page = tk.Label(frame3, text="SIGN UP", font=(
        "Georgia", 20), foreground='blue')

    label_username = tk.Label(frame3, text="Username", height=2)
    sign_up_usn = tk.Entry(frame3, width=30)

    label_password = tk.Label(frame3, text="Password", height=2)
    sign_up_psw = tk.Entry(frame3, width=30)

    label_confirm = tk.Label(frame3, text="Confirm", height=2)
    pws_confirm = tk.Entry(frame3, width=30)

    button_login = tk.Button(frame3, text="Login",
                             width=10, bg='cyan', command=lambda: create_Account(connect))

    frame3.pack(fill="both", expand=1)

    label_page.place(x=300, y=15)
    label_username.place(x=200, y=50)
    sign_up_usn.place(x=270, y=58)
    label_password.place(x=200, y=90)
    sign_up_psw.place(x=270, y=98)
    label_confirm.place(x=200, y=130)
    pws_confirm.place(x=270, y=138)
    button_login.place(x=300, y=168)

def hide_frame():
    '''
    Ẩn frame cũ khi chuyển frame
    '''
    frame1.pack_forget()
    frame2.pack_forget()
    frame3.pack_forget()
    frame4.pack_forget()



def startPage(connect):
    '''
    Đây là trang đăng nhập
    '''
    
    hide_frame()

    global entry_username
    global entry_password

    entry_password = StringVar()
    entry_username = StringVar()

    app_name = tk.Label(frame1, text="nCovi",
                        font=("Georgia", 20), foreground='blue')
    label_username = tk.Label(frame1, text="Username", height=2)
    entry_username = tk.Entry(frame1, width=30)
    label_password = tk.Label(frame1, text="Password", height=2)
    entry_password = tk.Entry(frame1, width=30)
    button_login = tk.Button(frame1, text="Login",
                             width=10, bg='cyan', command=lambda: check_login(connect))
    button_register = tk.Button(
        frame1, text="Register", width=10, bg='cyan', command=lambda: registerPage(connect))

    frame1.pack(fill=BOTH, expand=1)

    app_name.place(x=310)

    label_username.place(x=190, y=50)
    entry_username.place(x=260, y=60)
    label_password.place(x=190, y=90)
    entry_password.place(x=260, y=100)
    entry_password.config(show='*')
    button_login.place(x=240, y=130)
    button_register.place(x=350, y=130)


def validateIP(s):
    '''
    Kiểm tra tính hợp lệ của địa chỉ IP nhập vào
    - s: IP
    - return: True nếu hợp lệ
    '''
    a = s.split('.')
    if len(a) != 4:
        return False
    for x in a:
        if not x.isdigit():
            return False
        i = int(x)
        if i < 0 or i > 255:
            return False
    if(s == "192.168.1.1"):
        return False
    return True


def getIP_page():
    '''
    Trang nhập địa chỉ IP
    '''
    
    ip_entry = StringVar()
    ip_input = tk.Label(frame4, text="IP INPUT", font=(
        "Georgia", 20), foreground='blue')
    ip_entry = tk.Entry(frame4, width=30, font=("Arial", 12))
    ok_btn = tk.Button(frame4, width=10, text="OK",
                       bg="cyan", command=lambda: checkIP())

    def checkIP():
        '''
        Kiểm tra IP và tạo kết nối
        '''
        
        IP = ip_entry.get()
        cl.HOST = IP
        if(validateIP(cl.HOST)):
            connect = cl.connectToServer()
            if(connect != None):
                startPage(connect)
            else:
                messagebox.showinfo("Warning", "Server is not available")
                getIP_page()
        else:
            messagebox.showinfo("Warning", "IP Sever is incorrect")

    frame4.pack(fill=BOTH, expand=1)
    ip_input.place(x=280, y=50)
    ip_entry.place(x=210, y=100)
    ok_btn.place(x=300, y=130)



def get_info(connect):
    '''
    Lấy thông tin covid theo địa điểm
    - connect: kết nối của client
    '''
    information = []  # chứa vị trí và ngày
    info_page.delete(0.0, 'end')
    text_1 = info_entry.get()
    time = my_date.get_date()
    str_time = time.strftime("%Y-%m-%d")

    selected = drop.get()

    if selected == "Search by.....":
        info_page.insert(0.0, "You forgot to pick a dropdown menu!")
    elif selected == "World":
        information.append(text_1)
        information.append(str_time)
        str_name = cl.sendOption(connect, "4", information)
        if str_name == "stop":
            messagebox.showinfo("Warning", "server is not running")
            return
        elif str_name =="deny":
            str_name = "Not found"
        info_page.insert(0.0, str_name)

    elif selected == "Viet Nam":
        information.append(text_1)
        str_name = cl.sendOption(connect, "3", information)
        if str_name == "stop":
            messagebox.showinfo("Warning", "server is not running")
        elif str_name =="deny":
            str_name = "Not found"
        info_page.insert(0.0, str_name)


def close_App(connect):
    '''
    Thoát chương trình
    - connect: kết nối của client
    '''
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        window.destroy()
        cl.closeConnection(connect)


def homePage(connect):
    ''' 
    Đây là trang xem thông tin
    - connect: kết nối của client
    '''
    hide_frame()

    label_title = tk.Label(frame2, text='Home Page',
                           font=("Georgia", 20), foreground="blue")
    logout_button = tk.Button(frame2, text='Logout',
                              width=10, command=lambda: startPage(connect))

    global info_entry
    global info_page
    global drop
    global my_date
    info_entry = StringVar()
    my_date = StringVar()

    info_entry = tk.Entry(frame2, width=30)
    info_page = tk.Text(frame2, font=("Arial", 12), width=60, height=15)
    info_page.insert(0.0, "write without accents ")

    ok_button = tk.Button(frame2, text="Ok", width=5,
                          bg="cyan", command=lambda: get_info(connect))
    quit_button = tk.Button(frame2, text='Quit', width=10,
                            command=lambda: close_App(connect))
    # combobox
    drop = ttk.Combobox(frame2, values=["Search by.....", "World", "Viet Nam"])
    drop.current(0)
    # date picker
    my_date = DateEntry(frame2, selectmode='day', year=2022, month=1, day=3)

    def click(event):
        info_entry.configure(state="normal")
        info_entry.delete(0, "end")

    frame2.pack(fill=BOTH, expand=1)

    my_date.place(x=350, y=50)
    label_title.place(x=10, y=5)
    logout_button.place(x=600, y=10)
    info_page.place(x=100, y=100)
    info_entry.place(x=10, y=50)
    info_entry.insert(0, "enter your location")
    info_entry.configure(state="disabled")
    info_entry.bind("<Button-1>", click)
    ok_button.place(x=450, y=47)
    quit_button.place(x=600, y=45)
    drop.place(x=200, y=50)

getIP_page()
window.mainloop()
