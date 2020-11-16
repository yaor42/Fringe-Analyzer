import tkinter as tk
import multiprocessing


class Settings:
    is_valid = False

    using_multithreading = False
    number_of_threads = 0

    using_hole_masks = False

    def __init__(self, root):
        self.using_multithreading = root.using_multithreading
        self.number_of_threads = root.number_of_threads
        self.using_hole_masks = root.using_hole_masks

        self.window = tk.Toplevel(root.window)
        self.window.title('Settings')

        self.lbl_multithreading = tk.Label(
            master=self.window,
            text="Enable Multithreading: "
        )
        self.lbl_num_threads = tk.Label(
            master=self.window,
            text="Number of Threads (Invalid when not using multithreading): "
        )
        self.lbl_hole_masks = tk.Label(
            master=self.window,
            text="Enable Hole-Masking: "
        )

        self.var_multithreading = tk.BooleanVar()
        self.var_num_threads = tk.IntVar()
        self.var_hole_masks = tk.BooleanVar()

        self.chb_multithreading = tk.Checkbutton(master=self.window, variable=self.var_multithreading)
        self.scl_num_threads = tk.Scale(
            master=self.window,
            orient=tk.HORIZONTAL,
            from_=1,
            to=multiprocessing.cpu_count(),
            variable=self.var_num_threads
        )
        self.chb_hole_masks = tk.Checkbutton(master=self.window, variable=self.var_hole_masks)

        self.var_multithreading.set(self.using_multithreading)
        self.var_num_threads.set(self.number_of_threads)
        self.var_hole_masks.set(self.using_hole_masks)

        self.lbl_multithreading.grid(row=0, column=0, pady=5)
        self.lbl_num_threads.grid(row=1, column=0, pady=5)
        self.lbl_hole_masks.grid(row=2, column=0, pady=5)

        self.chb_multithreading.grid(row=0, column=1, pady=5)
        self.scl_num_threads.grid(row=1, column=1, pady=5)
        self.chb_hole_masks.grid(row=2, column=1, pady=5)

        self.frm_button = tk.Frame(master=self.window)

        self.btn_submit = tk.Button(master=self.frm_button, text="Submit", command=self.submit)
        self.btn_cancel = tk.Button(master=self.frm_button, text="Cancel", command=self.cancel)

        self.btn_submit.grid(row=0, column=1, ipadx=5, padx=5, pady=5)
        self.btn_cancel.grid(row=0, column=0, ipadx=5, padx=5, pady=5)

        self.frm_button.grid(row=3, column=1)

    def submit(self):
        self.is_valid = True

        self.using_multithreading = self.var_multithreading.get()
        self.number_of_threads = self.var_num_threads.get()
        self.using_hole_masks = self.var_hole_masks.get()

        # print(self.using_multithreading)
        # print(self.number_of_threads)
        # print(self.using_hole_masks)

        self.window.destroy()

    def cancel(self):
        self.is_valid = False
        self.window.destroy()

    def show(self):
        self.window.mainloop()


if __name__ == '__main__':
    gui = Settings(tk.Tk())
    gui.show()
