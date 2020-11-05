import tkinter as tk
from tkinter.filedialog import askopenfilename
import cv2
from FringeAnalysisFunctions import *


def select_file(entry):
    filepath = askopenfilename(
        filetypes=[
            ("JPEG files", ".jpeg .jpg .jpe"),
            ("JPEG 200 files", ".jp2"),
            ("Windows bitmaps", ".bmp .dib"),
            ("Portable Network Graphics", ".png"),
            ("TIFF files", ".tiff .tif"),
            ("All Files", "*.*")
        ]
    )

    entry.delete(0, tk.END)
    entry.insert(tk.END, filepath)


class FringeGUI:

    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Fringe Analysis Prototype")

        self.frm_input = tk.Frame(master=self.window, relief=tk.SUNKEN, borderwidth=5)
        self.frm_input.columnconfigure(1, minsize=200, weight=1)

        self.lbl_ref = tk.Label(master=self.frm_input, text='Reference picture: ')
        self.lbl_obj = tk.Label(master=self.frm_input, text='  Object picture : ')
        self.ent_ref = tk.Entry(master=self.frm_input)
        self.ent_obj = tk.Entry(master=self.frm_input)
        self.btn_select_ref = tk.Button(
            master=self.frm_input,
            text='Open..',
            command=lambda: select_file(self.ent_ref)
        )
        self.btn_select_obj = tk.Button(
            master=self.frm_input,
            text='Open..',
            command=lambda: select_file(self.ent_obj)
        )
        self.btn_submit = tk.Button(
            master=self.frm_input,
            text="Analyze",
            command=self.analyze
        )

        self.lbl_ref.grid(row=0, column=0, sticky='w')
        self.lbl_obj.grid(row=1, column=0, sticky='w')
        self.ent_ref.grid(row=0, column=1, sticky='ew')
        self.ent_obj.grid(row=1, column=1, sticky='ew')
        self.btn_select_ref.grid(row=0, column=2, padx=5, ipadx=5)
        self.btn_select_obj.grid(row=1, column=2, padx=5, ipadx=5)
        self.btn_submit.grid(row=2, column=1, padx=5, ipadx=5)

        self.frm_input.pack(fill=tk.X)

    def analyze(self, ks=5.7325):
        self.window.title("Fringe Analysis Prototype - Analyzing")

        ref_img = cv2.imread(self.ent_ref.get(), cv2.IMREAD_GRAYSCALE)
        obj_img = cv2.imread(self.ent_obj.get(), cv2.IMREAD_GRAYSCALE)

        pitch = getPitch(ref_img)

        ref_phase = fiveStepShift(ref_img, pitch, maskHoles=True)
        obj_phase = fiveStepShift(obj_img, pitch)

        diff = obj_phase - ref_phase

        unwrapped_phase_map = unwrapPhase(diff)
        depthMap = unwrapped_phase_map * ks

        self.window.title("Fringe Analysis Prototype - Done")

    def show(self):
        self.window.mainloop()


if __name__ == '__main__':
    gui = FringeGUI()
    gui.show()

