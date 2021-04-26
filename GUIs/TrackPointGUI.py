import tkinter as tk


class TrackPointGUI:
    x = 0
    y = 0

    is_valid = False

    def __init__(self, root):
        self.root = root

        self.x = self.root.cache_x
        self.y = self.root.cache_y

        self.var_x = tk.IntVar()
        self.var_y = tk.IntVar()
        self.var_x.set(self.x)
        self.var_y.set(self.y)

        self.window = tk.Toplevel(master=self.root.window)
        self.window.title(f"Track")

        self.frm_coord = tk.Frame(master=self.window)

        self.lbl_x = tk.Label(master=self.frm_coord, text="x: ")
        self.lbl_y = tk.Label(master=self.frm_coord, text="y: ")
        self.ent_x = tk.Entry(master=self.frm_coord, textvariable=self.var_x, width=10)
        self.ent_y = tk.Entry(master=self.frm_coord, textvariable=self.var_y, width=10)

        self.lbl_x.grid(row=0, column=0, padx=(5, 0), pady=10)
        self.ent_x.grid(row=0, column=1, padx=5, pady=10)
        self.lbl_y.grid(row=0, column=2, padx=(5, 0), pady=10)
        self.ent_y.grid(row=0, column=3, padx=5, pady=10)

        self.frm_coord.pack()

        self.frm_button = tk.Frame(master=self.window)

        self.btn_cancel = tk.Button(master=self.frm_button, text="Cancel", command=self.cancel)
        self.btn_submit = tk.Button(master=self.frm_button, text="Submit", command=self.submit)

        self.btn_cancel.pack(side=tk.LEFT, padx=5, pady=(0, 5))
        self.btn_submit.pack(side=tk.RIGHT, padx=5, pady=(0, 5))

        self.frm_button.pack()

        self.window.resizable(False, False)

    def cancel(self):
        self.window.destroy()

    def submit(self):
        if self.var_x.get() and self.var_y.get():
            self.is_valid = True
            self.x = self.var_x.get()
            self.y = self.var_y.get()
        else:
            self.is_valid = False

        self.window.destroy()
