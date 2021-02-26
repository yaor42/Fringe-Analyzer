import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import askdirectory

import matplotlib
import numpy as np


class ExportGUI:
    def __init__(self, root, filetype="image", export_all=False, track=False):
        self.root = root

        self.string_var_dir = tk.StringVar()
        self.string_var_filename = tk.StringVar()
        self.string_var_filename.set("Sample")
        self.string_var_filetype = tk.StringVar()

        self.window = tk.Toplevel(master=self.root.window)

        if track:
            self.window.title(f"Point Tracking: ({self.root.x_cache}, {self.root.y_cache})")
        else:
            if filetype == "image":
                self.window.title("Export as Image")
            else:
                self.window.title("Export as CSV")

        self.frm_main = tk.Frame(master=self.window)

        self.lbl_dir_text = tk.Label(master=self.frm_main, text="Directory")
        self.lbl_dir = tk.Label(master=self.frm_main, textvariable=self.string_var_dir, width=50, relief="sunken")
        self.btn_dir = tk.Button(master=self.frm_main, text="Choose Directory", command=self.select_dir)
        self.lbl_dir_text.grid(row=0, column=0, padx=5, pady=5)
        self.lbl_dir.grid(row=1, column=0, padx=(5, 1), pady=5)
        self.btn_dir.grid(row=2, column=0, padx=5, pady=5)

        self.lbl_slash = tk.Label(master=self.frm_main, text='/')
        self.lbl_slash.grid(row=1, column=1, padx=1, pady=5)

        self.lbl_filename_text = tk.Label(master=self.frm_main, text="File Name")
        self.ent_filename = tk.Entry(master=self.frm_main, textvariable=self.string_var_filename)
        self.lbl_filename_text.grid(row=1, column=2, padx=5, pady=5)
        self.ent_filename.grid(row=1, column=2, padx=1, pady=5)

        if export_all:
            self.lbl_num = tk.Label(master=self.frm_main, text="-n")
            self.lbl_num.grid(row=1, column=3, pady=5)

        self.lbl_filetype_text = tk.Label(master=self.frm_main, text="Extension")
        self.lbl_filetype_text.grid(row=0, column=4, padx=5, pady=5)

        if filetype == "image":
            self.cbo_filetype = ttk.Combobox(
                master=self.frm_main,
                value=['.bmp', '.jpg', '.png', '.gif', '.svg'],
                textvariable=self.string_var_filetype
            )
            self.cbo_filetype.grid(row=1, column=4, padx=(1, 5), pady=5)
        else:
            self.string_var_filetype.set(".csv")
            self.lbl_filetype = tk.Label(master=self.frm_main, textvariable=self.string_var_filetype)
            self.lbl_filetype.grid(row=1, column=4, padx=(1, 5), pady=5)

        self.frm_btn = tk.Frame(master=self.frm_main)
        self.btn_cancel = tk.Button(master=self.frm_btn, text='Cancel', command=self.cancel)
        self.btn_save = tk.Button(master=self.frm_btn, text=' Save ')
        self.btn_cancel.grid(row=1, column=0, padx=5, pady=5)
        self.btn_save.grid(row=1, column=1, padx=5, pady=5)

        if track:
            self.btn_save.configure(command=self.track_point)
        elif filetype == "image":
            if export_all:
                self.btn_save.configure(command=self.save_image_all)
            else:
                self.btn_save.configure(command=self.save_image)
        else:
            if export_all:
                self.btn_save.configure(command=self.save_csv_all)
            else:
                self.btn_save.configure(command=self.save_csv)

        self.frm_btn.grid(row=2, column=4, padx=5, pady=5)

        self.frm_main.pack()

        # Set the window not resizable so the layout would not be destroyed
        self.window.resizable(False, False)

    def select_dir(self):
        self.string_var_dir.set(askdirectory())

        self.window.lift()

    def cancel(self):
        self.window.destroy()

    def save_image(self):
        full_dir = f"{self.string_var_dir.get()}/{self.string_var_filename.get()}{self.string_var_filetype.get()}"

        matplotlib.image.imsave(full_dir, self.root.curr_map)

        self.cancel()

    def save_image_all(self):
        selected_map = self.root.cbo_map.get()

        if selected_map == 'Object Surface Contour':
            map_list = self.root.depth_map
        elif selected_map == 'Wrapped Phase Map':
            map_list = self.root.diff_phase
        elif selected_map == 'Object Phase':
            map_list = self.root.obj_phase

        for index in range(len(map_list)):
            full_dir = f"{self.string_var_dir.get()}/{self.string_var_filename.get()}-{index + 1}" \
                       f"{self.string_var_filetype.get()}"
            matplotlib.image.imsave(full_dir, map_list[index])

        self.cancel()

    def save_csv(self):
        full_dir = f"{self.string_var_dir.get()}/{self.string_var_filename.get()}{self.string_var_filetype.get()}"

        np.savetxt(full_dir, self.root.curr_map, delimiter=", ")

        self.cancel()

    def save_csv_all(self):
        selected_map = self.root.cbo_map.get()

        if selected_map == 'Object Surface Contour':
            map_list = self.root.depth_map
        elif selected_map == 'Wrapped Phase Map':
            map_list = self.root.diff_phase
        elif selected_map == 'Object Phase':
            map_list = self.root.obj_phase

        for index in range(len(map_list)):
            full_dir = f"{self.string_var_dir.get()}/{self.string_var_filename.get()}-{index + 1}" \
                       f"{self.string_var_filetype.get()}"
            np.savetxt(full_dir, map_list[index], delimiter=", ")

        self.cancel()

    def track_point(self):
        x = self.root.x_cache
        y = self.root.y_cache

        map_list = self.root.depth_map
        data = np.array([depth_map[x][y] for depth_map in map_list])

        full_dir = f"{self.string_var_dir.get()}/{self.string_var_filename.get()}{self.string_var_filetype.get()}"
        np.savetxt(full_dir, data, delimiter=", ")

        self.cancel()
