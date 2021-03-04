import multiprocessing
import tkinter as tk


class SettingsGUI:
    is_valid = False

    using_multithreading = False
    num_threads = 0

    using_hole_masks = False

    ks = 0
    scale = 0
    frame_rate = 0

    using_filter = False
    extrapolation = 'nearest'
    smooth_filter = 'median'

    def __init__(self, root):
        self.using_multithreading = root.using_multithreading
        self.num_threads = root.num_threads
        self.using_hole_masks = root.using_hole_masks
        self.ks = root.ks
        self.scale = root.scale
        # self.using_filter = root.using_filter
        # self.extrapolation = root.extrapolation
        # self.smooth_filter = root.smooth_filter

        self.window = tk.Toplevel(root.window)
        self.window.title('Settings')

        self.var_ks = tk.StringVar()
        self.var_scale = tk.StringVar()
        self.var_hole_masks = tk.BooleanVar()
        self.var_multithreading = tk.BooleanVar()
        self.var_num_threads = tk.IntVar()
        # self.var_using_filter = tk.BooleanVar()
        # self.var_extrapolation = tk.StringVar()
        # self.var_smooth_filter = tk.StringVar()

        self.var_ks.set(str(self.ks))
        self.var_scale.set(str(self.scale))
        self.var_hole_masks.set(self.using_hole_masks)
        self.var_multithreading.set(self.using_multithreading)
        self.var_num_threads.set(self.num_threads)
        # self.var_using_filter.set(self.using_filter)
        # self.var_extrapolation.set(self.extrapolation)
        # self.var_smooth_filter.set(self.smooth_filter)

        self.lbl_ks = tk.Label(master=self.window, text='ks Value: ')
        self.lbl_scale = tk.Label(master=self.window, text='Scale: ')
        self.lbl_hole_masks = tk.Label(master=self.window, text='Enable Hole-Masking: ')
        self.lbl_multithreading = tk.Label(master=self.window, text='Enable Multithreading: ')
        self.lbl_num_threads = tk.Label(master=self.window,
                                        text='Number of Threads (Invalid when not using multithreading): ')
        # self.lbl_using_filter = tk.Label(master=self.window, text='Enable Filter: ')
        # self.lbl_extrapolation = tk.Label(master=self.window,
        #                                   text='Extrapolation Method (Invalid when not using filter): ')
        # self.lbl_smooth_filter = tk.Label(master=self.window, text='Smooth Filter (Invalid when not using filter): ')

        self.lbl_ks.grid(row=0, column=0, pady=5, padx=5)
        self.lbl_scale.grid(row=1, column=0, pady=5, padx=5)
        self.lbl_hole_masks.grid(row=2, column=0, pady=10, padx=5)
        self.lbl_multithreading.grid(row=3, column=0, pady=10, padx=5)
        self.lbl_num_threads.grid(row=4, column=0, pady=10, padx=5)
        # self.lbl_using_filter.grid(row=5, column=0, pady=10, padx=5)
        # self.lbl_extrapolation.grid(row=6, column=0, pady=5, padx=5)
        # self.lbl_smooth_filter.grid(row=7, column=0, pady=5, padx=5)

        self.ent_ks = tk.Entry(master=self.window, textvariable=self.var_ks)
        self.ent_scale = tk.Entry(master=self.window, textvariable=self.var_scale)
        self.chb_hole_masks = tk.Checkbutton(master=self.window, variable=self.var_hole_masks)
        self.chb_multithreading = tk.Checkbutton(master=self.window, variable=self.var_multithreading)
        self.scl_num_threads = tk.Scale(master=self.window, orient=tk.HORIZONTAL,
                                        from_=1, to=multiprocessing.cpu_count(), variable=self.var_num_threads)
        # self.chb_filter = tk.Checkbutton(master=self.window, variable=self.var_using_filter)
        # self.cbo_extrapolation = ttk.Combobox(
        #     master=self.window,
        #     textvariable=self.var_extrapolation,
        #     values=[
        #         'nearest',
        #         'linear',
        #         'cubic'
        #     ]
        # )
        # self.cbo_smooth_filter = ttk.Combobox(
        #     master=self.window,
        #     textvariable=self.var_smooth_filter,
        #     values=[
        #         'median',
        #         'mean',
        #         'none'
        #     ]
        # )

        self.ent_ks.grid(row=0, column=1, pady=5, padx=5)
        self.ent_scale.grid(row=1, column=1, pady=5, padx=5)
        self.chb_hole_masks.grid(row=2, column=1, pady=5, padx=5)
        self.chb_multithreading.grid(row=3, column=1, pady=5, padx=5)
        self.scl_num_threads.grid(row=4, column=1, pady=5, padx=5)
        # self.chb_filter.grid(row=5, column=1, pady=5, padx=5)
        # self.cbo_extrapolation.grid(row=6, column=1, pady=5, padx=5)
        # self.cbo_smooth_filter.grid(row=7, column=1, pady=5, padx=5)

        self.frm_button = tk.Frame(master=self.window)

        self.btn_submit = tk.Button(master=self.frm_button, text='Submit', command=self.submit)
        self.btn_cancel = tk.Button(master=self.frm_button, text='Cancel', command=self.cancel)

        self.btn_submit.grid(row=0, column=1, ipadx=5, padx=5, pady=5)
        self.btn_cancel.grid(row=0, column=0, ipadx=5, padx=5, pady=5)

        self.frm_button.grid(row=8, column=1, padx=5, pady=5)

        # Set the window not resizable so the layout would not be destroyed
        self.window.resizable(False, False)

    def submit(self):
        self.is_valid = True

        self.ks = float(self.var_ks.get())
        self.scale = float(self.var_scale.get())
        self.using_hole_masks = self.var_hole_masks.get()

        self.using_multithreading = self.var_multithreading.get()
        self.num_threads = self.var_num_threads.get()

        # self.using_filter = self.var_using_filter.get()
        # self.extrapolation = self.var_extrapolation.get()
        # self.smooth_filter = self.var_smooth_filter.get()

        # print(self.using_multithreading)
        # print(self.number_of_threads)
        # print(self.using_hole_masks)

        self.window.destroy()

    def cancel(self):
        self.is_valid = False
        self.window.destroy()

    # def show(self):
    #     self.window.mainloop()


if __name__ == '__main__':
    gui = SettingsGUI(tk.Tk())
    gui.show()
