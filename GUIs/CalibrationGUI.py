import math
import tkinter as tk
from tkinter import ttk

import matplotlib
from matplotlib import cm
from matplotlib.backend_bases import MouseButton
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.patches import Circle, RegularPolygon

from GUIs.FileSelectionGUI import FileSelectionGui
from utility.FringeAnalysisFunctions import *

matplotlib.use('TkAgg')


class CalibrationGUI:
    is_valid = False

    ref_file = None
    obj_file = None

    patch_selected = None
    patch_center = None

    ks = 1.0
    scale = 1.0

    obj_image = None
    unwrapped_phase = None

    plot = None
    ax = None

    # State of dragging a circle or a square
    is_drawing = False
    is_dragging = False

    drag_x = 0
    drag_y = 0

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

        self.fig = Figure(figsize=(5, 5), facecolor='#F0F0F0')

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frm_left)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.frm_left.grid(row=0, column=0, ipadx=5, ipady=5)

        self.cbo_display = ttk.Combobox(master=self.frm_right, value=['Original Image', 'Default Depth Map'])
        self.cbo_display.bind("<<ComboboxSelected>>", self.set_display)
        self.cbo_display.current(0)

        self.cbo_display.grid(row=0, column=0, ipadx=5, ipady=5)

        self.cbo_map = ttk.Combobox(master=self.frm_right, value=['Circle', 'Pyramid'])
        self.cbo_map.bind("<<ComboboxSelected>>", self.set_reference)
        self.cbo_map.current(0)

        self.cbo_map.grid(row=1, column=0, ipadx=5, ipady=5)

        self.str_var_info = tk.StringVar()
        self.str_var_info.set("\n\n\n\n")
        self.lbl_info = tk.Label(master=self.frm_right, textvariable=self.str_var_info, width=25)

        self.lbl_info.grid(row=2, column=0, ipadx=5, ipady=5)

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

        self.frm_input.grid(row=3, column=0, ipadx=5, ipady=5)

        self.btn_analyze = tk.Button(master=self.frm_right, text="Calibration", command=self.calibration)
        self.btn_analyze.grid(row=4, column=0, ipadx=5, ipady=5)

        self.str_var_ks = tk.StringVar()
        self.str_var_ks.set(
            f"ks = {self.ks:.3f}\n"
            f"Scale : {self.scale:.3f}"
        )
        self.lbl_current_ks = tk.Label(master=self.frm_right, textvariable=self.str_var_ks)

        self.lbl_current_ks.grid(row=5, column=0, ipadx=5, ipady=5)

        self.frm_right.grid(row=0, column=1, ipadx=5, ipady=5)

        self.frm_submit = tk.Frame(master=self.window)

        self.btn_cancel = tk.Button(master=self.frm_submit, text="Cancel", command=self.cancel)
        self.btn_submit = tk.Button(master=self.frm_submit, text="Submit", command=self.submit)

        self.btn_cancel.grid(row=0, column=0, ipadx=5, ipady=5, padx=5)
        self.btn_submit.grid(row=0, column=1, ipadx=5, ipady=5, padx=5)

        self.frm_submit.grid(row=1, column=1, ipadx=5, ipady=5)

        self.set_reference()

        # Set the window not resizable so the layout would not be destroyed
        self.window.resizable(False, False)

    def select_files(self):
        file_gui = FileSelectionGui(self, True)

        self.window.wait_window(file_gui.window)

        self.window.lift()

        if file_gui.is_valid:
            if self.patch_selected is not None and self.patch_center is not None:
                self.patch_selected.remove()
                self.patch_center.remove()
                self.patch_selected = None
                self.patch_center = None

            self.ref_file = file_gui.ref_file
            self.obj_file = file_gui.obj_file

            self.analyze()

    def analyze(self):
        ref_img = cv2.imread(self.ref_file, cv2.IMREAD_GRAYSCALE)
        obj_img = [cv2.imread(self.obj_file[0], cv2.IMREAD_GRAYSCALE)]

        self.obj_image = obj_img[0]

        pitch = getPitch(ref_img)

        ref_phase = fiveStepShift(ref_img, pitch, maskHoles=self.using_hole_masks)

        _, _, [self.unwrapped_phase], _ = analyze_phase_mt(ref_phase, obj_img, self.ks, pitch)

        self.draw()

    def draw(self):
        if self.ax is not None:
            self.ax.remove()

        self.ax = self.fig.add_subplot(111)

        if self.cbo_display.get() == 'Original Image':
            self.plot = self.ax.imshow(self.obj_image, cmap=cm.gray)
        else:
            self.plot = self.ax.imshow(self.unwrapped_phase, cmap=cm.turbo)

        if self.patch_selected is not None and self.patch_center is not None:
            self.patch_selected.remove()
            self.patch_center.remove()

            self.patch_selected = Circle((self.center_x, self.center_y),
                                         self.radius, facecolor='none', edgecolor='black')
            self.patch_selected = self.ax.add_patch(self.patch_selected)

            self.patch_center = Circle((self.center_x, self.center_y),
                                       2, facecolor='black', edgecolor='black', hatch='x')
            self.patch_center = self.ax.add_patch(self.patch_center)

        self.canvas.draw()

    def calibration(self):
        (h, l) = self.unwrapped_phase.shape
        # print(f"{h}, {l}")
        x = int(self.center_x)
        y = int(self.center_y)
        radius_square = self.radius ** 2
        sum = 0
        num = 0

        for xx in range(x - int(self.radius) - 1, x + int(self.radius) + 2):
            for yy in range(y - int(self.radius) - 1, y + int(self.radius) + 2):
                if 0 <= xx < h and 0 <= yy < l and (xx - x) ** 2 + (yy - y) ** 2 > radius_square:
                    sum += self.unwrapped_phase[yy][xx]
                    num += 1

        base = sum / num

        # print(base)

        if self.cbo_map.get() == "Circle":
            self.ks = float(self.ent_input_2.get()) / (self.unwrapped_phase[y][x] - base)
            self.scale = float(self.ent_input_1.get()) / self.radius
        else:
            self.ks = float(self.ent_input_2.get()) / (self.unwrapped_phase[y][x] - base)
            self.scale = float(self.ent_input_1.get()) / self.radius / math.sqrt(2)

        self.str_var_ks.set(
            f"ks = {self.ks:.3f}\n"
            f"Scale : {self.scale:.3f}"
        )

    def set_display(self, _event=None):
        self.draw()

    def set_reference(self, _event=None):
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
        # print(event.button)
        if event.button == MouseButton.LEFT:
            if self.patch_selected is not None and self.patch_center is not None:
                self.patch_selected.remove()
                self.patch_center.remove()

            self.is_drawing = True
            self.center_x = event.xdata
            self.center_y = event.ydata

            self.patch_selected = Circle((self.center_x, self.center_y),
                                         self.radius, facecolor='none', edgecolor='black')
            self.patch_selected = self.ax.add_patch(self.patch_selected)

            self.patch_center = Circle((self.center_x, self.center_y),
                                       2, facecolor='black', edgecolor='black', hatch='x')
            self.patch_center = self.ax.add_patch(self.patch_center)
        elif event.button == MouseButton.RIGHT:
            self.is_dragging = True
            self.drag_x = event.xdata
            self.drag_y = event.ydata

    def on_move_circle(self, event):
        if event.button == MouseButton.LEFT and self.is_drawing:
            self.update_circle(event)
        elif event.button == MouseButton.RIGHT and self.is_dragging:
            self.move_circle(event)

    def on_release_circle(self, event):
        if event.button == MouseButton.LEFT:
            self.is_drawing = False
            self.update_circle(event)
        elif event.button == MouseButton.RIGHT:
            self.is_dragging = False
            self.move_circle(event)

    def move_circle(self, event):
        if self.patch_selected is not None:
            self.patch_selected.remove()

        if self.patch_center is not None:
            self.patch_center.remove()

        self.center_x += event.xdata - self.drag_x
        self.center_y += event.ydata - self.drag_y

        self.patch_selected = Circle((self.center_x, self.center_y),
                                     self.radius, facecolor='none', edgecolor='black')
        self.patch_selected = self.ax.add_patch(self.patch_selected)

        self.patch_center = Circle((self.center_x, self.center_y),
                                   2, facecolor='black', edgecolor='black', hatch='x')
        self.patch_center = self.ax.add_patch(self.patch_center)

        self.str_var_info.set(
            f"Center Depth: {self.unwrapped_phase[int(self.center_y)][int(self.center_x)]:.3f}\n"
            f"   Center   : ({self.center_x:.3f}, {self.center_y:.3f})\n"
            f"   Radius   : {self.radius:.3f}\n"
        )

        self.drag_x = event.xdata
        self.drag_y = event.ydata

        self.canvas.draw()

    def update_circle(self, event):
        self.radius = math.sqrt((event.xdata - self.center_x) ** 2 + (event.ydata - self.center_y) ** 2)

        self.patch_selected.set_radius(self.radius)

        self.str_var_info.set(
            f"Center Depth: {self.unwrapped_phase[int(self.center_y)][int(self.center_x)]:.3f}\n"
            f"Center : ({self.center_x:.3f}, {self.center_y:.3f})\n"
            f"Radius : {self.radius:.3f}\n"
        )

        self.canvas.draw()

    def on_press_square(self, event):
        if event.button == 1:
            if self.patch_selected is not None:
                self.patch_selected.remove()

            if self.patch_center is not None:
                self.patch_center.remove()

            self.is_drawing = True
            self.center_x = event.xdata
            self.center_y = event.ydata

            self.patch_selected = RegularPolygon((self.center_x, self.center_y),
                                                 4, self.radius, orientation=0.0,
                                                 facecolor='none', edgecolor='black')
            self.patch_selected = self.ax.add_patch(self.patch_selected)

            self.patch_center = Circle((self.center_x, self.center_y),
                                       2, facecolor='black', edgecolor='black', hatch='x')
            self.patch_center = self.ax.add_patch(self.patch_center)
        elif event.button == MouseButton.RIGHT:
            self.is_dragging = True
            self.drag_x = event.xdata
            self.drag_y = event.ydata

    def on_move_square(self, event):
        if event.button == MouseButton.LEFT and self.is_drawing:
            self.update_square(event)
        elif event.button == MouseButton.RIGHT and self.is_dragging:
            self.move_square(event)

    def on_release_square(self, event):
        if event.button == 1:
            self.is_drawing = False
            self.update_square(event)
        elif event.button == MouseButton.RIGHT:
            self.is_dragging = False
            self.move_square(event)

    def move_square(self, event):
        if self.patch_selected is not None:
            self.patch_selected.remove()

        if self.patch_center is not None:
            self.patch_center.remove()

        self.center_x += event.xdata - self.drag_x
        self.center_y += event.ydata - self.drag_y

        self.patch_selected = RegularPolygon((self.center_x, self.center_y),
                                             4, self.radius, orientation=self.angle,
                                             facecolor='none', edgecolor='black')
        self.patch_selected = self.ax.add_patch(self.patch_selected)

        self.patch_center = Circle((self.center_x, self.center_y),
                                   2, facecolor='black', edgecolor='black', hatch='x')
        self.patch_center = self.ax.add_patch(self.patch_center)

        self.str_var_info.set(
            f"Center Depth: {self.unwrapped_phase[int(self.center_y)][int(self.center_x)]:.3f}\n"
            f"   Center   : ({self.center_x:.3f}, {self.center_y:.3f})\n"
            f"   Radius   : {self.radius:.3f}\n"
            f"   Angle    : {self.angle}"
        )

        self.drag_x = event.xdata
        self.drag_y = event.ydata

        self.canvas.draw()

    def update_square(self, event):
        self.radius = math.sqrt((event.xdata - self.center_x) ** 2 + (event.ydata - self.center_y) ** 2)

        if self.radius != 0.0:
            if event.ydata - self.center_y >= 0:
                self.angle = math.acos((event.xdata - self.center_x) / self.radius)
            else:
                self.angle = - math.acos((event.xdata - self.center_x) / self.radius)
        else:
            self.angle = 0.0

        self.patch_selected.radius = self.radius
        self.patch_selected.orientation = self.angle

        self.str_var_info.set(
            f"Center Depth: {self.unwrapped_phase[int(self.center_y)][int(self.center_x)]:.3f}\n"
            f"   Center   : ({self.center_x:.3f}, {self.center_y:.3f})\n"
            f"   Radius   : {self.radius:.3f}\n"
            f"   Angle    : {self.angle}"
        )

        self.canvas.draw()

    def submit(self):
        self.is_valid = True
        self.window.destroy()

    def cancel(self):
        self.is_valid = False
        self.window.destroy()
