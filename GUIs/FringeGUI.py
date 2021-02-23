import tkinter as tk
from tkinter import ttk

from concurrent import futures

import matplotlib
from matplotlib import cm
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from utility.FringeAnalysisFunctions import *

from GUIs.ExportGUI import ExportGUI
from GUIs.FileSelectionGUI import FileSelectionGui
from GUIs.PlotGUI import PlotGUI
from GUIs.SettingsGUI import SettingsGUI
from GUIs.CalibrationGUI import CalibrationGUI

matplotlib.use('TkAgg')


class FringeGUI:
    """
        A GUIs module for Fringe Analysis
    """

    # Store the file name(s) for reference file and object file(s)
    ref_file = None
    obj_file = None

    # Store the phase map from five step shift for both reference file and object file(s)
    # and difference phase, unwrapped phase map and depth map
    ref_phase = None
    obj_phase = None
    diff_phase = None
    unwrapped_phase = None
    depth_map = None

    # utility for analyzing
    pitch = None

    # curr_map stores the current map show on main GUI
    curr_map = None

    # Store the currently shown plot for display
    plot = None

    # Store the max and min value from the curr_map for side plot display to set their boundary
    max_value = None
    min_value = None

    # Boolean var determined by if main plot display is initialized
    ax_added = False

    # Setting Variables
    using_multithreading = False
    num_threads = 0

    using_hole_masks = False

    # k value and scale
    ks = 1.0
    scale = 1.0

    def __init__(self):
        """
            Initialization of the main UI

            The main UI was mainly inspired by the counterpart of Joshua. It is consisted of
            a drop down menu, a 3 * 3 gird frame that contains the figures and color bar along
            with some utilities.

            To understand what every grid does, please check the comments in the function.
        """

        self.window = tk.Tk()
        self.window.title("Fringe Analysis Prototype")

        # Creating the drop down Menu
        self.menu_bar = tk.Menu(master=self.window)
        self.menu_file = tk.Menu(master=self.menu_bar, tearoff=0)
        self.menu_help = tk.Menu(master=self.menu_bar, tearoff=0)

        self.menu_file.add_command(label="Open..", command=self.select_files)
        self.menu_file.add_command(label="Calibration", command=self.calibration)
        self.menu_file.add_separator()
        self.menu_file.add_command(label="Settings", command=self.change_settings)
        self.menu_file.add_separator()
        self.menu_file.add_command(label="Exit", command=self.window.quit)

        self.menu_bar.add_cascade(label="File", menu=self.menu_file)
        self.menu_bar.add_cascade(label="Help", menu=self.menu_help)

        # Creating right click menus
        self.right_click_menu = tk.Menu(master=self.window, tearoff=0)
        self.right_click_menu.add_command(label="Export as Image", command=self.export_image)
        self.right_click_menu.add_command(label="Export as CSV", command=self.export_csv)

        self.right_click_menu_all = tk.Menu(master=self.window, tearoff=0)
        self.right_click_menu_all.add_command(label="Export as Image", command=self.export_image)
        self.right_click_menu_all.add_command(label="Export as CSV", command=self.export_csv)
        self.right_click_menu_all.add_command(label="Export All as Image", command=self.export_image_all)
        self.right_click_menu_all.add_command(label="Export All as CSV", command=self.export_csv_all)

        # Showing the menu
        self.window.config(menu=self.menu_bar)

        # Creating the main frame for figs and utilities with configuration
        self.frm_figs = tk.Frame(master=self.window)

        self.frm_figs.rowconfigure(0, weight=4)
        self.frm_figs.rowconfigure(1, weight=1, minsize=200)
        self.frm_figs.columnconfigure(1, weight=1, minsize=200)
        self.frm_figs.columnconfigure(2, weight=4)

        self.frm_figs.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        """
            Creating the frame in gird at (0, 2) which holds a combo box along with a button that
            switches the figure displayed in the center and a single button that pops a new window
            with 3d plot of the selected data
        """
        self.frm_right_upper = tk.Frame(master=self.frm_figs)

        self.cbo_map = ttk.Combobox(
            master=self.frm_right_upper,
            value=[
                'Object Surface Contour',
                # 'Quality Map',
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

        self.frm_right_upper.grid(row=0, column=2)

        """
            These four Frame take the place of gird(0, 1), (1, 1), (1, 2), (1, 0)
            
            The frm_center_mid is the main display that shows result map selected in combo box from
            frm_right_upper
            
            The frm_center_upper and frm_right_mid interact the figure displayed in frm_center_mid
            check function self.onclick_main(event) for more information
            
            The frm_left_mid displays the color bar of the figure displayed in frm_center_mid
        """
        self.frm_center_upper = tk.Frame(master=self.frm_figs)
        self.frm_center_mid = tk.Frame(master=self.frm_figs)
        self.frm_right_mid = tk.Frame(master=self.frm_figs)
        self.frm_left_mid = tk.Frame(master=self.frm_figs)

        self.frm_center_upper.grid(row=0, column=1)
        self.frm_center_mid.grid(row=1, column=1)
        self.frm_right_mid.grid(row=1, column=2)
        self.frm_left_mid.grid(row=1, column=0)

        # Create and configure figure objects with utilities provided by matplotlib
        self.fig_upper = Figure(figsize=(5, 3))
        self.fig_right = Figure(figsize=(3, 5))
        self.fig_main = Figure(figsize=(5, 5))
        self.fig_left = Figure(figsize=(1, 5))

        self.fig_upper.patch.set_facecolor('#F0F0F0')
        self.fig_right.patch.set_facecolor('#F0F0F0')
        self.fig_main.patch.set_facecolor('#F0F0F0')
        self.fig_left.patch.set_facecolor('#F0F0F0')

        # Pre-setup for axes object from those figures providing manipulation for plots drawn
        self.ax_upper = None
        self.ax_right = None
        self.ax_main = None
        self.ax_left = None

        # Acquire and pack tkinter canvas objects from those figures into our UI
        self.canvas_upper = FigureCanvasTkAgg(self.fig_upper, master=self.frm_center_upper)
        self.canvas_right = FigureCanvasTkAgg(self.fig_right, master=self.frm_right_mid)
        self.canvas_main = FigureCanvasTkAgg(self.fig_main, master=self.frm_center_mid)
        self.canvas_left = FigureCanvasTkAgg(self.fig_left, master=self.frm_left_mid)

        self.canvas_upper.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.canvas_right.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.canvas_main.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.canvas_left.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # This scale object takes the place of (2, 1) which provides a slider bar to change
        # current displayed map
        self.scl_main = tk.Scale(master=self.frm_figs, from_=1, command=self.draw, orient=tk.HORIZONTAL)
        self.scl_main.grid(row=2, column=1, stick='ew', pady=(0, 17.5))

        # These two buttons take the place of (2, 0) and (2, 2) which provides a step changing
        # for map display
        self.btn_next_pic = tk.Button(master=self.frm_figs, command=self.next_pic, text="-->")
        self.btn_prev_pic = tk.Button(master=self.frm_figs, command=self.prev_pic, text="<--")

        self.btn_next_pic.grid(row=2, column=2, stick='w')
        self.btn_prev_pic.grid(row=2, column=0, stick='e')

        # Add right mouse click menu for frm_center_mid
        # self.frm_center_mid.bind("<Button-3>", self.do_popup)

        # Set the window not resizable so the layout would not be destroyed
        # self.window.resizable(False, False)

    def next_pic(self):
        """
            This function is binded to the btn_next_pic which changes map displayed to next one
        """
        temp = self.scl_main.get()

        if temp + 1 <= self.scl_main["to"]:
            self.scl_main.set(temp + 1)

    def prev_pic(self):
        """
            This function is bound to the btn_next_pic which changes map displayed to previous one
        """
        temp = self.scl_main.get()

        if temp - 1 >= 1:
            self.scl_main.set(temp - 1)

    def analyze(self):
        """
            Actually analyzing the input file(s) with multi-threading or not
        """

        ref_img = cv2.imread(self.ref_file, cv2.IMREAD_GRAYSCALE)
        obj_img = [cv2.imread(f, cv2.IMREAD_GRAYSCALE) for f in self.obj_file]

        self.pitch = getPitch(ref_img)

        self.ref_phase = fiveStepShift(ref_img, self.pitch, maskHoles=self.using_hole_masks)

        num_img = len(obj_img)

        if self.using_multithreading and num_img > self.num_threads:

            handler = MultiProcessHandler()

            self.obj_phase, self.diff_phase, self.unwrapped_phase, self.depth_map = handler.analyze_mp(
                self.ref_phase,
                obj_img,
                num_img,
                self.num_threads,
                self.ks,
                self.pitch
            )

        else:
            # Using a single thread
            self.obj_phase, self.diff_phase, self.unwrapped_phase, self.depth_map = analyze_phase(
                self.ref_phase,
                obj_img,
                self.ks,
                self.pitch
            )

    def draw(self, _=None):
        """
            This function draws or redraws the main display.
        """
        # print("Drawing!")

        # if the input is not valid, we do nothing
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
            # if axes are not already set, we create them here and set up function binding
            self.ax_added = True
            self.ax_upper = self.fig_upper.add_subplot(111)
            self.ax_right = self.fig_right.add_subplot(111)
            self.ax_main = self.fig_main.add_subplot(111)
            self.ax_left = self.fig_left.add_axes([0.6, 0.1, 0.15, 0.75])

            self.canvas_main.mpl_connect('button_press_event', self.onclick_main)

            self.canvas_upper.draw()
            self.canvas_right.draw()
        else:
            # if they are set, just remove the color bar for update
            self.ax_main.remove()
            self.ax_main = self.fig_main.add_subplot(111)
            self.plot = None
            self.ax_left.remove()
            self.ax_left = self.fig_left.add_axes([0.6, 0.1, 0.15, 0.75])

        if self.plot is None:
            # if main display is empty, we create new display
            self.plot = self.ax_main.imshow(self.curr_map, cmap=cm.turbo)
        else:
            # else, we just swap the data
            self.plot.set_data(self.curr_map)

        # Create new color bar for current data
        self.fig_left.colorbar(self.plot, cax=self.ax_left)
        self.ax_left.yaxis.set_ticks_position('left')

        self.canvas_main.draw()
        self.canvas_left.draw()

    def onclick_main(self, event):
        """
            This function updates plots in frm_center_up and frm_right_mid by a right mouse
            button click event from main display, figure in frm_center_up will display
            x-axis data from the click location and figure in frm_right_mid will display
            y-axis data form the click location
        """
        # print('%s click: button=%d, x=%d, y=%d, xdata=%f, ydata=%f' %
        #       ('double' if event.dblclick else 'single', event.button,
        #        event.x, event.y, event.xdata, event.ydata))

        if event.button == 1:
            height = len(self.curr_map)
            width = len(self.curr_map[0])

            # print(f"h = {height}, w = {width}")

            x_offset = 0
            y_offset = 0

            if height > width:
                x_offset = (height - width) / 2
            elif height < width:
                y_offset = (width - height) / 2

            x = self.curr_map[:, int(event.xdata)]
            y = self.curr_map[int(event.ydata), :]
            axis_x = [i for i in range(len(x))]
            axis_y = [i for i in range(len(y))]

            self.ax_upper.clear()
            self.ax_right.clear()

            self.ax_upper.plot(axis_y, y)
            self.ax_right.plot(x, axis_x)

            self.ax_upper.set_xlim((- x_offset, x_offset + len(y) - 1))
            self.ax_upper.set_ylim((self.min_value, self.max_value))

            self.ax_right.set_xlim((self.min_value, self.max_value))
            self.ax_right.set_ylim((y_offset + len(x) - 1, - y_offset))

            self.canvas_upper.draw()
            self.canvas_right.draw()

        elif event.button == 3:
            selected_map = self.cbo_map.get()

            if selected_map == 'Reference Phase' or len(self.depth_map) == 1:
                try:
                    self.right_click_menu.tk_popup(
                        self.frm_center_mid.winfo_rootx() + event.x,
                        self.frm_center_mid.winfo_rooty() + self.frm_center_mid.winfo_height() - event.y
                    )
                finally:
                    self.right_click_menu.grab_release()
            else:
                try:
                    self.right_click_menu_all.tk_popup(
                        self.frm_center_mid.winfo_rootx() + event.x,
                        self.frm_center_mid.winfo_rooty() + self.frm_center_mid.winfo_height() - event.y
                    )
                finally:
                    self.right_click_menu_all.grab_release()

    def export_image(self):
        """
            Opens a new UI to select where to store the image
        """
        export_gui = ExportGUI(self, 'image')

        self.window.wait_window(export_gui.window)

    def export_csv(self):
        """
            Opens a new UI to select where to store the csv
        """
        export_gui = ExportGUI(self, 'csv')

        self.window.wait_window(export_gui.window)

    def export_image_all(self):
        """
            Opens a new UI to select where to store the image
        """
        export_gui = ExportGUI(self, 'image', all=True)

        self.window.wait_window(export_gui.window)

    def export_csv_all(self):
        """
            Opens a new UI to select where to store the csvs
        """
        export_gui = ExportGUI(self, 'csv', all=True)

        self.window.wait_window(export_gui.window)

    def change_settings(self):
        """
            Opens a new UI to change or check the current settings of the program
        """
        setting_gui = SettingsGUI(self)

        self.window.wait_window(setting_gui.window)

        if setting_gui.is_valid:
            self.using_multithreading = setting_gui.using_multithreading
            self.num_threads = setting_gui.number_of_threads
            self.using_hole_masks = setting_gui.using_hole_masks

    def select_files(self):
        """
            Opens a new UI to select reference file and object file(s) for the program
        """
        file_gui = FileSelectionGui(self)

        self.window.wait_window(file_gui.window)

        if file_gui.is_valid:
            self.ref_file = file_gui.ref_file
            self.obj_file = file_gui.obj_file

            self.analyze()

            self.scl_main.configure(from_=1, to=len(self.obj_file))
            self.draw()

    def plot3D(self):
        """
            Opens a new UI displaying 3D plot of the current map
        """
        if self.curr_map is None:
            return

        # print("Calling PlotGUI")

        PlotGUI(self, self.scale)

    def calibration(self):
        """
            Opens a new UI for calibration of the ks and scale value
        """
        cal_gui = CalibrationGUI(self)

        self.window.wait_window(cal_gui.window)

        if cal_gui.is_valid:
            self.ks = cal_gui.ks
            self.scale = cal_gui.scale

    def show(self):
        """
            Displays the UI we created
        """
        self.window.mainloop()


class MultiProcessHandler:
    def analyze_mp(self, ref_phase, obj_img, num_img, num_threads, ks, pitch):
        obj_number_per_thread = int(num_img / num_threads)
        future_list = []

        obj_phase = []
        diff_phase = []
        unwrapped_phase = []
        depth_map = []

        with futures.ThreadPoolExecutor() as executor:
            for i in range(num_threads):
                start = i * obj_number_per_thread
                end = (i + 1) * obj_number_per_thread if i + 1 != num_threads else num_img

                future_list.append(
                    executor.submit(
                        analyze_phase,
                        ref_phase,
                        obj_img[start:end],
                        ks,
                        pitch
                    )
                )

        for future in future_list:
            obj_phase_, diff_phase_, unwrapped_phase_, depth_map_ = future.result()
            obj_phase.extend(obj_phase_)
            diff_phase.extend(diff_phase_)
            unwrapped_phase.extend(unwrapped_phase_)
            depth_map.extend(depth_map_)

        return obj_phase, diff_phase, unwrapped_phase, depth_map


if __name__ == '__main__':
    main = FringeGUI()
    main.show()
