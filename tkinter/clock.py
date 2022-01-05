import tkinter
from time import strftime

#初始化ui
top = tkinter.Tk()
#设置APP标题
top.title('Clock')
#限制拉伸窗口大小
top.resizable(0,0)

def time():
    string = strftime('%H:%M:%S %p')
    clockTime.config(text = string)
    clockTime.after(1000, time)


clockTime = tkinter.Label(top, font = ('calibri', 40, 'bold'), background = 'black', foreground = 'white')

clockTime.pack(anchor = 'center')
time()


top.mainloop()
