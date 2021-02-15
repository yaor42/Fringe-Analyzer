import tkinter as tk
from tkinter.filedialog import asksaveasfilename
import numpy as np
import matplotlib
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.figure import Figure
from matplotlib.backend_bases import key_press_handler
from matplotlib import cm

matplotlib.use('TkAgg')


def find_range(map):
    min_value = map[0][0]
    max_value = map[0][0]

    for row in map:
        for elem in row:
            if min_value > elem:
                min_value = elem
            if max_value < elem:
                max_value = elem

    return min_value, max_value


class PlotGUI:
    zoom_scale = 0.2

    def __init__(self, root, base_scale):
        self.base_scale = base_scale
        self.map = root.curr_map

        self.window = tk.Toplevel(root.window)

        self.menu_bar = tk.Menu(master=self.window)
        self.menu_file = tk.Menu(master=self.menu_bar, tearoff=0)

        self.menu_file.add_command(label="Save As..", command=self.save_fig)
        self.menu_file.add_separator()
        self.menu_file.add_command(label="Exit", command=self.window.quit)

        self.menu_bar.add_cascade(label="File", menu=self.menu_file)

        self.window.config(menu=self.menu_bar)

        height, length = self.map.shape

        self.axis_x = np.array([[x * base_scale for x in range(length)] for _ in range(height)])
        self.axis_y = np.array([[x * base_scale for _ in range(length)] for x in range(height)])

        self.fig = Figure()

        self.cnv = FigureCanvasTkAgg(self.fig, master=self.window)  # A tk.DrawingArea.
        self.cnv.draw()
        self.cnv.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        # print(self.axis_x.shape)
        # print(self.axis_y.shape)
        # print(self.map.shape)

        self.ax = self.fig.add_subplot(111, projection="3d")
        self.ax.plot_surface(
            self.axis_x,
            self.axis_y,
            self.map,
            rstride=int(height / 50),
            cstride=int(length / 50),
            cmap=cm.turbo,
            linewidth=0,
            antialiased=False
        )

        minx, maxx, miny, maxy, minz, maxz = self.ax.get_w_lims()
        self.ax.set_ylim3d((maxy, miny))
        self.ax.set_zlim3d((minz, length * base_scale))

        # def zoom(event):
        #     if event.button == 'down':
        #         scale_factor = self.zoom_scale
        #     elif event.button == 'up':
        #         scale_factor = - self.zoom_scale
        #     else:
        #         scale_factor = 0
        #
        #     minx, maxx, miny, maxy, minz, maxz = self.ax.get_w_lims()
        #     dx = (maxx - minx) * scale_factor
        #     dy = (maxy - miny) * scale_factor
        #     dz = (maxz - minz) * scale_factor
        #
        #     self.ax.set_xlim3d(minx - dx, maxx + dx)
        #     self.ax.set_ylim3d(miny - dy, maxy + dy)
        #     self.ax.set_zlim3d(minz - dz, maxz + dz)
        #
        #     self.ax.get_proj()
        #     self.cnv.draw_idle()
        #
        # self.cnv.mpl_connect('scroll_event', zoom)

        # Set the window not resizable so the layout would not be destroyed
        self.window.resizable(False, False)

    def save_fig(self):
        filename = asksaveasfilename(
            title="Save as..",
            defaultextension='.png',
            filetypes=[
                ("Portable Network Graphics", ".png"),
                ("JPEG files", ".jpeg .jpg .jpe"),
                ("JPEG 200 files", ".jp2"),
                ("Windows bitmaps", ".bmp .dib"),
                ("TIFF files", ".tiff .tif"),
                ("All Files", "*.*")
            ]
        );
        self.fig.savefig(filename)

    # def show(self):
    #     self.window.mainloop()
