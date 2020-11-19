import tkinter as tk
import numpy as np
import matplotlib
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.figure import Figure
from matplotlib.backend_bases import key_press_handler
from matplotlib import cm

matplotlib.use('TkAgg')


class PlotGUI:
    base_scale = 1.2

    def __init__(self, root):
        self.map = root.curr_map
        self.window = tk.Toplevel(root.window)

        height, length = self.map.shape

        self.axis_x = np.array([[x for x in range(length)] for _ in range(height)])
        self.axis_y = np.array([[x for _ in range(height)] for x in range(length)])

        self.fig = Figure()

        self.cnv = FigureCanvasTkAgg(self.fig, master=self.window)  # A tk.DrawingArea.
        self.cnv.draw()
        self.cnv.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        self.ax = self.fig.add_subplot(111, projection="3d")
        self.ax.plot_surface(
            self.axis_x,
            self.axis_y,
            self.map,
            rstride=int(height / 25),
            cstride=int(length / 25),
            cmap=cm.coolwarm,
            linewidth=0,
            antialiased=False
        )

        self.cnv.mpl_connect('scroll_event', self.zoom)

    def zoom(self, event):
        cur_xlim = self.ax.get_xlim()
        cur_ylim = self.ax.get_ylim()
        cur_zlim = self.ax.get_zlim()

        xdata = event.xdata  # get event x location
        ydata = event.ydata  # get event y location
        zdata = event.zdata

        if event.button == 'down':
            # deal with zoom in
            scale_factor = 1 / self.base_scale
        elif event.button == 'up':
            # deal with zoom out
            scale_factor = self.base_scale
        else:
            # deal with something that should never happen
            scale_factor = 1
            print(event.button)

        new_width = (cur_xlim[1] - cur_xlim[0]) * scale_factor
        new_height = (cur_ylim[1] - cur_ylim[0]) * scale_factor
        new_length = (cur_zlim[1] - cur_zlim[0]) * scale_factor

        relx = (cur_xlim[1] - xdata) / (cur_xlim[1] - cur_xlim[0])
        rely = (cur_ylim[1] - ydata) / (cur_ylim[1] - cur_ylim[0])
        relz = (cur_zlim[1] - zdata) / (cur_zlim[1] - cur_zlim[0])

        self.ax.set_xlim([xdata - new_width * (1 - relx), xdata + new_width * relx])
        self.ax.set_ylim([ydata - new_height * (1 - rely), ydata + new_height * rely])
        self.ax.set_zlim([zdata - new_length * (1 - relz), zdata + new_length * relz])

        self.cnv.draw()

    # def show(self):
    #     self.window.mainloop()
