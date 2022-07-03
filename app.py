import tkinter as tk
from tkinter import ttk


root = tk.Tk()
root.resizable(0,0)

root.style = ttk.Style()
# ('clam', 'alt', 'default', 'classic')
root.style.theme_use("clam")

menu = tk.Menu(root)
root.config(menu=menu)

fm = tk.Menu(menu, tearoff=0)
menu.add_cascade(label="Settings",menu=fm)
fm.add_command(label="Preferances")

hm = tk.Menu(menu, tearoff=0)
menu.add_cascade(label="Help",menu=hm)
hm.add_command(label="About", command=about_window)
hm.add_command(label="Exit",command=root.quit)
#

tk.mainloop()