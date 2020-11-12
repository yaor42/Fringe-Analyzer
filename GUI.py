import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import askopenfilename, askopenfilenames
from PIL import Image, ImageTk
from FringeAnalysisFunctions import *
import matplotlib
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.figure import Figure

matplotlib.use('TkAgg')

""" A GUI module for the Fringe Analysis 
    

"""


class FileSelectionGui:
    is_valid = False

    ref_file = None
    obj_file = None

    def __init__(self, root):
        self.window = tk.Toplevel(root)
        self.window.title('Image Selection')

        self.frm_left = tk.Frame(master=self.window)
        self.frm_right = tk.Frame(master=self.window)

        self.lbl_ref = tk.Label(master=self.frm_left, text='Select reference image: ')
        self.lbl_obj = tk.Label(master=self.frm_right, text='Select object images: ')

        self.ref_img = ImageTk.PhotoImage(Image.new('RGB', (200, 200), (240, 240, 240)))
        self.obj_img = ImageTk.PhotoImage(Image.new('RGB', (200, 200), (240, 240, 240)))

        self.lbl_ref_img = tk.Label(master=self.frm_left, image=self.ref_img)
        self.lbl_obj_img = tk.Label(master=self.frm_right, image=self.obj_img)

        self.scl_obj = tk.Scale(master=self.window, command=self.redraw_obj, orient=tk.HORIZONTAL)

        self.btn_ref = tk.Button(master=self.window, text="Open..", command=self.select_ref_image)
        self.btn_obj = tk.Button(master=self.window, text="Open..", command=self.select_obj_image)

        self.lbl_ref.pack()
        self.lbl_ref_img.pack()

        self.lbl_obj.pack()
        self.lbl_obj_img.pack()

        self.frm_left.grid(row=0, column=0)
        self.frm_right.grid(row=0, column=1)
        self.scl_obj.grid(row=1, column=1)
        self.btn_ref.grid(row=2, column=0)
        self.btn_obj.grid(row=2, column=1)

        self.frm_button = tk.Frame(master=self.window)

        self.btn_submit = tk.Button(master=self.frm_button, text="Submit", command=self.check_and_submit)
        self.btn_cancel = tk.Button(master=self.frm_button, text="Cancel", command=self.cancel)

        self.btn_submit.grid(row=0, column=1, ipadx=5, padx=5, pady=5)
        self.btn_cancel.grid(row=0, column=0, ipadx=5, padx=5, pady=5)

        self.frm_button.grid(row=3, column=1)

    def select_ref_image(self):
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

        self.ref_img = ImageTk.PhotoImage(Image.open(self.ref_file).resize((200, 200)))
        self.lbl_ref_img.configure(image=self.ref_img)

        self.window.lift()

    def select_obj_image(self):
        self.obj_file = askopenfilenames(
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

        self.obj_img = ImageTk.PhotoImage(Image.open(self.obj_file[0]).resize((200, 200)))
        self.lbl_obj_img.configure(image=self.obj_img)
        self.scl_obj.configure(from_=1, to=len(self.obj_file))

        self.window.lift()

    def redraw_obj(self, _=None):
        if self.obj_file is None:
            return

        self.obj_img = ImageTk.PhotoImage(Image.open(self.obj_file[self.scl_obj.get() - 1]).resize((200, 200)))
        self.lbl_obj_img.configure(image=self.obj_img)

    def check_and_submit(self):
        if self.obj_file is not None or self.ref_file is not None:
            self.is_valid = True
            self.window.destroy()
        else:
            self.is_valid = False
            tk.messagebox.showerror(title="Invalid Input", message="Input is not valid!")

    def cancel(self):
        self.obj_file = None
        self.ref_file = None
        self.is_valid = False
        self.window.destroy()


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

    ax_added = False

    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Fringe Analysis Prototype")

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

        self.frm_figs = tk.Frame(master=self.window)

        self.frm_figs.rowconfigure(0, weight=4)
        self.frm_figs.rowconfigure(1, weight=1, minsize=200)
        self.frm_figs.columnconfigure(1, weight=1, minsize=200)
        self.frm_figs.columnconfigure(2, weight=4)

        self.frm_center_upper = tk.Frame(master=self.frm_figs)
        self.frm_right_upper = tk.Frame(master=self.frm_figs)
        self.frm_center_lower = tk.Frame(master=self.frm_figs)
        self.frm_right_lower = tk.Frame(master=self.frm_figs)
        self.frm_left_lower = tk.Frame(master=self.frm_figs)

        self.cbo_map = ttk.Combobox(
            self.frm_right_upper,
            value=[
                'Object Surface Contour',
                'Quality Map',
                'Wrapped Phase Map',
                'Object Phase',
                'Reference Phase'
            ]
        )
        self.cbo_map.current(0)

        self.btn_show = tk.Button(self.frm_right_upper, text='Show', command=self.draw)

        self.cbo_map.pack(side=tk.TOP)
        self.btn_show.pack(side=tk.BOTTOM)

        self.fig_upper = Figure(figsize=(5, 3))
        self.fig_right = Figure(figsize=(3, 5))
        self.fig_main = Figure(figsize=(5, 5))
        self.fig_left = Figure(figsize=(1, 5))

        self.fig_upper.patch.set_facecolor('#F0F0F0')
        self.fig_right.patch.set_facecolor('#F0F0F0')
        self.fig_main.patch.set_facecolor('#F0F0F0')
        self.fig_left.patch.set_facecolor('#F0F0F0')

        self.canvas_upper = FigureCanvasTkAgg(self.fig_upper, master=self.frm_center_upper)
        self.canvas_right = FigureCanvasTkAgg(self.fig_right, master=self.frm_right_lower)
        self.canvas_main = FigureCanvasTkAgg(self.fig_main, master=self.frm_center_lower)
        self.canvas_left = FigureCanvasTkAgg(self.fig_left, master=self.frm_left_lower)

        self.canvas_upper.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.canvas_right.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.canvas_main.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.canvas_left.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.ax_upper = None
        self.ax_right = None
        self.ax_main = None
        self.ax_left = None

        # self.frm_center_upper.grid(row=0, column=1, padx=5, pady=5)
        # self.frm_right_upper.grid(row=0, column=2, padx=5, pady=5)
        # self.frm_center_lower.grid(row=1, column=1, padx=5, pady=5)
        # self.frm_right_lower.grid(row=1, column=2, padx=5, pady=5)
        # self.frm_left_lower.grid(row=1, column=0, padx=5, pady=5)

        self.frm_center_upper.grid(row=0, column=1)
        self.frm_right_upper.grid(row=0, column=2)
        self.frm_center_lower.grid(row=1, column=1)
        self.frm_right_lower.grid(row=1, column=2)
        self.frm_left_lower.grid(row=1, column=0)

        self.scl_main = tk.Scale(master=self.frm_figs, command=self.draw, orient=tk.HORIZONTAL)
        self.scl_main.grid(row=2, column=1, stick='ew')

        self.frm_figs.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.window.resizable(False, False)

    def select_files(self):
        file_gui = FileSelectionGui(self.window)

        self.window.wait_window(file_gui.window)

        if file_gui.is_valid:
            self.ref_file = file_gui.ref_file
            self.obj_file = file_gui.obj_file

            self.analyze()

            self.scl_main.configure(from_=1, to=len(self.obj_file))

    def analyze(self):
        self.window.title("Fringe Analysis Prototype - Reading")

        ref_img = cv2.imread(self.ref_file, cv2.IMREAD_GRAYSCALE)
        obj_img = [cv2.imread(f, cv2.IMREAD_GRAYSCALE) for f in self.obj_file]

        self.pitch = getPitch(ref_img)

        self.window.title("Fringe Analysis Prototype - Calculating Five Step Shift Phase")

        self.ref_phase = fiveStepShift(ref_img, self.pitch)
        self.obj_phase = [fiveStepShift(img, self.pitch) for img in obj_img]

        self.window.title("Fringe Analysis Prototype - Calculating Difference")

        self.diff_phase = [phase - self.ref_phase for phase in self.obj_phase]

        self.window.title("Fringe Analysis Prototype - Unwrapping")

        self.unwrapped_phase = [unwrapPhase(phase) for phase in self.diff_phase]
        self.depth_map = [phase * self.ks for phase in self.unwrapped_phase]

        self.window.title("Fringe Analysis Prototype - Done")

        # print("Analyze")

        # self.draw()

    def draw(self, _=None):
        if self.obj_file is None:
            return

        selected_map = self.cbo_map.get()

        if selected_map == 'Object Surface Contour':
            self.curr_map = self.depth_map[self.scl_main.get() - 1]
        elif selected_map == 'Quality Map':
            return
        elif selected_map == 'Wrapped Phase Map':
            self.curr_map = self.diff_phase[self.scl_main.get() - 1]
        elif selected_map == 'Object Phase':
            self.curr_map = self.obj_phase[self.scl_main.get() - 1]
        elif selected_map == 'Reference Phase':
            self.curr_map = self.ref_phase

        self.max_value = max([max(i) for i in self.curr_map])
        self.min_value = min([min(i) for i in self.curr_map])

        if not self.ax_added:
            self.ax_added = True
            self.ax_upper = self.fig_upper.add_subplot(111)
            self.ax_right = self.fig_right.add_subplot(111)
            self.ax_main = self.fig_main.add_subplot(111)
            self.ax_left = self.fig_left.add_axes([0.45, 0.1, 0.1, 0.8])

            self.canvas_upper.draw()
            self.canvas_right.draw()
        else:
            self.ax_left.remove()
            self.ax_left = self.fig_left.add_axes([0.45, 0.1, 0.1, 0.8])

        self.canvas_main.mpl_connect('button_press_event', self.onclick_main)

        plot = self.ax_main.imshow(self.curr_map, cmap=cm.turbo)

        self.fig_left.colorbar(plot, cax=self.ax_left)

        self.canvas_main.draw()
        self.canvas_left.draw()

    def onclick_main(self, event):
        print('%s click: button=%d, x=%d, y=%d, xdata=%f, ydata=%f' %
              ('double' if event.dblclick else 'single', event.button,
               event.x, event.y, event.xdata, event.ydata))

        if event.button == 1:
            x = self.curr_map[int(event.xdata), :]
            y = self.curr_map[:, int(event.ydata)]
            axis_x = [i for i in range(len(x))]
            axis_y = [i for i in range(len(y))]

            self.ax_upper.clear()
            self.ax_right.clear()

            self.ax_upper.plot(axis_y, y)
            self.ax_right.plot(x, axis_x)

            self.ax_upper.set_ylim((self.min_value, self.max_value))
            self.ax_right.set_xlim((self.min_value, self.max_value))

            self.canvas_upper.draw()
            self.canvas_right.draw()

    def show(self):
        self.window.mainloop()


if __name__ == '__main__':
    gui = FringeGUI()
    gui.show()
