"""
Tutorial script for feedback forms generation
"""

from effm.common_config import CommonConfig
from effm.data_handler import DataHandler
from effm.form import FormMaker


def make_forms(name_excel_cfg, name_form_cfg, compile_tex) -> None:
    """
    Function to produce feeback forms
    """
    common_config = CommonConfig(name_excel_cfg)
    data = DataHandler(common_config, name_form_cfg)
    forms = FormMaker(common_config, data, max_rank_shown=10)
    forms.make(compile_tex=compile_tex)


if __name__ == "__main__":
    # Import configuration for Excel template generation
    NAME_EXCEL_CFG: str = "config_excel_template.yml"

    # Configuration for Feedback forms generation
    USE_GUI: bool = False  # switch to use the GUI rather than the config file
    NAME_FORM_CFG: str = "config_form.yml" if not USE_GUI else str()
    COMPILE_TEX: bool = True  # switch to automatically compile .tex files via pdflatex
    # Call the function
    make_forms(NAME_EXCEL_CFG, NAME_FORM_CFG, COMPILE_TEX)
