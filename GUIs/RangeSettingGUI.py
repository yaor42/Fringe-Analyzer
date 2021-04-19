import tkinter as tk


class RangeSettingGUI:
    max_value = None
    min_value = None

    is_valid = False

    def __init__(self, root):
        self.root = root

        self.min_value = self.root.min_value
        self.max_value = self.root.max_value

        self.var_min = tk.StringVar()
        self.var_max = tk.StringVar()
        self.var_min.set(str(self.min_value))
        self.var_max.set(str(self.max_value))

        self.window = tk.Toplevel(master=self.root.window)
        self.window.title(f"Range Setting")

        self.frm_var = tk.Frame(master=self.window)

        self.lbl_min = tk.Label(master=self.frm_var, text="Min: ")
        self.lbl_max = tk.Label(master=self.frm_var, text="Max: ")
        self.ent_min = tk.Entry(master=self.frm_var, textvariable=self.var_min, width=10)
        self.ent_max = tk.Entry(master=self.frm_var, textvariable=self.var_max, width=10)

        self.lbl_min.grid(row=0, column=0, padx=(5, 0), pady=10)
        self.ent_min.grid(row=0, column=1, padx=5, pady=10)
        self.lbl_max.grid(row=0, column=2, padx=(5, 0), pady=10)
        self.ent_max.grid(row=0, column=3, padx=5, pady=10)

        self.frm_var.pack()

        self.frm_button = tk.Frame(master=self.window)

        self.btn_cancel = tk.Button(master=self.frm_button, text="Cancel", command=self.cancel)
        self.btn_submit = tk.Button(master=self.frm_button, text="Submit", command=self.submit)

        self.btn_cancel.pack(side=tk.LEFT, padx=5, pady=(0, 5))
        self.btn_submit.pack(side=tk.RIGHT, padx=5, pady=(0, 5))

        self.frm_button.pack()

    def cancel(self):
        self.window.destroy()

    def submit(self):
        if self.var_min.get() and self.var_max.get():
            self.is_valid = True
            self.min_value = float(self.var_min.get())
            self.max_value = float(self.var_max.get())
        else:
            self.is_valid = False

        self.window.destroy()
