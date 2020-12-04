import tkinter as tk
from GUIs.FileSelectionGUI import FileSelectionGui
from utility.FringeAnalysisFunctions import *
import matplotlib
from matplotlib import cm
from matplotlib.patches import Circle
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

    is_drawing = False
    center_x = 0.0
    center_y = 0.0
    radius = 0.0

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

        def on_press(event):
            if event.button == 1:
                if self.patch is not None:
                    self.patch.remove()

                self.is_drawing = True
                self.center_x = event.xdata
                self.center_y = event.ydata

                self.patch = Circle((self.center_x, self.center_y), self.radius, facecolor='none', edgecolor='black')
                self.patch = self.ax.add_patch(self.patch)

        def on_move(event):
            if event.button == 1 and self.is_drawing:
                self.update(event)

        def on_release(event):
            if event.button == 1:
                self.is_drawing = False
                self.update(event)

        self.canvas.mpl_connect('button_press_event', on_press)
        self.canvas.mpl_connect('motion_notify_event', on_move)
        self.canvas.mpl_connect('button_release_event', on_release)

        self.frm_left.grid(row=0, column=0, ipadx=5, ipady=5)

        self.str_var_info = tk.StringVar()
        self.str_var_info.set(
            f"Center Point : ({self.center_x:.3f}, {self.center_y:.3f})\n"
            f"Radius : {self.radius:.3f}"
        )
        self.lbl_info = tk.Label(master=self.frm_right, textvariable=self.str_var_info, width=25)

        self.lbl_info.grid(row=0, column=0, ipadx=5, ipady=5)

        self.frm_circle_input = tk.Frame(master=self.frm_right)

        self.lbl_cone_radius = tk.Label(master=self.frm_circle_input, text="Radius of the cone(mm): ")
        self.lbl_cone_height = tk.Label(master=self.frm_circle_input, text="Height of the cone(mm): ")
        self.ent_cone_radius = tk.Entry(master=self.frm_circle_input)
        self.ent_cone_height = tk.Entry(master=self.frm_circle_input)

        self.lbl_cone_radius.grid(row=0, column=0)
        self.lbl_cone_height.grid(row=1, column=0)
        self.ent_cone_radius.grid(row=0, column=1)
        self.ent_cone_height.grid(row=1, column=1)

        self.frm_circle_input.grid(row=1, column=0, ipadx=5, ipady=5)

        self.btn_analyze = tk.Button(master=self.frm_right, text="Calibration", command=self.calibration)
        self.btn_analyze.grid(row=2, column=0, ipadx=5, ipady=5)

        self.str_var_ks = tk.StringVar()
        self.str_var_ks.set(
            f"ks = {self.ks:.3f}\n"
            f"Scale : {self.scale:.3f}"
        )
        self.lbl_current_ks = tk.Label(master=self.frm_right, textvariable=self.str_var_ks)

        self.lbl_current_ks.grid(row=3, column=0, ipadx=5, ipady=5)

        self.frm_right.grid(row=0, column=1, ipadx=5, ipady=5)

        self.frm_submit = tk.Frame(master=self.window)

        self.btn_cancel = tk.Button(master=self.frm_submit, text="Cancel", command=self.cancel)
        self.btn_submit = tk.Button(master=self.frm_submit, text="Submit", command=self.submit)

        self.btn_cancel.grid(row=0, column=0, ipadx=5, ipady=5)
        self.btn_submit.grid(row=0, column=1, ipadx=5, ipady=5)

        self.frm_submit.grid(row=1, column=1, ipadx=5, ipady=5)

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
        self.ax = self.fig.add_subplot(111)
        self.plot = self.ax.imshow(self.unwrapped_phase, cmap=cm.turbo)
        self.canvas.draw()

    def update(self, event):
        self.radius = math.sqrt((event.xdata - self.center_x) ** 2 + (event.ydata - self.center_y) ** 2)

        self.str_var_info.set(
            f"Center : ({self.center_x:.3f}, {self.center_y:.3f})\n"
            f"Radius : {self.radius:.3f}"
        )
        self.patch.set_radius(self.radius)

        self.canvas.draw()

    def calibration(self):
        self.ks = float(self.ent_cone_height.get()) / self.unwrapped_phase[int(self.center_x)][int(self.center_y)]
        self.scale = float(self.ent_cone_radius.get()) / self.radius

        self.str_var_ks.set(
            f"ks = {self.ks:.3f}\n"
            f"Scale : {self.scale:.3f}"
        )

    def submit(self):
        self.is_valid = True
        self.window.destroy()

    def cancel(self):
        self.is_valid = False
        self.window.destroy()
