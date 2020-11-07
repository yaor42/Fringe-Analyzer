import tkinter as tk
from tkinter.filedialog import askopenfilename
from FringeAnalysisFunctions import *
import matplotlib
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.figure import Figure

matplotlib.use('TkAgg')
#
#
# def select_file(entry):
#     filepath = askopenfilename(
#         filetypes=[
#             ("JPEG files", ".jpeg .jpg .jpe"),
#             ("JPEG 200 files", ".jp2"),
#             ("Windows bitmaps", ".bmp .dib"),
#             ("Portable Network Graphics", ".png"),
#             ("TIFF files", ".tiff .tif"),
#             ("All Files", "*.*")
#         ]
#     )
#
#     entry.delete(0, tk.END)
#     entry.insert(tk.END, filepath)
#
#
# class FringeGUI:
#
#     def __init__(self):
#         self.depth_map = None
#         self.X_axis = None
#         self.Y_axis = None
#
#         self.window = tk.Tk()
#         self.window.title("Fringe Analysis Prototype")
#
#         self.frm_input = tk.Frame(master=self.window, relief=tk.RIDGE, borderwidth=5)
#         self.frm_input.columnconfigure(1, minsize=200, weight=1)
#
#         self.lbl_ref = tk.Label(master=self.frm_input, text='Reference picture: ')
#         self.lbl_obj = tk.Label(master=self.frm_input, text='  Object picture : ')
#         self.ent_ref = tk.Entry(master=self.frm_input)
#         self.ent_obj = tk.Entry(master=self.frm_input)
#         self.btn_select_ref = tk.Button(
#             master=self.frm_input,
#             text='Open..',
#             command=lambda: select_file(self.ent_ref)
#         )
#         self.btn_select_obj = tk.Button(
#             master=self.frm_input,
#             text='Open..',
#             command=lambda: select_file(self.ent_obj)
#         )
#         self.btn_submit = tk.Button(
#             master=self.frm_input,
#             text="Analyze",
#             command=self.analyze
#         )
#
#         self.lbl_ref.grid(row=0, column=0, sticky='w')
#         self.lbl_obj.grid(row=1, column=0, sticky='w')
#         self.ent_ref.grid(row=0, column=1, sticky='ew')
#         self.ent_obj.grid(row=1, column=1, sticky='ew')
#         self.btn_select_ref.grid(row=0, column=2, padx=5, ipadx=5)
#         self.btn_select_obj.grid(row=1, column=2, padx=5, ipadx=5)
#         self.btn_submit.grid(row=2, column=1, padx=5, ipadx=5)
#
#         self.frm_input.pack(fill=tk.X, ipadx=5, ipady=5)
#
#         self.fig = Figure()
#
#         self.canvas = FigureCanvasTkAgg(self.fig, master=self.window)
#         self.canvas.draw()
#         self.canvas.get_tk_widget().pack(fill=tk.BOTH)
#
#         self.ax = self.fig.add_subplot(111, projection="3d")
#
#     def analyze(self, ks=5.7325):
#         ref_file = self.ent_ref.get()
#         obj_file = self.ent_obj.get()
#
#         if not os.path.exists(ref_file):
#             tk.messagebox.showerror('File Input Error', f'Reference image path "{ref_file}" is not valid!')
#             return
#
#         if not os.path.exists(obj_file):
#             tk.messagebox.showerror('File Input Error', f'object image path "{obj_file}" is not valid!')
#             return
#
#         self.window.title("Fringe Analysis Prototype - Analyzing")
#
#         ref_img = cv2.imread(ref_file, cv2.IMREAD_GRAYSCALE)
#         obj_img = cv2.imread(obj_file, cv2.IMREAD_GRAYSCALE)
#
#         pitch = getPitch(ref_img)
#
#         ref_phase = fiveStepShift(ref_img, pitch, maskHoles=True)
#         obj_phase = fiveStepShift(obj_img, pitch)
#
#         diff = obj_phase - ref_phase
#
#         unwrapped_phase_map = unwrapPhase(diff)
#         self.depth_map = unwrapped_phase_map * ks
#
#         self.X_axis = np.array(
#             [
#                 [x for x in range(0, self.depth_map.shape[0])] for i in range(0, self.depth_map.shape[1])
#             ]
#         )
#         self.Y_axis = np.array(
#             [
#                 [x for i in range(0, self.depth_map.shape[0])] for x in range(0, self.depth_map.shape[1])
#             ]
#         )
#
#         self.draw()
#
#         self.window.title("Fringe Analysis Prototype - Done")
#
#     def draw(self):
#         if self.X_axis is None or self.Y_axis is None or self.depth_map is None:
#             return
#
#         self.ax.clear()
#
#         surf = self.ax.plot_surface(
#             self.X_axis,
#             self.Y_axis,
#             self.depth_map,
#             rstride=25,
#             cstride=25,
#             cmap=cm.coolwarm,
#             linewidth=0,
#             antialiased=False
#         )
#
#         self.fig.colorbar(surf, shrink=0.5, aspect=5)
#         self.canvas.draw()
#         self.canvas.flush_events()
#
#     def show(self):
#         self.window.mainloop()


class FringeGUI:
    ref_file = None
    obj_file = None
    ref_phase = None
    obj_phase = None
    diff_phase = None
    unwrapped_phase = None
    depth_map = None
    pitch = None
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

        self.frm_upper_left.grid(row=0, column=0, padx=5, pady=5)
        self.frm_upper_right.grid(row=0, column=1)
        self.frm_down_left.grid(row=1, column=0, padx=5, pady=5)
        self.frm_down_right.grid(row=1, column=1, padx=5, pady=5)

        self.fig_upper = Figure(figsize=(5, 3))
        self.fig_right = Figure(figsize=(3, 5))
        self.fig_main = Figure(figsize=(5, 5))

        self.fig_upper.patch.set_facecolor('#F0F0F0')
        self.fig_right.patch.set_facecolor('#F0F0F0')
        self.fig_main.patch.set_facecolor('#F0F0F0')

        self.canvas_upper = FigureCanvasTkAgg(self.fig_upper, master=self.frm_upper_left)
        self.canvas_right = FigureCanvasTkAgg(self.fig_right, master=self.frm_down_right)
        self.canvas_main = FigureCanvasTkAgg(self.fig_main, master=self.frm_down_left)

        self.canvas_main.mpl_connect('button_press_event', self.onclick_main)

        self.canvas_upper.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.canvas_right.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.canvas_main.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.ax_upper = self.fig_upper.add_subplot(111)
        self.ax_right = self.fig_right.add_subplot(111)
        self.ax_main = self.fig_main.add_subplot(111)

        self.frm_figs.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.window.resizable(False, False)

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

        self.analyze()

    def analyze(self, ks=5.7325):
        ref_img = cv2.imread(self.ref_file, cv2.IMREAD_GRAYSCALE)
        obj_img = cv2.imread(self.obj_file, cv2.IMREAD_GRAYSCALE)

        self.pitch = getPitch(ref_img)

        self.ref_phase = fiveStepShift(ref_img, self.pitch)
        self.obj_phase = fiveStepShift(obj_img, self.pitch)

        self.diff_phase = self.obj_phase - self.ref_phase

        self.unwrapped_phase = unwrapPhase(self.diff_phase)
        self.depth_map = self.unwrapped_phase * ks

        self.max_value = max([max(i) for i in self.depth_map])
        self.min_value = min([min(i) for i in self.depth_map])

        self.ax_main.imshow(self.depth_map, cmap=cm.coolwarm)
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

            self.ax_upper.plot(axis, x)
            self.ax_right.plot(y, axis)

            self.ax_upper.set_ylim((self.min_value, self.max_value))
            self.ax_right.set_xlim((self.min_value, self.max_value))

            self.canvas_upper.draw()
            self.canvas_right.draw()

    def show(self):
        self.window.mainloop()


if __name__ == '__main__':
    gui = FringeGUI()
    gui.show()
