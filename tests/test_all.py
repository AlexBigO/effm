"""
Test of the whole library
"""

from effm.common_config import CommonConfig
from effm.data_handler import DataHandler
from effm.excel_template import ExcelTemplate
from effm.form import FormMaker


def make_excel_template(name_excel_cfg) -> None:
    """
    Function to produce Excel template
    """
    excel_template = ExcelTemplate(name_excel_cfg)
    excel_template.generate_template()


def make_forms(name_excel_cfg, name_form_cfg, compile_tex) -> None:
    """
    Function to produce feeback forms
    """
    common_config = CommonConfig(name_excel_cfg)
    data = DataHandler(common_config, name_form_cfg)
    forms = FormMaker(common_config, data)
    forms.make(compile_tex=compile_tex)


if __name__ == "__main__":
    NAME_EXCEL_CFG: str = "config_excel_template.yml"

    USE_GUI: bool = False
    NAME_FORM_CFG: str = "config_form.yml" if not USE_GUI else str()
    COMPILE_TEX: bool = True
    make_forms(NAME_EXCEL_CFG, NAME_FORM_CFG, COMPILE_TEX)
