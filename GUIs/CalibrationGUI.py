import tkinter as tk
from GUIs.FileSelectionGUI import FileSelectionGui
from utility.FringeAnalysisFunctions import *
import matplotlib
from matplotlib import pyplot as plt
from matplotlib import cm
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

matplotlib.use('TkAgg')


class CalibrationGUI:
    is_valid = False

    ref_file = None
    obj_file = None

    patch = None

    ks = 1.0
    scale = None

    depth_map = None

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

        def onclick(event):
            if event.button == 1:
                if self.patch is not None:
                    self.patch.remove()
                self.patch = plt.Circle((event.xdata, event.ydata), 5, facecolor='none', edgecolor='black')
                self.patch = self.ax.add_patch(self.patch)
                self.canvas.draw()

        self.canvas.mpl_connect('button_press_event', onclick)

        self.frm_left.grid(row=0, column=0)
        self.frm_right.grid(row=0, column=1)

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

        _, _, _, self.depth_map = analyze_phase(
            ref_phase,
            obj_img,
            self.ks,
            pitch
        )

        self.depth_map = self.depth_map[0]

        self.draw()

    def draw(self):
        self.ax = self.fig.add_subplot(111)
        self.plot = self.ax.imshow(self.depth_map, cmap=cm.turbo)
        self.canvas.draw()

    def cancel(self):
        self.is_valid = False
        self.window.destroy()
