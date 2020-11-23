import tkinter as tk
from tkinter import ttk
from utility.FringeAnalysisFunctions import *
import matplotlib
from matplotlib import cm
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from concurrent import futures
from GUIs.FileSelectionGUI import FileSelectionGui
from GUIs.PlotGUI import PlotGUI
from GUIs.SettingsGUI import SettingsGUI
# import time

matplotlib.use('TkAgg')

""" A GUIs module for the Fringe Analysis 
    

"""


class FringeGUI:
    ref_file = None
    obj_file = None

    ref_phase = None
    obj_phase = None

    diff_phase = None
    unwrapped_phase = None
    depth_map = None

    curr_map = None
    plot = None

    pitch = None

    max_value = None
    min_value = None

    ax_added = False

    # Setting Variables
    using_multithreading = False
    number_of_threads = 0

    ks = 5.7325

    using_hole_masks = False

    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Fringe Analysis Prototype")

        self.menu_bar = tk.Menu(master=self.window)
        self.menu_file = tk.Menu(master=self.menu_bar, tearoff=0)
        self.menu_help = tk.Menu(master=self.menu_bar, tearoff=0)

        self.menu_file.add_command(label="Open..", command=self.select_files)
        self.menu_file.add_command(label="Calibration", command=None)
        self.menu_file.add_separator()
        self.menu_file.add_command(label="Settings", command=self.change_settings)
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
        self.btn_plot = tk.Button(self.frm_right_upper, text="Plot in 3D", command=self.plot3D)

        self.cbo_map.pack()
        self.btn_show.pack()
        self.btn_plot.pack()

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

        self.scl_main = tk.Scale(master=self.frm_figs, from_=1, command=self.draw, orient=tk.HORIZONTAL)
        self.scl_main.grid(row=2, column=1, stick='ew')

        self.btn_next_pic = tk.Button(master=self.frm_figs, command=self.next_pic, text="->")
        self.btn_prev_pic = tk.Button(master=self.frm_figs, command=self.prev_pic, text="<-")

        self.btn_next_pic.grid(row=2, column=2, stick='w')
        self.btn_prev_pic.grid(row=2, column=0, stick='e')

        self.frm_figs.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.window.resizable(False, False)

    def next_pic(self):
        temp = self.scl_main.get()

        if temp + 1 <= self.scl_main["to"]:
            self.scl_main.set(temp + 1)

    def prev_pic(self):
        temp = self.scl_main.get()

        if temp - 1 >= 1:
            self.scl_main.set(temp - 1)

    def change_settings(self):
        setting_gui = SettingsGUI(self)

        self.window.wait_window(setting_gui.window)

        if setting_gui.is_valid:
            self.using_multithreading = setting_gui.using_multithreading
            self.number_of_threads = setting_gui.number_of_threads
            self.using_hole_masks = setting_gui.using_hole_masks

    def select_files(self):
        file_gui = FileSelectionGui(self)

        self.window.wait_window(file_gui.window)

        if file_gui.is_valid:
            self.ref_file = file_gui.ref_file
            self.obj_file = file_gui.obj_file

            self.analyze()

            self.scl_main.configure(from_=1, to=len(self.obj_file))
            self.draw()

    def analyze(self):
        ref_img = cv2.imread(self.ref_file, cv2.IMREAD_GRAYSCALE)
        obj_img = [cv2.imread(f, cv2.IMREAD_GRAYSCALE) for f in self.obj_file]

        self.pitch = getPitch(ref_img)

        self.ref_phase = fiveStepShift(ref_img, self.pitch, maskHoles=self.using_hole_masks)

        num_img = len(obj_img)

        if self.using_multithreading and num_img > self.number_of_threads:
            obj_number_per_thread = int(num_img / self.number_of_threads)
            future_list = []

            self.obj_phase = []
            self.diff_phase = []
            self.unwrapped_phase = []
            self.depth_map = []

            with futures.ThreadPoolExecutor() as executor:
                for i in range(self.number_of_threads):
                    start = i * obj_number_per_thread
                    end = (i + 1) * obj_number_per_thread if i + 1 != self.number_of_threads else num_img

                    future_list.append(
                        executor.submit(
                            analyze_phase,
                            self.ref_phase,
                            obj_img[start:end],
                            self.ks,
                            self.pitch
                        )
                    )

            for future in future_list:
                obj_phase_, diff_phase_, unwrapped_phase_, depth_map_ = future.result()
                self.obj_phase.extend(obj_phase_)
                self.diff_phase.extend(diff_phase_)
                self.unwrapped_phase.extend(unwrapped_phase_)
                self.depth_map.extend(depth_map_)
        else:
            self.obj_phase, self.diff_phase, self.unwrapped_phase, self.depth_map = analyze_phase(
                self.ref_phase,
                obj_img,
                self.ks,
                self.pitch
            )

    def draw(self, _=None):
        # print("Drawing!")

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

        if self.plot is None:
            self.plot = self.ax_main.imshow(self.curr_map, cmap=cm.turbo)
        else:
            self.plot.set_data(self.curr_map)

        self.fig_left.colorbar(self.plot, cax=self.ax_left)

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

    def plot3D(self):
        if self.curr_map is None:
            return

        # print("Calling PlotGUI")

        PlotGUI(self)

    def show(self):
        self.window.mainloop()


if __name__ == '__main__':
    main = FringeGUI()
    main.show()

    # from tkinter.filedialog import askopenfilename, askopenfilenames
    #
    # number_of_threads = 8
    # ks = 5.7325
    #
    # ref_file = askopenfilename()
    # obj_file = askopenfilenames()
    #
    # ref_img = cv2.imread(ref_file, cv2.IMREAD_GRAYSCALE)
    # obj_img = [cv2.imread(f, cv2.IMREAD_GRAYSCALE) for f in obj_file]
    #
    # pitch = getPitch(ref_img)
    #
    # ref_phase = fiveStepShift(ref_img, pitch, maskHoles=True)
    #
    # start_time = time.time()
    #
    # num_img = len(obj_img)
    #
    # obj_number_per_thread = int(num_img / number_of_threads)
    # future_list = []
    #
    # obj_phase = []
    # diff_phase = []
    # unwrapped_phase = []
    # depth_map = []
    #
    # with futures.ThreadPoolExecutor() as executor:
    #     for i in range(number_of_threads):
    #         start = i * obj_number_per_thread
    #         end = (i + 1) * obj_number_per_thread if i + 1 != number_of_threads else num_img
    #
    #         future_list.append(
    #             executor.submit(
    #                 analyze_phase,
    #                 ref_phase,
    #                 obj_img[start:end],
    #                 ks,
    #                 pitch
    #             )
    #         )
    #
    # for future in future_list:
    #     obj_phase_, diff_phase_, unwrapped_phase_, depth_map_ = future.result()
    #     obj_phase.extend(obj_phase_)
    #     diff_phase.extend(diff_phase_)
    #     unwrapped_phase.extend(unwrapped_phase_)
    #     depth_map.extend(depth_map_)
    #
    # end_time = time.time()
    #
    # print(f"Multithreading Version takes {end_time - start_time}s")
    #
    # start_time = time.time()
    #
    # obj_phase_2, diff_phase_2, unwrapped_phase_2, depth_map_2 = analyze_phase(
    #     ref_phase,
    #     obj_img,
    #     ks,
    #     pitch
    # )
    #
    # end_time = time.time()
    #
    # print(f"Single-thread Version takes {end_time - start_time}s")
    #
    # print(f"depth_map length is {len(depth_map)}")
    # print(f"depth_map_2 length is {len(depth_map_2)}")
    #
    # print(depth_map[0])
    # print(depth_map_2[0])