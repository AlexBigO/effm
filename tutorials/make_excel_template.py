"""
Tutorial script for Excel template generation
"""

from effm.excel_template import ExcelTemplate


def make_excel_template(name_excel_cfg) -> None:
    """
    Function to produce Excel template
    """
    excel_template = ExcelTemplate(name_excel_cfg)
    excel_template.generate_template()


if __name__ == "__main__":
    NAME_EXCEL_CFG: str = "config_excel_template.yml"
    make_excel_template(NAME_EXCEL_CFG)
