"""
Module to produce a template of Excel file based on a (default) configuration
"""

from effm.utils import Logger

try:
    import pandas as pd
except ModuleNotFoundError:
    Logger("'pandas' is not installed. Please install it to use this module.", "FATAL")

try:
    import yaml
except ModuleNotFoundError:
    Logger("'yaml' is not installed. Please install it to use this module.", "FATAL")

# pylint:disable=import-error
try:
    from xlsxwriter.utility import xl_rowcol_to_cell
except ModuleNotFoundError:
    Logger("'xlsxwriter' is not installed. Please install it to use this module.", "FATAL")


WIDTH_COL: int = 20
HEIGHT_CELL: int = 25

BLUE: str = "#373f6b"
GREEN: str = "d4edbc"
ORANGE: str = "#FFD580"
RED: str = "#E34234"
COLORS_LEVEL: list[str] = ["red", "orange", "green"]
COLORS_POINT: list[str] = ["red", "orange", "green"]


# pylint: disable= too-many-instance-attributes, too-few-public-methods
class ExcelTemplate:
    """
    Class to generate a template of Excel file configured via a YAML input file
    """

    def __init__(self, name_cfg_file: str) -> None:
        """
        Init method

        Parameters
        ------------------------------------------------
        - name_cfg_file: str
            Name of the input configuration file
        """

        # import configuration
        self.config: dict = {}
        with open(name_cfg_file, "r", encoding="utf-8") as yml_config_file:
            self.config = yaml.load(yml_config_file, yaml.FullLoader)

        self.n_students: int = self.config["Input"]["n_students"]
        if self.n_students is None:
            self.n_students = 1
        self.n_default_cols: int = len(self.config["Input"]["labels"])
        self.n_questions: int = len(self.config["GradingScheme"])
        # "+1" because a column is added in the code
        self.n_remarks: int = len(self.config["Remarks"]) + 1
        self.n_copy_comments: int = len(self.config["Copy"])
        self.n_skills: int = len(self.config["Skills"])
        self.levels: list[str] = self.config["Levels"]
        self.label_grade_col: str = self.config["LabelGradeColumn"]

        self.name_outfile: str = self.config["name_outfile"]
        self.name_sheets: dict = self.config["Sheets"]
        self.formats: dict = {}

    # pylint: disable = too-many-branches
    def __check_input_consistency(self) -> None:
        """
        Helper method to check self consistency of inputs
        """

        if not isinstance(self.config["Input"]["labels"], list):
            Logger("The 'labels' entry in 'Input' must be a list!", "FATAL")

        if not isinstance(self.n_students, int):
            Logger("The 'n_students' entry must ba a positive int if not null!", "FATAL")
        if self.n_students < 0:
            Logger("The 'n_students' entry must ba a positive int if not null!", "FATAL")

        if not isinstance(self.config["Input"]["import_from_file"]["name_cols"], list):
            Logger("The 'name_cols' entry in 'Input' must be a list!", "FATAL")

        if not isinstance(self.levels, list):
            Logger("The 'Levels' entry must be a list!", "FATAL")
        if len(self.levels) != len(COLORS_LEVEL):
            Logger("The 'Levels' entry must be a list of length 3!", "FATAL")

        for _, scheme in self.config["GradingScheme"].items():
            if not isinstance(scheme, list):
                Logger("The grading scheme for a given question must be a list!", "FATAL")

        for _, remark in self.config["Remarks"].items():
            if remark["default"] is not None:
                if not isinstance(remark["default"], bool):
                    Logger("The default value of a remark must be a boolean of null!", "FATAL")
            if remark["autofill"]["activate"]:
                if not isinstance(remark["autofill"]["questions"], list):
                    Logger("The 'questions' entry in 'Remarks: autofill' must be a list!", "FATAL")
                if remark["autofill"]["criteria"] not in ["<", "<=", ">", ">="]:
                    Logger(
                        "The 'criteria' entry in 'Remarks: autofill' must be chosen among:"
                        "<, <=, > or >=",
                        "FATAL",
                    )
                if not 0 <= remark["autofill"]["threshold"] <= 1:
                    Logger(
                        "The 'threshold' entry in 'Remarks: autofill' must be between 0 and 1!",
                        "FATAL",
                    )

        for _, comment in self.config["Copy"].items():
            if comment["default"] is not None:
                if comment["default"] not in self.levels:
                    Logger("The default value of a copy comment must be in 'Levels'!", "FATAL")

        for _, skill in self.config["Skills"].items():
            if skill["default"] is not None:
                if skill["default"] not in self.levels:
                    Logger("The default value of a skill must be in 'Levels'!", "FATAL")
            if skill["autofill"]["activate"]:
                if not isinstance(skill["autofill"]["questions"], list):
                    Logger("The 'questions' entry in 'Skills: autofill' must be a list!", "FATAL")
                if not isinstance(skill["autofill"]["thresholds"], list):
                    Logger("The 'thresholds' entry in 'Skills: autofill' must be a list!", "FATAL")
                if len(skill["autofill"]["thresholds"]) != len(self.levels) - 1:
                    Logger(
                        "The length of the 'thresholds' entry in 'Skills: autofill'"
                        "must be equal to the length of 'Levels' minus one!",
                        "FATAL",
                    )

    def __get_df_default(self) -> pd.DataFrame:
        """
        Helper method to convert input (Excel sheets) to pandas dataframes
        while respecting the conventions
        """

        cfg = self.config["Input"]

        # produce empty dataframe (with right column names)
        if not cfg["import_from_file"]["activate"]:
            labels = cfg["labels"]
            dico = {}
            for label in labels:
                dico[label] = []
            return pd.DataFrame(dico)

        # produce dataframe according to input file content
        infile = pd.ExcelFile(cfg["import_from_file"]["name_file"])
        df = pd.read_excel(
            io=infile,
            sheet_name=cfg["import_from_file"]["name_sheet"],
            usecols=cfg["import_from_file"]["name_cols"],
        )
        # update number of students
        self.n_students = len(df)
        # convert the column labels
        converter_label_col = {}
        for label_col_old, label_col_new in zip(
            cfg["import_from_file"]["name_cols"], cfg["labels"]
        ):
            converter_label_col[label_col_old] = label_col_new

        return df.rename(columns=converter_label_col)

    def generate_template(self) -> None:
        """
        Helper method to generate the output templated file
        """

        self.__check_input_consistency()

        df_default = self.__get_df_default()

        # start writing the xlsx file
        with pd.ExcelWriter(self.name_outfile, engine="xlsxwriter") as writer:
            # create the sheets with the default columns
            for _, name in self.name_sheets.items():
                df_default.to_excel(
                    writer,
                    sheet_name=name,
                    startrow=1,
                    startcol=0,
                    header=False,
                    index=False,
                )

            workbook = writer.book

            self.__set_formats(workbook)
            self.__write_header_columns(writer, df_default)
            self.__add_condition_for_absence(writer)
            self.__config_classe_sheet(writer)
            self.__config_grade_sheet(writer)
            self.__config_remark_sheet(writer)
            self.__config_copy_sheet(writer)
            self.__config_skill_sheet(writer)

    def __write_header_columns(self, writer, df: pd.DataFrame) -> None:
        """
        Helper method to write header columns

        Parameters
        ------------------------------------------------
        - writer: xlsxwriter
            Instance of xlsxwriter

        - df: pandas.DataFrame
            Dataframe corresponding to an Excel sheet
        """
        # write the column headers with the defined format
        for name, sheet in writer.sheets.items():
            sheet.set_column(0, self.n_default_cols - 1, WIDTH_COL, self.formats["default"])
            sheet.set_row(0, height=1.5 * HEIGHT_CELL)
            for icol, value in enumerate(df.columns.values):
                sheet.write(0, icol, value, self.formats["header"])
                for irow in range(self.n_students):
                    sheet.set_row(irow + 1, height=HEIGHT_CELL)
                    if self.config["Input"]["import_from_file"]["activate"]:
                        continue
                    if name not in self.name_sheets["Classe"]:
                        cell = xl_rowcol_to_cell(irow + 1, icol)
                        sheet.write_formula(
                            cell,
                            f"={self.name_sheets['Classe']}!{cell}",
                            cell_format=self.formats["default"],
                        )

    def __add_condition_for_absence(self, writer) -> None:
        """
        Helper method to add gray bands in Excel if student is absent

        Parameters
        ------------------------------------------------
        - writer: xlsxwriter
            Instance of xlsxwriter
        """
        # add condition on absent students
        for name, sheet in writer.sheets.items():
            for irow in range(self.n_students):
                cell_absence = xl_rowcol_to_cell(irow + 1, self.n_default_cols)
                n_max_col = self.n_default_cols
                if name in self.name_sheets["Grades"]:
                    n_max_col += self.n_questions + 1
                elif name in self.name_sheets["Remarks"]:
                    n_max_col += self.n_remarks
                elif name in self.name_sheets["Copy"]:
                    n_max_col += self.n_copy_comments
                elif name in self.name_sheets["Skills"]:
                    n_max_col += self.n_skills
                for icol in range(n_max_col):
                    cell = xl_rowcol_to_cell(irow + 1, icol)
                    condition = f"{self.name_sheets['Classe']}!{cell_absence}"
                    sheet.conditional_format(
                        cell,
                        {
                            "type": "formula",
                            "criteria": f"{condition}",
                            "format": self.formats["absent"],
                        },
                    )

    def __config_classe_sheet(self, writer) -> None:
        """
        Helper method to configure the classe sheet

        Parameters
        ------------------------------------------------
        - writer: xlsxwriter
            Instance of xlsxwriter
        """
        classe_sheet = self.__get_sheet(writer, "Classe")
        self.__add_column(classe_sheet, "Absence")
        # configure Absence column
        for irow in range(self.n_students):
            cell = xl_rowcol_to_cell(irow + 1, self.n_default_cols)
            classe_sheet.write_blank(cell, "", self.formats["default"])  # format cells
            classe_sheet.data_validation(cell, {"validate": "list", "source": [True, False]})

    def __config_grade_sheet(self, writer) -> None:
        """
        Helper method to configure the grade sheet

        Parameters
        ------------------------------------------------
        - writer: xlsxwriter
            Instance of xlsxwriter
        """
        grade_sheet = self.__get_sheet(writer, "Grades")
        self.__add_column(grade_sheet, self.label_grade_col, self.n_questions)
        grade_sheet.set_column(
            self.n_default_cols,
            self.n_default_cols + self.n_questions,
            WIDTH_COL,
            self.formats["default"],
        )
        # grade_max = 0  # TODO change convention and use this to show max grade in xlsx file
        for irow in range(self.n_students):
            for icol, (key, grading_scheme) in enumerate(self.config["GradingScheme"].items()):
                cell = xl_rowcol_to_cell(irow + 1, self.n_default_cols + icol)
                grade_sheet.write_number(cell, -1, self.formats["default"])  # format cells

                point_max = grading_scheme[-1]
                label_question = f"{key} (/{point_max})"
                self.__add_column(grade_sheet, label_question, icol)
                grade_sheet.data_validation(
                    cell,
                    {
                        "validate": "list",
                        "source": grading_scheme,
                        "input_title": "input",
                    },
                )

                # TODO make colors and thresholds configurable !
                thresholds = [0.33, 0.66]
                self.__point_formatting(grade_sheet, cell, point_max, thresholds)

            cell_first_question = xl_rowcol_to_cell(irow + 1, self.n_default_cols)
            cell_last_question = xl_rowcol_to_cell(
                irow + 1, self.n_default_cols + self.n_questions - 1
            )
            formula = "=IF(AND("
            cell_absence = xl_rowcol_to_cell(irow + 1, self.n_default_cols)
            formula += f"{self.name_sheets['Classe']}!{cell_absence}=FALSE(), "
            for icol in range(self.n_default_cols):
                formula += f"{xl_rowcol_to_cell(irow+1, self.n_default_cols+icol)}<>-1"
                if icol < self.n_default_cols - 1:
                    formula += ", "
            formula += "),"
            formula += f"SUM({cell_first_question}:{cell_last_question})"
            formula += ","
            formula += "NA()"
            formula += ")"
            grade_sheet.write_formula(
                irow + 1,
                self.n_default_cols + self.n_questions,
                formula,
                cell_format=self.formats["default"],
            )

    def __get_points_max(self) -> list[float]:
        """
        Helper method to get a list of max points for all questions
        """
        points_max = []
        for _, grading_scheme in self.config["GradingScheme"].items():
            points_max.append(grading_scheme[-1])
        return points_max

    # pylint: disable=too-many-locals
    def __config_remark_sheet(self, writer) -> None:
        """
        Helper method to configure the remark sheet

        Parameters
        ------------------------------------------------
        - writer: xlsxwriter
            Instance of xlsxwriter
        """
        remark_sheet = self.__get_sheet(writer, "Remarks")
        self.__add_column(remark_sheet, "Remarque personnalisée")
        remark_sheet.set_column(
            self.n_default_cols,
            self.n_default_cols + self.n_remarks - 1,
            WIDTH_COL,
            self.formats["default"],
        )
        # add columns for remarks
        points_max = self.__get_points_max()
        for irow in range(self.n_students):
            for icol, (_, remark) in enumerate(self.config["Remarks"].items()):
                icol += 1  # translation due to addition of the column "Remarque personnalisée"
                self.__add_column(remark_sheet, remark["label"], icol)
                # configure column
                cell = xl_rowcol_to_cell(irow + 1, self.n_default_cols + icol)
                remark_sheet.write_blank(cell, "", self.formats["default"])

                if remark["autofill"]["activate"]:
                    selected_cells = []
                    norm = 0
                    for label in remark["autofill"]["questions"]:
                        id_question = list(self.config["GradingScheme"]).index(label)
                        selected_cells.append(
                            xl_rowcol_to_cell(irow + 1, self.n_default_cols + id_question)
                        )
                        norm += points_max[id_question]
                    # get selected cells
                    str_selected_cells = ""
                    for i, selected_cell in enumerate(selected_cells):
                        str_selected_cells += f"{self.name_sheets['Grades']}!{selected_cell}"
                        if i + 1 < len(selected_cells):
                            str_selected_cells += ", "

                    # define formula for autofill
                    formula = "=IF("
                    formula += f"SUM({str_selected_cells})/{norm}"
                    formula += f"{remark['autofill']['criteria']}"
                    formula += f"{remark['autofill']['threshold']}"
                    formula += ","
                    formula += "TRUE"
                    formula += ","
                    formula += "FALSE"
                    formula += ")"
                    remark_sheet.write_formula(
                        cell,
                        formula,
                        value="autofill",
                        cell_format=self.formats["italic"],
                    )
                else:
                    remark_sheet.data_validation(
                        cell, {"validate": "list", "source": [True, False]}
                    )

                    if remark["default"] is not None:
                        remark_sheet.write(cell, remark["default"])

    def __config_copy_sheet(self, writer) -> None:
        """
        Helper method to configure the remark sheet

        Parameters
        ------------------------------------------------
        - writer: xlsxwriter
            Instance of xlsxwriter
        """
        copy_sheet = self.__get_sheet(writer, "Copy")
        copy_sheet.set_column(
            self.n_default_cols,
            self.n_default_cols + self.n_copy_comments - 1,
            WIDTH_COL,
            self.formats["default"],
        )

        for irow in range(self.n_students):
            for icol, (_, comment) in enumerate(self.config["Copy"].items()):
                self.__add_column(copy_sheet, comment["label"], icol)
                cell = xl_rowcol_to_cell(irow + 1, self.n_default_cols + icol)
                copy_sheet.write_blank(cell, "", self.formats["default"])
                copy_sheet.data_validation(cell, {"validate": "list", "source": self.levels})

                self.__level_formatting(copy_sheet, cell)

                if comment["default"] is not None:
                    copy_sheet.write(cell, comment["default"], self.formats["default"])

    def __config_skill_sheet(self, writer) -> None:
        """
        Helper method to configure the skill sheet

        Parameters
        ------------------------------------------------
        - writer: xlsxwriter
            Instance of xlsxwriter
        """
        skill_sheet = self.__get_sheet(writer, "Skills")
        skill_sheet.set_column(
            self.n_default_cols,
            self.n_default_cols + self.n_skills - 1,
            WIDTH_COL,
            self.formats["default"],
        )
        points_max = self.__get_points_max()
        for irow in range(self.n_students):
            for icol, (_, skill) in enumerate(self.config["Skills"].items()):
                self.__add_column(skill_sheet, skill["label"], icol)
                # configure column
                cell = xl_rowcol_to_cell(irow + 1, self.n_default_cols + icol)
                skill_sheet.write_blank(cell, "", self.formats["default"])

                self.__level_formatting(skill_sheet, cell)

                if skill["autofill"]["activate"]:
                    selected_cells = []
                    norm = 0
                    for label in skill["autofill"]["questions"]:
                        id_question = list(self.config["GradingScheme"]).index(label)
                        selected_cells.append(
                            xl_rowcol_to_cell(irow + 1, self.n_default_cols + id_question)
                        )
                        norm += points_max[id_question]
                    # get selected cells
                    str_selected_cells = ""
                    for i, selected_cell in enumerate(selected_cells):
                        str_selected_cells += f"{self.name_sheets['Grades']}!{selected_cell}"
                        if i + 1 < len(selected_cells):
                            str_selected_cells += ", "

                    formula = "=IF("
                    formula += f"SUM({str_selected_cells})/{norm}"
                    formula += "<"
                    formula += f"{skill['autofill']['thresholds'][1]}"
                    formula += ", "
                    formula += "IF("
                    formula += f"SUM({str_selected_cells})/{norm}"
                    formula += "<"
                    formula += f"{skill['autofill']['thresholds'][0]}"
                    formula += ","
                    formula += f'"{self.levels[0]}"'
                    formula += ","
                    formula += f'"{self.levels[1]}"'
                    formula += ")"
                    formula += ","
                    formula += f'"{self.levels[2]}"'
                    formula += ")"
                    skill_sheet.write_formula(
                        cell,
                        formula,
                        cell_format=self.formats["italic"],
                        value="autofill",
                    )
                else:
                    skill_sheet.data_validation(cell, {"validate": "list", "source": self.levels})

                    if skill["default"] is not None:
                        skill_sheet.write(cell, skill["default"], self.formats["default"])

    def __add_column(self, sheet, label_col: str, icol: int = 0) -> None:
        """
        Helper method to add a column to a sheet

        Parameters
        ------------------------------------------------
        - sheet: xlsxwriter.worksheet
            A worksheet instance

        - label_col: str
            Column label

        - icol: int
            Index of column (starting from the column after the default columns)
        """

        sheet.write(0, self.n_default_cols + icol, label_col, self.formats["header"])

    def __get_sheet(self, writer, label: str):
        """
        Helper method to get sheets

        Parameters
        ------------------------------------------------
        - writer: xlsxwriter
            Instance of xlsxwriter

        - label: str
            Label of the sheet
        """

        return writer.sheets[self.name_sheets[label]]

    def __level_formatting(self, sheet, cell: str) -> None:
        """
        Helper method to format a cell according to the level

        Parameters
        ------------------------------------------------
        - sheet: xlsxwriter.worksheet
            A worksheet instance

        - cell: str
            Cell of the sheet
        """
        for level, color in zip(self.levels, COLORS_LEVEL):
            sheet.conditional_format(
                cell,
                {
                    "type": "text",
                    "criteria": "containing",
                    "value": level,
                    "format": self.formats[f"{color}"],
                },
            )

    def __point_formatting(
        self, sheet, cell: str, point_max: float, thresholds: list[float]
    ) -> None:
        """
        Helper method to format a cell according to the level

        Parameters
        ------------------------------------------------
        - sheet: xlsxwriter.worksheet
            A worksheet instance

        - cell: str
            Cell of the sheet

        - point_max: float
            Maximum value of the points for this question

        - thresholds: list[float]
            Interval (in percentage of point_max) of the mid-level grade
        """
        thresholds = [0] + thresholds + [1]
        intervals = []
        for i, _ in enumerate(thresholds):
            if i == 0:
                continue
            intervals.append([thresholds[i - 1], thresholds[i]])

        for (min_rel, max_rel), color in zip(intervals, COLORS_POINT):
            sheet.conditional_format(
                cell,
                {
                    "type": "cell",
                    "criteria": "between",
                    "minimum": min_rel * point_max,
                    "maximum": max_rel * point_max,
                    "format": self.formats[f"{color}"],
                },
            )

        sheet.conditional_format(
            cell,
            {
                "type": "cell",
                "criteria": "<",
                "value": 0,
                "format": self.formats["white"],
            },
        )

    def __set_formats(self, workbook) -> None:
        """
        Helper method to get the formats

        Parameters
        ------------------------------------------------
        - workbook: xlsxwriter.Workbook
            The Excel workbook
        """
        default = {
            "font_name": "Lato Light",
            "valign": "vcenter",
            "align": "center",
            "text_wrap": True,
        }
        self.formats["default"] = workbook.add_format(default)
        self.formats["italic"] = workbook.add_format({"italic": True, **default})
        self.formats["white"] = workbook.add_format({"font_color": "white", **default})
        self.formats["absent"] = workbook.add_format(
            {
                "bg_color": "gray",
                "border_color": "black",
                "top": 1,
                "bottom": 1,
                "top_color": "black",
                "bottom_color": "black",
                **default,
            }
        )
        self.formats["red"] = workbook.add_format(
            {
                "font_color": "black",
                "bg_color": RED,
                "bottom": 1,
                "bottom_color": "white",
                "right": 1,
                "right_color": "white",
                **default,
            }
        )
        self.formats["orange"] = workbook.add_format(
            {
                "bg_color": ORANGE,
                "bottom": 1,
                "bottom_color": "white",
                "right": 1,
                "right_color": "white",
                **default,
            }
        )
        self.formats["green"] = workbook.add_format(
            {
                "bg_color": GREEN,
                "bottom": 1,
                "bottom_color": "white",
                "right": 1,
                "right_color": "white",
                **default,
            }
        )
        self.formats["header"] = workbook.add_format(
            {
                "bold": True,
                "text_wrap": True,
                "border": 1,
                "font_color": "white",
                "fg_color": BLUE,
                **default,
            }
        )
