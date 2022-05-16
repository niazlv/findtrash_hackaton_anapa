from tkinter import *
from tkinter.filedialog import askopenfilename
from main import *
from PIL import ImageTk,Image  

window = Tk()

def openfile__():
    filename = askopenfilename(title="Найдите видео для загрузки...",filetypes=[("videos",(".avi",".mp4")),("All types",".*")])
    print(filename)
    get_garbage(filename)
    destroy_object = [lbl, btn]
    for object_name in destroy_object:
        if object_name.winfo_viewable():
            object_name.grid_remove()
        else:
            object_name.grid()
    cam = "1"
    if getStatus() < 3:
        comm = "\nВсе чисто"
    else:
        comm = "\nНадо убрать мусор!"
    coord = "28.159.2N 28.14W"
    adr = "Ул. Пушкина, дом 9"
    width = 100
    height = 100
    img = Image.open("result_standard_preview.png")
    img = img.resize((width,height), Image.ANTIALIAS)
    img = ImageTk.PhotoImage(img)

    img1 = Image.open("img_last.png")
    img1 = img1.resize((width,height), Image.ANTIALIAS)
    img1 = ImageTk.PhotoImage(img1)

    canvas = Canvas(window, width = width, height = height)
    canvas1 = Canvas(window, width = width, height = height)
    #canvas.pack()
    #canvas1.pack()
    canvas.grid(column=0,row=0)
    canvas1.grid(column=1,row=0)
    canvas.create_image(0,0,anchor=NW, image=img)
    canvas.image = img

    canvas1.create_image(0,0,anchor=NW, image=img1)
    canvas1.image = img1

    if getStatus()>5:
        nc = nc = Label(window,text="Степень загрязнения: "+str(4))
    else:
        nc = Label(window,text="Степень загрязнения: "+str(getStatus()))
    nc.grid(column=0,row=1)
    #nc.pack()

    camera = Label(window, text="Камера: "+cam)
    camera.grid(column=0,row=2)
    #camera.pack()

    comment = Label(window,text="Коментарий: "+comm)
    comment.grid(column=0,row=3)
    #comment.pack()

    coords = Label(window,text="Координаты: "+coord)
    coords.grid(column=0,row=4)
    #coords.pack()

    address = Label(window,text="Адрес: "+adr)
    address.grid(column=0,row=5)
    #address.pack()


window.title("загрязнение")
window.geometry('400x250')
lbl = Label(window, text=" ")
lbl.grid(column=0, row=0)
btn = Button(window, text="Open file...", command=openfile__)
btn.grid()

window.mainloop()
