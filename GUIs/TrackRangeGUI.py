import tkinter as tk
from tkinter import ttk

import cv2
import matplotlib
from matplotlib import cm
from matplotlib.backend_bases import MouseButton
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle


class TrackRangeGUI:
    is_valid = False

    plot = None
    ax = None

    patch = None

    x1 = None
    y1 = None
    x2 = None
    y2 = None

    is_drawing = False
    is_dragging = False

    cache_x1 = None
    cache_y1 = None
    cache_x2 = None
    cache_y2 = None

    drag_x = None
    drag_y = None

    def __init__(self, root):
        self.root = root

        self.window = tk.Toplevel(master=root.window)

        self.frm_left = tk.Frame(master=self.window)
        self.frm_right = tk.Frame(master=self.window)

        self.fig = Figure(figsize=(5, 5), facecolor='#F0F0F0')

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frm_left)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.canvas.mpl_connect('button_press_event', self.on_press)
        self.canvas.mpl_connect('motion_notify_event', self.on_move)
        self.canvas.mpl_connect('button_release_event', self.on_release)

        self.frm_left.grid(row=0, column=0, ipadx=5, ipady=5)

        self.cbo_display = ttk.Combobox(master=self.frm_right, value=['Reference Image',
                                                                      'Original Image',
                                                                      'Depth Map'])
        self.cbo_display.bind("<<ComboboxSelected>>", self.set_display)
        self.cbo_display.current(2)

        self.cbo_display.grid(row=0, column=0, ipadx=5, ipady=5)

        self.frm_input = tk.Frame(master=self.frm_right)

        self.var_x1 = tk.IntVar()
        self.var_y1 = tk.IntVar()
        self.var_x2 = tk.IntVar()
        self.var_y2 = tk.IntVar()

        self.lbl_x1 = tk.Label(master=self.frm_input, text="x1: ")
        self.lbl_y1 = tk.Label(master=self.frm_input, text="y1: ")
        self.lbl_x2 = tk.Label(master=self.frm_input, text="x2: ")
        self.lbl_y2 = tk.Label(master=self.frm_input, text="y2: ")

        self.ent_x1 = tk.Entry(master=self.frm_input, textvariable=self.var_x1, width=10)
        self.ent_y1 = tk.Entry(master=self.frm_input, textvariable=self.var_y1, width=10)
        self.ent_x2 = tk.Entry(master=self.frm_input, textvariable=self.var_x2, width=10)
        self.ent_y2 = tk.Entry(master=self.frm_input, textvariable=self.var_y2, width=10)

        self.lbl_x1.grid(row=0, column=0, ipadx=5, ipady=5)
        self.ent_x1.grid(row=0, column=1, ipadx=5, ipady=5)
        self.lbl_y1.grid(row=0, column=2, ipadx=5, ipady=5)
        self.ent_y1.grid(row=0, column=3, ipadx=5, ipady=5)
        self.lbl_x2.grid(row=1, column=0, ipadx=5, ipady=5)
        self.ent_x2.grid(row=1, column=1, ipadx=5, ipady=5)
        self.lbl_y2.grid(row=1, column=2, ipadx=5, ipady=5)
        self.ent_y2.grid(row=1, column=3, ipadx=5, ipady=5)

        self.btn_apply = tk.Button(master=self.frm_input, text="Apply", command=self.draw)
        self.btn_apply.grid(row=2, column=3, ipadx=5, ipady=5)

        self.frm_input.grid(row=1, column=0, ipadx=5, ipady=5)

        self.frm_right.grid(row=0, column=1, ipadx=5, ipady=5)

        self.frm_submit = tk.Frame(master=self.window)

        self.btn_cancel = tk.Button(master=self.frm_submit, text="Cancel", command=self.cancel)
        self.btn_submit = tk.Button(master=self.frm_submit, text="Submit", command=self.submit)

        self.btn_cancel.grid(row=0, column=0, ipadx=5, ipady=5, padx=5)
        self.btn_submit.grid(row=0, column=1, ipadx=5, ipady=5, padx=5)

        self.frm_submit.grid(row=1, column=1, ipadx=5, ipady=5)

        self.draw()

    def draw(self):
        if self.patch is not None:
            self.patch.remove()

        if self.ax is not None:
            self.ax.remove()

        self.ax = self.fig.add_subplot(111)

        if self.cbo_display.get() == 'Reference Image':
            self.plot = self.ax.imshow(cv2.imread(self.root.ref_file, cv2.IMREAD_GRAYSCALE), cmap=cm.gray)
        elif self.cbo_display.get() == 'Original Image':
            self.plot = self.ax.imshow(
                cv2.imread(self.root.obj_file[self.root.scl_main.get() - 1], cv2.IMREAD_GRAYSCALE),
                cmap=cm.gray
            )
        else:
            self.plot = self.ax.imshow(self.root.curr_map, vmax=self.root.max_value,
                                       vmin=self.root.min_value, cmap=cm.turbo)

        x1 = self.var_x1.get()
        y1 = self.var_y1.get()
        x2 = self.var_x2.get()
        y2 = self.var_y2.get()

        self.patch = Rectangle((x1, y2), width=x2 - x1, height=y1 - y2, facecolor='none', edgecolor='black')
        self.patch = self.ax.add_patch(self.patch)

        self.canvas.draw()

    def set_display(self, _event=None):
        self.draw()

    def on_press(self, event):
        if event.button == MouseButton.LEFT:
            self.is_drawing = True
            self.cache_x1 = event.xdata
            self.cache_y1 = event.ydata
            self.cache_x2 = event.xdata
            self.cache_y2 = event.ydata

        elif event.button == MouseButton.RIGHT:
            self.is_dragging = True
            self.drag_x = event.xdata
            self.drag_y = event.ydata

    def on_move(self, event):
        if event.button == MouseButton.LEFT and self.is_drawing:
            self.update_rectangle(event)
        elif event.button == MouseButton.RIGHT and self.is_dragging:
            self.move_rectangle(event)

    def on_release(self, event):
        if event.button == MouseButton.LEFT:
            self.is_drawing = False
            self.update_rectangle(event)
        elif event.button == MouseButton.RIGHT:
            self.is_dragging = False
            self.move_rectangle(event)

    def move_rectangle(self, event):
        move_x = int(event.xdata - self.drag_x)
        move_y = int(event.ydata - self.drag_y)

        self.drag_x = event.xdata
        self.drag_y = event.ydata

        self.var_x1.set(self.var_x1.get() + move_x)
        self.var_y1.set(self.var_y1.get() + move_y)
        self.var_x2.set(self.var_x2.get() + move_x)
        self.var_y2.set(self.var_y2.get() + move_y)

        self.draw()

    def update_rectangle(self, event):
        self.cache_x2 = event.xdata
        self.cache_y2 = event.ydata

        self.var_x1.set(int(min(self.cache_x1, self.cache_x2)))
        self.var_y1.set(int(min(self.cache_y1, self.cache_y2)))
        self.var_x2.set(int(max(self.cache_x1, self.cache_x2)))
        self.var_y2.set(int(max(self.cache_y1, self.cache_y2)))

        self.draw()

    def cancel(self):
        self.window.destroy()

    def submit(self):
        if self.var_x1.get() and self.var_y1.get() and self.var_x2.get() and self.var_y2.get():
            self.is_valid = True
            self.x1 = self.var_x1.get()
            self.y1 = self.var_y1.get()
            self.x2 = self.var_x2.get()
            self.y2 = self.var_y2.get()
        else:
            self.is_valid = False

        self.window.destroy()
