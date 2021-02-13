import tkinter as tk
from tkinter.filedialog import askopenfilename, askopenfilenames
from PIL import Image, ImageTk


class FileSelectionGui:
    """
        This is the universal file reading UI for Fringe Analysis Project
    """
    # Marks if the result is valid
    is_valid = False

    # Image Size
    img_size = 512

    # Results
    ref_file = None
    obj_file = None

    def __init__(self, root, calibration=False):
        """
            Initialize the UI with reference image input frame on the left and object image(s)
            input frame one the right, and submit button is at the bottom with cancel button
        """
        self.calibration = calibration
        self.window = tk.Toplevel(root.window)
        self.window.title('Image Selection')

        # Left frame
        self.frm_left = tk.Frame(master=self.window)

        # Text label and image preview label for reference input
        self.lbl_ref = tk.Label(master=self.frm_left, text='Select reference image: ')
        self.ref_img = ImageTk.PhotoImage(Image.new('RGB', (self.img_size, self.img_size), (240, 240, 240)))
        self.lbl_ref_img = tk.Label(master=self.frm_left, image=self.ref_img)

        self.lbl_ref.pack()
        self.lbl_ref_img.pack()

        # Reference Image Input Button
        self.btn_ref = tk.Button(master=self.window, text="Open..", command=self.select_ref_image)
        self.btn_ref.grid(row=2, column=0)

        self.frm_left.grid(row=0, column=0)

        # Right frame
        self.frm_right = tk.Frame(master=self.window)
        self.frm_right.grid(row=0, column=1)

        # Text label and image preview label for object(s) input
        self.lbl_obj = tk.Label(master=self.frm_right, text='Select object images: ')
        self.obj_img = ImageTk.PhotoImage(Image.new('RGB', (self.img_size, self.img_size), (240, 240, 240)))
        self.lbl_obj_img = tk.Label(master=self.frm_right, image=self.obj_img)

        self.lbl_obj.pack()
        self.lbl_obj_img.pack()

        # Object Image(s) Input Button
        self.btn_obj = tk.Button(master=self.window, text="Open..", command=self.select_obj_image)
        self.btn_obj.grid(row=2, column=1)

        # Calibration does not need multiple object input, hence, when not calibrating
        # do not show the slider for multiple preview images
        # do not show the slider for multiple preview images
        if not self.calibration:
            self.scl_obj = tk.Scale(master=self.window, command=self.redraw_obj, orient=tk.HORIZONTAL)
            self.scl_obj.grid(row=1, column=1)

        # Button Frame
        self.frm_button = tk.Frame(master=self.window)

        self.btn_submit = tk.Button(master=self.frm_button, text="Submit", command=self.check_and_submit)
        self.btn_submit.grid(row=0, column=1, ipadx=5, padx=5, pady=5)

        self.btn_cancel = tk.Button(master=self.frm_button, text="Cancel", command=self.cancel)
        self.btn_cancel.grid(row=0, column=0, ipadx=5, padx=5, pady=5)

        self.frm_button.grid(row=3, column=1)

        # Set the window not resizable so the layout would not be destroyed
        self.window.resizable(False, False)

    def select_ref_image(self):
        """
            Display an UI to ask for reference image name
        """
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

        image = Image.open(self.ref_file)

        height = image.height
        width = image.width

        if height > width:
            width = int(self.img_size / height * width)
            height = self.img_size
        else:
            height = int(self.img_size / width * height)
            width = self.img_size

        self.ref_img = ImageTk.PhotoImage(image.resize((width, height)))

        self.lbl_ref_img.configure(image=self.ref_img)

        self.window.lift()

    def select_obj_image(self):
        """
            Display an UI to ask for object images name
        """
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

        image = Image.open(self.obj_file[0])

        height = image.height
        width = image.width

        if height > width:
            width = int(self.img_size / height * width)
            height = self.img_size
        else:
            height = int(self.img_size / width * height)
            width = self.img_size

        self.obj_img = ImageTk.PhotoImage(image.resize((width, height)))
        self.lbl_obj_img.configure(image=self.obj_img)

        # Adaptation for calibration
        if not self.calibration:
            self.scl_obj.configure(from_=1, to=len(self.obj_file))

        self.window.lift()

    def redraw_obj(self, _=None):
        """
            redraw the preview object image according to update of the slider
        """
        if self.obj_file is None:
            return

        image = Image.open(self.obj_file[self.scl_obj.get() - 1])

        height = image.height
        width = image.width

        if height > width:
            width = int(self.img_size / height * width)
            height = self.img_size
        else:
            height = int(self.img_size / width * height)
            width = self.img_size

        self.obj_img = ImageTk.PhotoImage(image.resize((width, height)))
        self.lbl_obj_img.configure(image=self.obj_img)

    def check_and_submit(self):
        """
            Check if the results are valid for reading, if so destroy the window
        """
        if self.obj_file is not None and self.ref_file is not None:
            self.is_valid = True
            self.window.destroy()
        else:
            self.is_valid = False
            tk.messagebox.showerror(title="Invalid Input", message="Input is not valid!")

    def cancel(self):
        """
            Invalidate the result and destroy the window
        """
        self.obj_file = None
        self.ref_file = None
        self.is_valid = False
        self.window.destroy()
