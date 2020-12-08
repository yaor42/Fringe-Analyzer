import tkinter as tk
from  tkinter import ttk
from GUIs.FileSelectionGUI import FileSelectionGui
from utility.FringeAnalysisFunctions import *
import matplotlib
from matplotlib import cm
from matplotlib.patches import Circle, RegularPolygon
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import math

matplotlib.use('TkAgg')


class CalibrationGUI:
    is_valid = False

    ref_file = None
    obj_file = None

    patch = None

    ks = 1.0
    scale = 1.0

    unwrapped_phase = None

    # State of dragging a circle or a square
    is_drawing = False

    # Center and radian information of the circle or the square
    center_x = 0.0
    center_y = 0.0
    radius = 0.0

    # Angle for the square
    angle = 0.0

    # cid of binded functions
    cid_press = None
    cid_move = None
    cid_release = None

    def __init__(self, root, using_hole_masks=False):
        self.using_hole_masks = using_hole_masks

        self.window = tk.Toplevel(root.window)
        self.window.title('Calibration')

        self.menu_bar = tk.Menu(master=self.window)
        self.menu_file = tk.Menu(master=self.menu_bar, tearoff=0)

        self.menu_file.add_command(label="Open", command=self.select_files)
        self.menu_file.add_separator()
        self.menu_file.add_command(label="Exit", command=self.window.quit)

        self.menu_bar.add_cascade(label="File", menu=self.menu_file)
        self.window.config(menu=self.menu_bar)

        self.frm_left = tk.Frame(master=self.window)
        self.frm_right = tk.Frame(master=self.window)

        self.fig = Figure(figsize=(5, 5))
        self.fig.patch.set_facecolor('#F0F0F0')

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frm_left)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.ax = None
        self.plot = None

        self.frm_left.grid(row=0, column=0, ipadx=5, ipady=5)

        self.cbo_map = ttk.Combobox(
            master=self.frm_right,
            value=[
                'Circle',
                'Pyramid'
            ]
        )
        self.cbo_map.bind("<<ComboboxSelected>>", self.bind)
        self.cbo_map.current(0)

        self.cbo_map.grid(row=0, column=0, ipadx=5, ipady=5)

        self.str_var_info = tk.StringVar()
        self.str_var_info.set("\n\n")
        self.lbl_info = tk.Label(master=self.frm_right, textvariable=self.str_var_info, width=25)

        self.lbl_info.grid(row=1, column=0, ipadx=5, ipady=5)

        self.frm_input = tk.Frame(master=self.frm_right)

        self.str_var_input_1 = tk.StringVar()
        self.str_var_input_2 = tk.StringVar()

        self.lbl_input_1 = tk.Label(master=self.frm_input, textvariable=self.str_var_input_1)
        self.lbl_input_2 = tk.Label(master=self.frm_input, textvariable=self.str_var_input_2)
        self.ent_input_1 = tk.Entry(master=self.frm_input)
        self.ent_input_2 = tk.Entry(master=self.frm_input)

        self.lbl_input_1.grid(row=0, column=0)
        self.lbl_input_2.grid(row=1, column=0)
        self.ent_input_1.grid(row=0, column=1)
        self.ent_input_2.grid(row=1, column=1)

        self.frm_input.grid(row=2, column=0, ipadx=5, ipady=5)

        self.btn_analyze = tk.Button(master=self.frm_right, text="Calibration", command=self.calibration)
        self.btn_analyze.grid(row=3, column=0, ipadx=5, ipady=5)

        self.str_var_ks = tk.StringVar()
        self.str_var_ks.set(
            f"ks = {self.ks:.3f}\n"
            f"Scale : {self.scale:.3f}"
        )
        self.lbl_current_ks = tk.Label(master=self.frm_right, textvariable=self.str_var_ks)

        self.lbl_current_ks.grid(row=4, column=0, ipadx=5, ipady=5)

        self.frm_right.grid(row=0, column=1, ipadx=5, ipady=5)

        self.frm_submit = tk.Frame(master=self.window)

        self.btn_cancel = tk.Button(master=self.frm_submit, text="Cancel", command=self.cancel)
        self.btn_submit = tk.Button(master=self.frm_submit, text="Submit", command=self.submit)

        self.btn_cancel.grid(row=0, column=0, ipadx=5, ipady=5, padx=5, pady=5)
        self.btn_submit.grid(row=0, column=1, ipadx=5, ipady=5, padx=5, pady=5)

        self.frm_submit.grid(row=1, column=1, ipadx=5, ipady=5)

        self.bind()

    def select_files(self):
        file_gui = FileSelectionGui(self, True)

        self.window.wait_window(file_gui.window)

        self.window.lift()

        if file_gui.is_valid:
            self.ref_file = file_gui.ref_file
            self.obj_file = file_gui.obj_file

            self.analyze()

    def analyze(self):
        ref_img = cv2.imread(self.ref_file, cv2.IMREAD_GRAYSCALE)
        obj_img = [cv2.imread(self.obj_file[0], cv2.IMREAD_GRAYSCALE)]

        pitch = getPitch(ref_img)

        ref_phase = fiveStepShift(ref_img, pitch, maskHoles=self.using_hole_masks)

        _, _, [self.unwrapped_phase], _ = analyze_phase(
            ref_phase,
            obj_img,
            self.ks,
            pitch
        )

        self.draw()

    def draw(self):
        if self.ax is None:
            self.ax = self.fig.add_subplot(111)
        self.plot = self.ax.imshow(self.unwrapped_phase, cmap=cm.turbo)
        self.canvas.draw()

    def calibration(self):
        if self.cbo_map.get() == "Circle":
            self.ks = float(self.ent_input_2.get()) / self.unwrapped_phase[int(self.center_x)][int(self.center_y)]
            self.scale = float(self.ent_input_1.get()) / self.radius
        else:
            self.ks = float(self.ent_input_2.get()) / self.unwrapped_phase[int(self.center_x)][int(self.center_y)]
            self.scale = float(self.ent_input_1.get()) / self.radius / math.sqrt(2)

        self.str_var_ks.set(
            f"ks = {self.ks:.3f}\n"
            f"Scale : {self.scale:.3f}"
        )

    def bind(self, _event=None):
        if self.cid_move is not None:
            self.canvas.mpl_disconnect(self.cid_press)
            self.canvas.mpl_disconnect(self.cid_move)
            self.canvas.mpl_disconnect(self.cid_release)

        if self.cbo_map.get() == "Circle":
            self.cid_press = self.canvas.mpl_connect('button_press_event', self.on_press_circle)
            self.cid_move = self.canvas.mpl_connect('motion_notify_event', self.on_move_circle)
            self.cid_release = self.canvas.mpl_connect('button_release_event', self.on_release_circle)

            self.str_var_input_1.set("The Radius of the Cone(mm): ")
            self.str_var_input_2.set("The Height of the Cone(mm): ")
        else:
            self.cid_press = self.canvas.mpl_connect('button_press_event', self.on_press_square)
            self.cid_move = self.canvas.mpl_connect('motion_notify_event', self.on_move_square)
            self.cid_release = self.canvas.mpl_connect('button_release_event', self.on_release_square)

            self.str_var_input_1.set("The Length of Side of the Pyramid(mm): ")
            self.str_var_input_2.set("The Height of the Pyramid(mm): ")

    def on_press_circle(self, event):
        if event.button == 1:
            if self.patch is not None:
                self.patch.remove()

            self.is_drawing = True
            self.center_x = event.xdata
            self.center_y = event.ydata

            self.patch = Circle((self.center_x, self.center_y), self.radius, facecolor='none', edgecolor='black')
            self.patch = self.ax.add_patch(self.patch)

    def on_move_circle(self, event):
        if event.button == 1 and self.is_drawing:
            self.update_circle(event)

    def on_release_circle(self, event):
        if event.button == 1:
            self.is_drawing = False
            self.update_circle(event)

    def update_circle(self, event):
        self.radius = math.sqrt((event.xdata - self.center_x) ** 2 + (event.ydata - self.center_y) ** 2)

        self.str_var_info.set(
            f"Center : ({self.center_x:.3f}, {self.center_y:.3f})\n"
            f"Radius : {self.radius:.3f}\n"
        )
        self.patch.set_radius(self.radius)

        self.canvas.draw()

    def on_press_square(self, event):
        if event.button == 1:
            if self.patch is not None:
                self.patch.remove()

            self.is_drawing = True
            self.center_x = event.xdata
            self.center_y = event.ydata

            self.patch = RegularPolygon((self.center_x, self.center_y), 4, self.radius, orientation=0.0,
                                        facecolor='none', edgecolor='black')
            self.patch = self.ax.add_patch(self.patch)

    def on_move_square(self, event):
        if event.button == 1 and self.is_drawing:
            self.update_square(event)

    def on_release_square(self, event):
        if event.button == 1:
            self.is_drawing = False
            self.update_square(event)

    def update_square(self, event):
        self.radius = math.sqrt((event.xdata - self.center_x) ** 2 + (event.ydata - self.center_y) ** 2)

        if self.radius != 0.0:
            if event.ydata - self.center_y >= 0:
                self.angle = math.acos((event.xdata - self.center_x) / self.radius)
            else:
                self.angle = - math.acos((event.xdata - self.center_x) / self.radius)
        else:
            self.angle = 0.0

        self.str_var_info.set(
            f"Center : ({self.center_x:.3f}, {self.center_y:.3f})\n"
            f"Radius : {self.radius:.3f}\n"
            f"Angle  : {self.angle}"
        )

        self.patch.radius = self.radius
        self.patch.orientation = self.angle

        self.canvas.draw()

    def submit(self):
        self.is_valid = True
        self.window.destroy()

    def cancel(self):
        self.is_valid = False
        self.window.destroy()
