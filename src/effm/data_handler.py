"""
Simple module with a class to manage the input data
"""

import os
import tkinter as tk
from tkinter import filedialog

import pandas as pd
import ttkbootstrap as tb  # pylint:disable=import-error
import yaml

from effm.utils import enforce_trailing_slash


# pylint:disable=too-many-instance-attributes, too-few-public-methods
class TkWindow:
    """
    Class to create and configure a ttkbootstrap window (GUI to launch the script)
    """

    # pylint:disable=too-many-statements, too-many-locals
    def __init__(self) -> None:
        """
        Init method
        """
        self.window = tb.Window(themename="darkly")
        self.window.geometry("400x550")
        self.window.resizable(True, False)
        self.window.title("Menu")

        my_btn_style = tb.Style()
        my_btn_style.configure("mySubmit.success.TButton", font=("gothic", 13))

        padx_in_frame = 10
        pady_in_frame = 10
        padx_frame = 5
        pady_frame = 1

        # header
        label_header = tb.Label(
            self.window, text="Générateur de rapports  individuels", font=("gothic", 14, "bold")
        )
        label_header.pack(expand=True, padx=padx_in_frame, pady=pady_in_frame)

        label_input = tb.Label(self.window, text="Input", font=("Helvetica", 11))
        frame_input = tb.LabelFrame(self.window, labelwidget=label_input)
        # define left and right columns
        left_frame_input = [tb.Frame(frame_input)] * 1
        right_frame_input = [tb.Frame(frame_input)] * 1
        # input file
        self.name_infile = tb.StringVar(value="path/myExcelFile.xlsx")
        self.entry_infile = tb.Entry(right_frame_input[0], textvariable=self.name_infile)
        self.entry_infile.pack(expand=True, fill=tb.X, padx=padx_in_frame, pady=pady_in_frame)
        btn_infile = tb.Button(
            left_frame_input[0], text="Sélectionner le fichier Excel", command=self.__browse_file
        )
        btn_infile.pack(expand=True, fill=tb.X, padx=padx_in_frame, pady=pady_in_frame)

        # frame for the exam configuration
        label_exam = tb.Label(self.window, text="Exam", font=("Helvetica", 11))
        frame_exam = tb.LabelFrame(self.window, labelwidget=label_exam)
        # define left and right columns
        left_frame_exam = [tb.Frame(frame_exam)] * 4
        right_frame_exam = [tb.Frame(frame_exam)] * 4
        # field
        label_field = tb.Label(left_frame_exam[0], text="Matière")
        label_field.pack(
            expand=True, fill=tb.X, padx=padx_in_frame, pady=pady_in_frame
        )  # grid(row=1, column=0)
        self.field = tb.StringVar(value="Physique")
        self.entry_field = tb.Entry(right_frame_exam[0], textvariable=self.field)
        # .grid(row=1, column=1)
        self.entry_field.pack(expand=True, fill=tb.X, padx=padx_in_frame, pady=pady_in_frame)
        # classe
        label_classe = tb.Label(left_frame_exam[1], text="Classe")
        label_classe.pack(expand=True, fill=tb.X, padx=padx_in_frame, pady=pady_in_frame)
        self.classe = tb.StringVar(value="Licence 3")
        self.entry_classe = tb.Entry(right_frame_exam[1], textvariable=self.classe)
        self.entry_classe.pack(expand=True, fill=tb.X, padx=padx_in_frame, pady=pady_in_frame)
        # exam name
        label_name_exam = tb.Label(left_frame_exam[2], text="Examen")
        label_name_exam.pack(expand=True, fill=tb.X, padx=padx_in_frame, pady=pady_in_frame)
        self.name_exam = tb.StringVar(value="CC1 Mécanique quantique")
        self.entry_name_exam = tb.Entry(right_frame_exam[2], textvariable=self.name_exam)
        self.entry_name_exam.pack(expand=True, fill=tb.X, padx=padx_in_frame, pady=pady_in_frame)
        # date
        label_date = tb.Label(left_frame_exam[3], text="Date")
        label_date.pack(expand=True, fill=tb.X, padx=padx_in_frame, pady=pady_in_frame)
        self.date = tb.StringVar(value="jour/mois/année")
        self.entry_date = tb.Entry(right_frame_exam[3], textvariable=self.date)
        self.entry_date.pack(expand=True, fill=tb.X, padx=padx_in_frame, pady=pady_in_frame)

        # frame for output
        label_output = tb.Label(self.window, text="Output", font=("Helvetica", 11))
        frame_output = tb.LabelFrame(self.window, labelwidget=label_output)
        # define left and right columns
        left_frame_output = [tb.Frame(frame_output)] * 2
        right_frame_output = [tb.Frame(frame_output)] * 2
        # output dir
        btn_outdir = tb.Button(
            left_frame_output[0],
            text="Sélectionner le dossier de sortie",
            command=self.__browse_dir,
        )
        btn_outdir.pack(expand=True, fill=tb.X, padx=padx_in_frame, pady=pady_in_frame)
        self.outdir = tb.StringVar(value="./output")
        self.entry_outdir = tb.Entry(right_frame_output[0], textvariable=self.outdir)
        self.entry_outdir.pack(expand=True, fill=tb.X, padx=padx_in_frame, pady=pady_in_frame)
        # suffix
        label_suffix = tb.Label(left_frame_output[1], text="Suffixe des fichiers de sortie")
        label_suffix.pack(expand=True, fill=tb.X, padx=padx_in_frame, pady=pady_in_frame)
        self.suffix = tb.StringVar(value="FeedbackForm")
        self.entry_suffix = tb.Entry(right_frame_output[1], textvariable=self.suffix)
        self.entry_suffix.pack(expand=True, fill=tb.X, padx=padx_in_frame, pady=pady_in_frame)

        # frame for submision button
        frame_submit = tb.Frame(self.window)
        btn_submit = tb.Button(
            frame_submit,
            text="Soumettre",
            command=lambda: self.window.destroy(),  # pylint:disable=unnecessary-lambda
            style="mySubmit.success.TButton",
        )
        btn_submit.pack(expand=True, fill=tb.X, padx=padx_in_frame, pady=pady_in_frame)

        # display frames !
        frame_input.pack(expand=True, fill=tb.X, padx=padx_frame, pady=pady_frame)
        for l_frame_in, r_frame_in in zip(left_frame_input, right_frame_input):
            l_frame_in.pack(expand=True, fill=tb.Y, padx=2, pady=2, side=tb.LEFT)
            r_frame_in.pack(expand=True, fill=tb.X, padx=2, pady=2, side=tb.RIGHT)
        frame_exam.pack(expand=True, fill=tb.X, padx=padx_frame, pady=pady_frame)
        for l_frame_exam, r_frame_exam in zip(left_frame_exam, right_frame_exam):
            l_frame_exam.pack(expand=True, fill=tb.Y, padx=2, pady=2, side=tb.LEFT)
            r_frame_exam.pack(expand=True, fill=tb.X, padx=2, pady=2, side=tb.RIGHT)
        frame_output.pack(expand=True, fill=tb.X, padx=padx_frame, pady=pady_frame)
        for l_frame_out, r_frame_out in zip(left_frame_output, right_frame_output):
            l_frame_out.pack(expand=True, fill=tb.Y, padx=2, pady=2, side=tb.LEFT)
            r_frame_out.pack(expand=True, fill=tb.X, padx=2, pady=2, side=tb.RIGHT)
        frame_submit.pack(expand=True, padx=padx_frame, pady=pady_frame)

        self.window.mainloop()

    def __browse_file(self) -> None:
        """
        Helper method to define an object allowing to browse directories
        and select Excel input file
        """
        filename = filedialog.askopenfilename(
            initialdir="~/",
            initialfile="example.xlsx",
            title="Sélectionner le fichier",
            filetypes=(("Excel files", "*.xlsx*"), ("all files", "*.*")),
        )
        self.entry_infile.insert(tk.END, filename.split("/")[-1])
        self.name_infile.set(filename)

    def __browse_dir(self) -> None:
        """
        Helper method to set output directory path
        """
        dirname = filedialog.askdirectory(title="Sélectionner le dossier")
        self.entry_outdir.insert(tk.END, dirname)
        self.outdir.set(dirname)


class DataHandler:
    """
    Class to handle data coming from both configuration file and input files
    """

    def __init__(self, common_config, name_cfg_file="", rm_log=True) -> None:
        """
        Init method
        """
        self.name_sheet_classe = common_config.get_name_sheet_classe()
        self.name_sheets = common_config.get_name_sheets()
        self.labels_default_columns = common_config.get_labels()

        self.config = {}
        if name_cfg_file:
            with open(name_cfg_file, "r", encoding="utf-8") as yml_config_file:
                self.config = yaml.load(yml_config_file, yaml.FullLoader)
        else:
            window = TkWindow()
            # retrieve configuration
            self.config["Input"] = {"name_file": window.name_infile.get()}
            self.config["Exam"] = {
                "field": window.field.get(),
                "classe": window.classe.get(),
                "name": window.name_exam.get(),
                "date": window.date.get(),
            }
            self.config["Output"] = {
                "dir": window.outdir.get(),
                "suffix": window.suffix.get(),
                "rm_log": rm_log,
            }

    # pylint: disable=possibly-used-before-assignment
    def get_df(self) -> dict[str, pd.DataFrame]:
        """
        Helper method to convert input (Excel sheets) to pandas dataframes
        while respecting the conventions
        """
        infile = pd.ExcelFile(self.config["Input"]["name_file"])
        # convert to dataframes
        df = {}
        for name_sheet in self.name_sheets:
            df[name_sheet] = pd.read_excel(infile, name_sheet, na_filter=False)
            # remove number, name and firstname columns from dataframes other than the "Classe" one
            if name_sheet != self.name_sheet_classe:
                df[name_sheet].drop(columns=self.labels_default_columns, inplace=True)

        return df

    def get_exam_config(self) -> dict[str, str]:
        """
        Helper method to get the configuration
        """
        return self.config["Exam"]

    def create_output_dir(self) -> None:
        """
        Helper method to create the output directory (if not already existing)
        """
        output_dir = enforce_trailing_slash(self.config["Output"]["dir"])
        self.config["Output"]["dir"] = output_dir

        if os.path.isdir(output_dir):
            log_output_dir = f"\033[93mWARNING: Output directory'{output_dir}'"
            log_output_dir += " already exists,"
            log_output_dir += " overwrites possibly ongoing!\033[0m"
            print(log_output_dir)
        else:
            os.makedirs(output_dir)

    def get_output_config(self) -> dict[str, str | bool]:
        """
        Helper method to get the configuration
        """
        return self.config["Output"]
