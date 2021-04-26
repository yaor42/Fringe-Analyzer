import json
import multiprocessing
import tkinter as tk
from concurrent import futures
from tkinter import ttk

import matplotlib
from matplotlib import cm
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.patches import Circle, Rectangle

from GUIs.CalibrationGUI import CalibrationGUI
from GUIs.ExportGUI import ExportGUI
from GUIs.FileSelectionGUI import FileSelectionGui
from GUIs.PlotGUI import PlotGUI
from GUIs.RangeSettingGUI import RangeSettingGUI
from GUIs.SettingsGUI import SettingsGUI
from GUIs.TrackPointGUI import TrackPointGUI
from GUIs.TrackRangeGUI import TrackRangeGUI
from utility.FringeAnalysisFunctions import *

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

    # counter for progress display
    counter = 0
    num_img = 0

    # utility for analyzing
    pitch = None

    # curr_map stores the current map show on main GUI
    curr_map = None

    # Store the currently shown plot and data for display
    plot = None
    lx = None
    ly = None
    cache_x = 0
    cache_y = 0

    patch_dict = {}

    # Store the max and min value from the curr_map for side plot display to set their boundary
    obj_phase_maxv = None
    obj_phase_minv = None
    diff_phase_maxv = None
    diff_phase_minv = None
    unwrapped_phase_maxv = None
    unwrapped_phase_minv = None
    depth_map_maxv = None
    depth_map_minv = None

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

    # Filter options
    using_filter = False
    extrapolation = "nearest"
    smooth_filter = "none"

    def __init__(self):
        """
            Initialization of the main UI

            The main UI was mainly inspired by the counterpart of Joshua. It is consisted of
            a drop down menu, a 3 * 3 gird frame that contains the figures and color bar along
            with some utilities.

            To understand what every grid does, please check the comments in the function.
        """

        self.import_settings()

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
        self.right_click_menu.add_command(label="Set Value Range", command=self.set_range)
        self.right_click_menu.add_separator()
        self.right_click_menu.add_command(label="Export as Image", command=self.export_image)
        self.right_click_menu.add_command(label="Export as CSV", command=self.export_csv)

        self.right_click_menu_all = tk.Menu(master=self.window, tearoff=0)
        self.right_click_menu_all.add_command(label="Track Point", command=self.track_point)
        self.right_click_menu_all.add_command(label="Track Range", command=self.track_range)
        self.right_click_menu_all.add_command(label="Set Value Range", command=self.set_range)
        self.right_click_menu_all.add_separator()
        self.right_click_menu_all.add_command(label="Export as Image", command=self.export_image)
        self.right_click_menu_all.add_command(label="Export as CSV", command=self.export_csv)
        self.right_click_menu_all.add_command(label="Export All as Image", command=self.export_image_all)
        self.right_click_menu_all.add_command(label="Export All as CSV", command=self.export_csv_all)

        # Showing the menu
        self.window.config(menu=self.menu_bar)

        self.frm_main = tk.Frame(master=self.window)
        self.frm_main.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Creating the main frame for figs and utilities with configuration
        self.frm_figs = tk.Frame(master=self.frm_main)

        self.frm_figs.rowconfigure(0, weight=4)
        self.frm_figs.rowconfigure(1, weight=1, minsize=100)
        self.frm_figs.columnconfigure(1, weight=1, minsize=100)
        self.frm_figs.columnconfigure(2, weight=4)

        # self.frm_figs.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.frm_figs.grid(row=0, column=0)

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
        self.btn_plot = tk.Button(self.frm_right_upper, text="Plot in 3D", command=self.plot3d)

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
        self.fig_upper = Figure(figsize=(5, 3), dpi=75, facecolor='#F0F0F0')
        self.fig_right = Figure(figsize=(3, 5), dpi=75, facecolor='#F0F0F0')
        self.fig_main = Figure(figsize=(5, 5), dpi=75, facecolor='#F0F0F0')
        self.fig_left = Figure(figsize=(1, 5), dpi=75, facecolor='#F0F0F0')

        self.fig_upper.subplots_adjust(bottom=0.15)
        self.fig_right.subplots_adjust(left=0.3)

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

        # UI for tracking utilities
        self.frm_track = tk.Frame(master=self.frm_main)

        self.frm_track.grid(row=0, column=1, padx=5, pady=5, sticky=tk.NSEW)

        self.frm_point = tk.Frame(master=self.frm_track)

        self.lbl_point = tk.Label(master=self.frm_point, text="Tracking Table")
        self.lbl_point.pack(fill=tk.BOTH, padx=5, pady=5)

        self.frm_table = tk.Frame(master=self.frm_point)

        self.trv_track = ttk.Treeview(master=self.frm_table, columns=('x', 'y', 'value'))
        # self.trv_track = ttk.Treeview(master=self.frm_table, columns=('x', 'y', 'value', 'roi'))
        self.vsb_track = tk.Scrollbar(master=self.frm_table, orient='vertical', command=self.trv_track.yview)
        self.trv_track.configure(yscrollcommand=self.vsb_track.set)

        self.trv_track.column('#0', stretch=tk.NO, minwidth=0, width=0)
        self.trv_track.heading("x", text='x')
        self.trv_track.column("x", anchor='c', width=64)
        self.trv_track.heading("y", text='y')
        self.trv_track.column("y", anchor='c', width=64)
        self.trv_track.heading("value", text='value')
        self.trv_track.column("value", anchor='c', width=128)
        # self.trv_track.column('roi', stretch=tk.NO, minwidth=0, width=0)

        self.trv_track.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.vsb_track.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.frm_table.pack(fill=tk.BOTH, expand=True)

        self.btn_stop_track = tk.Button(master=self.frm_point, text=' Delete ', command=self.stop_track)
        self.btn_stop_track.pack(side=tk.LEFT, pady=5)
        self.btn_track = tk.Button(master=self.frm_point, text='Export..', command=self.export_points)
        self.btn_track.pack(side=tk.RIGHT, padx=5, pady=5)

        self.frm_point.pack(fill=tk.Y, expand=True)

        self.var_coord = tk.StringVar()
        self.lbl_coord = tk.Label(master=self.window, textvariable=self.var_coord, relief="sunken")
        self.lbl_coord.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        # Set the window not resizable so the layout would not be destroyed
        self.window.resizable(False, False)
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)

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

    def finish_one(self):
        self.counter += 1
        self.window.title(f"Fringe Analysis Prototype - Processing {self.counter}/{self.num_img}")

    def analyze(self):
        """
            Actually analyzing the input file(s) with multi-threading or not
        """

        ref_img = cv2.imread(self.ref_file, cv2.IMREAD_GRAYSCALE)
        obj_img = [cv2.imread(f, cv2.IMREAD_GRAYSCALE) for f in self.obj_file]

        self.pitch = getPitch(ref_img)

        self.ref_phase = fiveStepShift(ref_img, self.pitch, maskHoles=self.using_hole_masks)

        self.counter = 0
        self.num_img = len(obj_img)

        self.window.title(f"Fringe Analysis Prototype - Processing {self.counter}/{self.num_img}")

        if self.using_multithreading and self.num_img > self.num_threads:
            self.obj_phase, self.diff_phase, self.unwrapped_phase, self.depth_map = MultiProcessHandler.analyze_mp(
                self.ref_phase,
                obj_img,
                self.num_img,
                self.num_threads,
                self.ks,
                self.pitch
            )
        else:
            # Using a single thread
            self.obj_phase, self.diff_phase, self.unwrapped_phase, self.depth_map = analyze_phase(
                self,
                self.ref_phase,
                obj_img,
                self.ks,
                self.pitch
            )

        # self.obj_phase_minv, self.obj_phase_maxv = find_range_from_maps(self.obj_phase)
        # self.diff_phase_minv, self.diff_phase_maxv = find_range_from_maps(self.diff_phase)
        # self.unwrapped_phase_minv, self.unwrapped_phase_maxv = find_range_from_maps(self.unwrapped_phase)
        # self.depth_map_minv, self.depth_map_maxv = find_range_from_maps(self.depth_map)

        self.window.title("Fringe Analysis Prototype - Done!")

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
            self.max_value = self.depth_map_maxv
            self.min_value = self.depth_map_minv
        elif selected_map == 'Quality Map':
            return
        elif selected_map == 'Wrapped Phase Map':
            self.curr_map = self.diff_phase[self.scl_main.get() - 1]
            self.max_value = self.diff_phase_maxv
            self.min_value = self.diff_phase_minv
        elif selected_map == 'Object Phase':
            self.curr_map = self.obj_phase[self.scl_main.get() - 1]
            self.max_value = self.obj_phase_maxv
            self.min_value = self.obj_phase_minv
        elif selected_map == 'Reference Phase':
            self.curr_map = self.ref_phase
            self.max_value = max([max(i) for i in self.curr_map])
            self.min_value = min([min(i) for i in self.curr_map])

        if not self.ax_added:
            # if axes are not already set, we create them here and set up function binding
            self.ax_added = True
            self.ax_upper = self.fig_upper.add_subplot(111)
            self.ax_upper.set_xlabel('x axis')
            self.ax_upper.set_ylabel('depth')

            self.ax_right = self.fig_right.add_subplot(111)
            self.ax_right.set_xlabel('depth')
            self.ax_right.set_ylabel('y axis')

            self.ax_main = self.fig_main.add_subplot(111)
            self.ax_left = self.fig_left.add_axes([0.6, 0.1, 0.15, 0.75])

            self.lx = self.ax_main.axhline(color='k')
            self.ly = self.ax_main.axvline(color='k')

            self.canvas_main.mpl_connect('button_press_event', self.onclick_main)
            self.canvas_main.mpl_connect('motion_notify_event', self.onmove_main)

            self.canvas_upper.draw()
            self.canvas_right.draw()
        else:
            self.ax_main.remove()
            self.ax_main = self.fig_main.add_subplot(111)
            self.lx = self.ax_main.axhline(color='k')
            self.ly = self.ax_main.axvline(color='k')
            self.plot = None
            self.ax_left.remove()
            self.ax_left = self.fig_left.add_axes([0.6, 0.1, 0.15, 0.75])

        # if self.plot is None:
        # # if main display is empty, we create new display
        self.plot = self.ax_main.imshow(self.curr_map, vmax=self.max_value, vmin=self.min_value, cmap=cm.turbo)
        # print(self.curr_map[0][0])

        for value in self.patch_dict.values():
            if value is not None:
                value.remove()

        self.patch_dict = {}

        for item in self.trv_track.get_children():
            strs = item.split(' ')
            if strs[0] == 'point':
                coord = strs[1].split(',')

                x = int(coord[0])
                y = int(coord[1])

                self.trv_track.delete(item)
                self.trv_track.insert('', 'end', f'point {x},{y}', values=(x, y, f'{self.curr_map[x][y]:.5}'))
                self.patch_dict[f'point {x},{y}'] = self.ax_main.add_patch(Circle((x, y), 4, facecolor='none',
                                                                             edgecolor='black', fill=True))
            else:
                coord = strs[1].split(',')

                x1 = int(coord[0])
                y1 = int(coord[1])
                x2 = int(coord[2])
                y2 = int(coord[3])

                self.trv_track.delete(item)
                self.trv_track.insert('', 'end', f'range {x1},{y1},{x2},{y2}',
                                      values=(f'{x1} - {x2}', f'{y1} - {y2}', '-'))

                self.patch_dict[f'range {x1},{y1},{x2},{y2}'] = self.ax_main.add_patch(
                    Rectangle((x1, y2), width=x2 - x1, height=y1 - y2, facecolor='none', edgecolor='black')
                )

        # Create new color bar for current data
        self.fig_left.colorbar(self.plot, cax=self.ax_left)
        self.ax_left.yaxis.set_ticks_position('left')

        self.canvas_main.draw()
        self.canvas_left.draw()

    def onmove_main(self, event):
        # print(event)

        if not event.inaxes:
            return

        x, y = int(event.xdata), int(event.ydata)
        # update the line positions
        self.lx.set_ydata(y)
        self.ly.set_xdata(x)

        # print(f"x = {x}, y = {y}")

        self.var_coord.set(f"x = {x}, y = {y}, value = {self.curr_map[int(y)][int(x)]}")

        self.canvas_main.draw()

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
        print(event)

        if event.xdata is None or event.ydata is None:
            pass

        if event.button == 1:
            if event.dblclick:
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

                self.ax_upper.set_xlabel('x axis')
                self.ax_upper.set_ylabel('depth')
                self.ax_upper.set_xlim((- x_offset, x_offset + len(y) - 1))
                self.ax_upper.set_ylim((self.min_value, self.max_value))

                self.ax_right.set_xlabel('depth')
                self.ax_right.set_ylabel('y axis')
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
                self.cache_x = int(event.xdata)
                self.cache_y = int(event.ydata)

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
            Opens a new UI to select where to store images
        """
        export_gui = ExportGUI(self, 'image', export_all=True)

        self.window.wait_window(export_gui.window)

    def export_csv_all(self):
        """
            Opens a new UI to select where to store csvs
        """
        export_gui = ExportGUI(self, 'csv', export_all=True)

        self.window.wait_window(export_gui.window)

    def export_points(self):
        """
            Opens a new UI to select where to store csvs from point tracking
        """
        if len(self.trv_track.get_children()) != 0:
            export_gui = ExportGUI(self, 'csv', track=True)

            self.window.wait_window(export_gui.window)

    def set_range(self):
        """
            Set a range for the color bar
        """
        range_gui = RangeSettingGUI(self)

        self.window.wait_window(range_gui.window)

        if range_gui.is_valid:
            selected_map = self.cbo_map.get()

            if selected_map == 'Object Surface Contour':
                self.depth_map_maxv = range_gui.max_value
                self.depth_map_minv = range_gui.min_value
            elif selected_map == 'Wrapped Phase Map':
                self.diff_phase_maxv = range_gui.max_value
                self.diff_phase_minv = range_gui.min_value
            elif selected_map == 'Object Phase':
                self.obj_phase_maxv = range_gui.max_value
                self.obj_phase_minv = range_gui.min_value

            self.draw()

    def track_point(self):
        """
            Add point into the tracking list
        """
        # hash_string = f'{self.x_cache}, {self.y_cache}'
        #
        # self.trv_track.insert('', 'end', hash_string,
        #                       values=(self.x_cache, self.y_cache, f'{self.curr_map[self.y_cache][self.x_cache]:.5}'))
        # self.patch_dict[hash_string] = self.ax_main.add_patch(Circle((self.x_cache, self.y_cache), 4,
        #                                                              facecolor='none', edgecolor='black', fill=True))
        track_gui = TrackPointGUI(self)

        self.window.wait_window(track_gui.window)

        if track_gui.is_valid:
            hash_string = f'point {track_gui.x},{track_gui.y}'

            self.trv_track.insert('', 'end', hash_string,
                                  values=(track_gui.x, track_gui.y, f'{self.curr_map[track_gui.y][track_gui.x]:.5}'))
            self.patch_dict[hash_string] = self.ax_main.add_patch(Circle((track_gui.x, track_gui.y), 4,
                                                                         facecolor='none', edgecolor='black',
                                                                         fill=True))

    def track_range(self):
        track_gui = TrackRangeGUI(self)

        self.window.wait_window(track_gui.window)

        if track_gui.is_valid:
            hash_string = f'range {track_gui.x1},{track_gui.y1},{track_gui.x2},{track_gui.y2}'

            self.trv_track.insert('', 'end', hash_string,
                                  values=(f'{track_gui.x1} - {track_gui.x2}', f'{track_gui.y1} - {track_gui.y2}', '-'))
            self.patch_dict[hash_string] = self.ax_main.add_patch(
                Rectangle(
                    (track_gui.x1, track_gui.y2),
                    width=track_gui.x2 - track_gui.x1,
                    height=track_gui.y1 - track_gui.y2,
                    facecolor='none',
                    edgecolor='black'
                )
            )

    def stop_track(self):
        """
            Delete the point selected from the tracking list
        """
        selection = self.trv_track.selection()

        for item in selection:
            self.patch_dict[item].remove()
            self.patch_dict[item] = None
            self.trv_track.delete(item)

        self.canvas_main.draw()

    def change_settings(self):
        """
            Opens a new UI to change or check the current settings of the program
        """
        setting_gui = SettingsGUI(self)

        self.window.wait_window(setting_gui.window)

        if setting_gui.is_valid:
            self.ks = setting_gui.ks
            self.scale = setting_gui.scale
            self.using_hole_masks = setting_gui.using_hole_masks

            self.using_multithreading = setting_gui.using_multithreading
            self.num_threads = setting_gui.num_threads

            self.using_filter = setting_gui.using_filter
            self.extrapolation = setting_gui.extrapolation
            self.smooth_filter = setting_gui.smooth_filter

    def select_files(self):
        """
            Opens a new UI to select reference file and object file(s) for the program
        """
        file_gui = FileSelectionGui(self)

        self.window.wait_window(file_gui.window)

        if file_gui.is_valid:
            for key, value in self.patch_dict.items():
                value.remove()
                self.trv_track.delete(key)
            self.patch_dict = {}

            self.ref_file = file_gui.ref_file
            self.obj_file = file_gui.obj_file

            if len(self.obj_file) == 1:
                self.btn_next_pic['state'] = tk.DISABLED
                self.btn_prev_pic['state'] = tk.DISABLED
            else:
                self.btn_next_pic['state'] = tk.ACTIVE
                self.btn_prev_pic['state'] = tk.ACTIVE

            self.analyze()

            self.scl_main.configure(from_=1, to=len(self.obj_file))
            self.draw()

    def plot3d(self):
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

    def on_close(self):
        settings = {
            "multithreading": self.using_multithreading,
            "num_threads": self.num_threads,
            "using_hole_masks": self.using_hole_masks,
            "ks": self.ks,
            "scale": self.scale
        }

        settings_json = json.dumps(settings)
        with open("settings.json", 'w') as file:
            file.write(settings_json)

        self.window.destroy()

    def show(self):
        """
            Displays the UI we created
        """
        self.window.mainloop()

    def import_settings(self):
        if os.path.exists("settings.json"):
            with open("settings.json", 'r') as file:
                settings_json = json.load(file)

                self.using_multithreading = settings_json['multithreading']
                self.num_threads = min(multiprocessing.cpu_count(), settings_json['num_threads'])
                self.using_hole_masks = settings_json['using_hole_masks']
                self.ks = settings_json['ks']
                self.scale = settings_json['scale']


class MultiProcessHandler:
    @staticmethod
    def analyze_mp(ref_phase, obj_img, num_img, num_threads, ks, pitch):
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
                        analyze_phase_mt,
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
