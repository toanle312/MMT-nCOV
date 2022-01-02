from tkinter import  StringVar, messagebox
from tkinter.constants import END
from tkinter import ttk
import threading
import api
import re
import tkinter as tk
import server as se


window = tk.Tk()

window.title("nCovi_server")
window.geometry("720x480")
window.resizable(width=False, height=False)

frame2 = tk.Frame(window)


def close_App(server):
    '''
    Thoát chương trình
    - server: kết nối của server
    '''
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        se.closeServer(server)
        window.destroy()

def homePage():

    '''
    Trang chính
    '''
    
    sThread = se.threading.Thread(target=se.openServer)
    sThread.daemon = True 
    sThread.start() 

    frame2.pack(fill="both", expand=1)
    page_name = tk.Label(frame2, text="SERVER", font=("Georgia",20), foreground="blue")
    page_name.place(x=245)
    

    quit_button = tk.Button(frame2, text='Quit',width=10, command=lambda:close_App(se.s))
    quit_button.place(x=600,y = 10)
    
    def seeConnection():
        txt.delete(0, len(se.live_account))
        for i in range(len(se.live_account)):
            txt.insert(i, se.live_account[i])

    
    user_info = tk.Label(frame2, text=("Server: " + str(se.HOST) + "  -  " + str(se.SERVER_PORT)))
    user_info.place(x=220, y=55)
    refresh_button = tk.Button(frame2,text = 'REFRESH', bg='blue',width=15, command=seeConnection)
    refresh_button.place(x = 280, y=430)
    
    global txt
    txt = tk.Listbox(frame2,font=("Arial",15), width=45, height=12)
    scrollbar  = tk.Scrollbar(frame2, orient="vertical", command=txt.yview)
    txt['yscroll'] = scrollbar.set
    scrollbar.place(in_=txt, relx=1.0, relheight=1.0, bordermode="outside")
    txt.place(x=100, y=80)

homePage()
window.mainloop()