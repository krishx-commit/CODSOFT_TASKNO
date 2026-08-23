import customtkinter as ctk
import math


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.geometry("360x640")
app.title("Simple Mobile Calculator")

#<-------display area----->

frame = ctk.CTkFrame(app,fg_color = "black", corner_radius=10)
frame.pack(padx=10,pady = 20, fill = "x")

inputvar = ctk.StringVar()
outputvar = ctk.StringVar()

inputlabel = ctk.CTkLabel(frame, textvariable=inputvar,font = ("segoe UI", 24),
                          anchor = "e",
                          text_color = "white",
                          height = 50)
inputlabel.pack(fill = "x", padx = 12,pady=(12,4))

outputlabel = ctk.CTkLabel(frame, textvariable=outputvar,font = ("segoe UI", 24,"bold"),
                          anchor = "e",
                          text_color = "white",
                          height = 60)
outputlabel.pack(fill = "x", padx = 12,pady=(0,12))

def press(key):
    if key == "=":
        try:
            expressio = inputvar.get().replace("*","**")
            result = eval(expressio)
            outputvar.set(str(round(result,6)))
        except ZeroDivisionError:
            outputvar.set("Div by 0")
        except:
            outputvar.set("Error")
    elif key == "c":
        inputvar.set("")
        outputvar.set("")
    elif key == "✂":
        inputvar.set(inputvar.get()[:-1])
    elif key == "√":
        try:
            value = float(inputvar.get())
            outputvar.set(str(round(math.sqrt(value),6)))
        except:
            outputvar.set("Error")
    elif key == "log":
        try:
            value = float(inputvar.get())
            outputvar.set(str(round(math.log10(value),6)))
        except:
            outputvar.set("Error")
        else:
            inputlabel.set(inputvar.get() + key)
    else:
        inputvar.set(inputvar.get() + key)

#BUTTONS SECTIONS------>
buttonframe = ctk.CTkFrame(app, fg_color = "Black", corner_radius = 10)
buttonframe.pack(padx= 15,pady=10, fill ="both",expand = True)

buttons = [
    ["c" , "✂" , "%" , "/"],
    ["7", "8", "9" , "*"],
    ["4", "5", "6","-"],
    ["1", "2", "3", "+"],
    ["0","." , "^", "="]
]

def createbutton(txt, row, col):
    color = "#FF9500" if txt == "=" else "#171335"
    button = ctk.CTkButton(buttonframe, text = txt, corner_radius=100,
                           fg_color =color,
                           hover_color = "#161628",
                           font = ("segoe UI",20,"bold"),
                           text_color = "#ffffff",
                           command = lambda: press(txt)
                           )
    button.grid(row = row, column = col, sticky = "nsew", padx = 5, pady = 5)
    
# CREATE AND PLACING---->
for r, rowvalues in enumerate(buttons):
    for c, char in enumerate(rowvalues):
        createbutton(char, r,c)
        
#SIZING----->
for i in range(5):
    buttonframe.rowconfigure(i,weight = 1)
for j in range(4):
   buttonframe.columnconfigure(j,weight = 1)


app.mainloop()