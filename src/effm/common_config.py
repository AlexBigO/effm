"""
Simple module to handle configurations
"""

try:
    import yaml
except ModuleNotFoundError:
    print("'yaml' is not installed. Please install it to use this module.")


class CommonConfig:
    """
    Class to handle configuration common to Excel file production
    and feedback form makers
    """

    def __init__(self, name_excel_cfg) -> None:
        """
        Init method
        """
        self.config: dict = {}
        with open(name_excel_cfg, "r", encoding="utf-8") as yml_config_file:
            self.config = yaml.load(yml_config_file, yaml.FullLoader)

        self.labels: list[str] = self.config["Input"]["labels"]
        self.name_sheets: list[str] = list(self.config["Sheets"].values())
        self.levels: list[str] = self.config["Levels"]
        self.label_grade_col: str = self.config["LabelGradeColumn"]

    def get_name_sheets(self) -> list[str]:
        """
        Helper method to get the names of Excel file sheets
        """
        return self.name_sheets

    def get_name_sheet_classe(self) -> str:
        """
        Helper method to get the name of the 'Classe' Excel file sheet
        """
        return self.config["Sheets"]["Classe"]

    def get_name_sheet_grades(self) -> str:
        """
        Helper method to get the name of the 'Grades' Excel file sheet
        """
        return self.config["Sheets"]["Grades"]

    def get_name_sheet_remarks(self) -> str:
        """
        Helper method to get the name of the 'Remarks' Excel file sheet
        """
        return self.config["Sheets"]["Remarks"]

    def get_name_sheet_copy(self) -> str:
        """
        Helper method to get the name of the 'Copy' Excel file sheet
        """
        return self.config["Sheets"]["Copy"]

    def get_name_sheet_skills(self) -> str:
        """
        Helper method to get the name of the 'Skills' Excel file sheet
        """
        return self.config["Sheets"]["Skills"]

    def get_labels(self) -> list[str]:
        """
        Helper method to get labels of common columns in Excel file
        """
        return self.labels

    def get_levels(self) -> list[str]:
        """
        Helper method to get levels
        """
        return self.levels

    def get_label_grade_column(self) -> str:
        """
        Helper method to get the label of the grade column
        """
        return self.label_grade_col
