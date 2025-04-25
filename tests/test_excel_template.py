"""
Test for effm.excel_template
"""

from effm.excel_template import ExcelTemplate


def main():
    """
    Main function
    """
    excel_template = ExcelTemplate("config_excel_template.yml")
    excel_template.generate_template()


if __name__ == "__main__":
    main()
