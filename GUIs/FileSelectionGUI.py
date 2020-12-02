import tkinter as tk
from tkinter.filedialog import askopenfilename, askopenfilenames
from PIL import Image, ImageTk


class FileSelectionGui:
    is_valid = False

    ref_file = None
    obj_file = None

    def __init__(self, root, calibration=False):
        self.window = tk.Toplevel(root.window)
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
        if not calibration:
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
