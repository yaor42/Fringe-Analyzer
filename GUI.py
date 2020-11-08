import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import askopenfilename, askopenfilenames
from FringeAnalysisFunctions import *
import matplotlib
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.figure import Figure

matplotlib.use('TkAgg')


class FringeGUI:
    ref_file = None
    obj_file = None

    ref_phase = None
    obj_phase = None

    diff_phase = None
    unwrapped_phase = None
    depth_map = None

    curr_map = None

    pitch = None
    ks = 5.7325

    max_value = None
    min_value = None

    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Fringe Analysis Prototype")

        self.frm_figs = tk.Frame(master=self.window)

        self.frm_figs.rowconfigure(0, weight=4)
        self.frm_figs.rowconfigure(1, weight=1, minsize=200)
        self.frm_figs.columnconfigure(0, weight=1, minsize=200)
        self.frm_figs.columnconfigure(1, weight=4)

        self.frm_upper_left = tk.Frame(master=self.frm_figs)
        self.frm_upper_right = tk.Frame(master=self.frm_figs)
        self.frm_down_left = tk.Frame(master=self.frm_figs)
        self.frm_down_right = tk.Frame(master=self.frm_figs)

        self.cbo_map = ttk.Combobox(
            self.frm_upper_right,
            value=[
                'Object Surface Contour',
                'Quality Map',
                'Wrapped Phase Map',
                'Object Image',
                'Reference Image'
            ]
        )
        self.cbo_map.current(0)

        self.btn_show = tk.Button(self.frm_upper_right, text='Show', command=self.draw)

        self.cbo_map.pack(side=tk.TOP)
        self.btn_show.pack(side=tk.BOTTOM)

        self.fig_upper = Figure(figsize=(5, 3))
        self.fig_right = Figure(figsize=(3, 5))
        self.fig_main = Figure(figsize=(5, 5))

        self.fig_upper.patch.set_facecolor('#F0F0F0')
        self.fig_right.patch.set_facecolor('#F0F0F0')
        self.fig_main.patch.set_facecolor('#F0F0F0')

        self.canvas_upper = FigureCanvasTkAgg(self.fig_upper, master=self.frm_upper_left)
        self.canvas_right = FigureCanvasTkAgg(self.fig_right, master=self.frm_down_right)
        self.canvas_main = FigureCanvasTkAgg(self.fig_main, master=self.frm_down_left)

        self.canvas_upper.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.canvas_right.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.canvas_main.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.ax_upper = self.fig_upper.add_subplot(111)
        self.ax_right = self.fig_right.add_subplot(111)
        self.ax_main = self.fig_main.add_subplot(111)

        self.frm_figs.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.menu_bar = tk.Menu(master=self.window)
        self.menu_file = tk.Menu(master=self.menu_bar, tearoff=0)
        self.menu_help = tk.Menu(master=self.menu_bar, tearoff=0)

        self.menu_file.add_command(label="Open..", command=self.select_files)
        self.menu_file.add_command(label="Calibration", command=None)
        self.menu_file.add_separator()
        self.menu_file.add_command(label="Exit", command=self.window.quit)

        self.menu_bar.add_cascade(label="File", menu=self.menu_file)
        self.menu_bar.add_cascade(label="Help", menu=self.menu_help)

        self.window.config(menu=self.menu_bar)

        self.frm_upper_left.grid(row=0, column=0, padx=5, pady=5)
        self.frm_upper_right.grid(row=0, column=1, padx=5, pady=5)
        self.frm_down_left.grid(row=1, column=0, padx=5, pady=5)
        self.frm_down_right.grid(row=1, column=1, padx=5, pady=5)

        # self.window.resizable(False, False)

    def select_files(self):
        self.ref_file = askopenfilename(
            title="Select reference image",
            filetypes=[
                ("JPEG files", ".jpeg .jpg .jpe"),
                ("JPEG 200 files", ".jp2"),
                ("Windows bitmaps", ".bmp .dib"),
                ("Portable Network Graphics", ".png"),
                ("TIFF files", ".tiff .tif"),
                ("All Files", "*.*")
            ]
        )

        self.obj_file = askopenfilename(
            title="Select object image",
            filetypes=[
                ("JPEG files", ".jpeg .jpg .jpe"),
                ("JPEG 200 files", ".jp2"),
                ("Windows bitmaps", ".bmp .dib"),
                ("Portable Network Graphics", ".png"),
                ("TIFF files", ".tiff .tif"),
                ("All Files", "*.*")
            ]
        )

        # self.obj_file = askopenfiles(
        #     title="Select object image",
        #     filetypes=[
        #         ("JPEG files", ".jpeg .jpg .jpe"),
        #         ("JPEG 200 files", ".jp2"),
        #         ("Windows bitmaps", ".bmp .dib"),
        #         ("Portable Network Graphics", ".png"),
        #         ("TIFF files", ".tiff .tif"),
        #         ("All Files", "*.*")
        #     ]
        # )

        print(self.obj_file)

        self.analyze()

    def analyze(self):
        ref_img = cv2.imread(self.ref_file, cv2.IMREAD_GRAYSCALE)
        obj_img = cv2.imread(self.obj_file, cv2.IMREAD_GRAYSCALE)

        self.pitch = getPitch(ref_img)

        self.ref_phase = fiveStepShift(ref_img, self.pitch)
        self.obj_phase = fiveStepShift(obj_img, self.pitch)

        self.diff_phase = self.obj_phase - self.ref_phase

        self.unwrapped_phase = unwrapPhase(self.diff_phase)
        self.depth_map = self.unwrapped_phase * self.ks

        self.draw()

    def draw(self):
        selected_map = self.cbo_map.get()

        if selected_map == 'Object Surface Contour':
            self.curr_map = self.depth_map
        elif selected_map == 'Quality Map':
            self.curr_map = self.depth_map
        elif selected_map == 'Wrapped Phase Map':
            self.curr_map = self.diff_phase
        elif selected_map == 'Object Image':
            self.curr_map = self.obj_phase
        elif selected_map == 'Reference Image':
            self.curr_map = self.ref_phase

        self.max_value = max([max(i) for i in self.curr_map])
        self.min_value = min([min(i) for i in self.curr_map])

        self.canvas_main.mpl_connect('button_press_event', self.onclick_main)

        self.ax_main.imshow(self.curr_map, cmap=cm.coolwarm)
        self.canvas_main.draw()

    def onclick_main(self, event):
        print('%s click: button=%d, x=%d, y=%d, xdata=%f, ydata=%f' %
              ('double' if event.dblclick else 'single', event.button,
               event.x, event.y, event.xdata, event.ydata))
        if event.button == 1:
            x = self.depth_map[event.x, :]
            y = self.depth_map[:, event.y]
            axis = [i for i in range(len(x))]

            self.ax_upper.clear()
            self.ax_right.clear()

            self.ax_upper.plot(axis, y)
            self.ax_right.plot(x, axis)

            self.ax_upper.set_ylim((self.min_value, self.max_value))
            self.ax_right.set_xlim((self.min_value, self.max_value))

            self.canvas_upper.draw()
            self.canvas_right.draw()

    def show(self):
        self.window.mainloop()


if __name__ == '__main__':
    gui = FringeGUI()
    gui.show()
