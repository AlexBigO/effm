"""
Module to produce forms for the exam
"""

import os

from effm.exam import Exam
from effm.latex import LaTeXOutput
from effm.student import Student
from effm.utils import get_name_columns


# pylint: disable=too-many-instance-attributes
class FormMaker:
    """
    Class to make feedback forms
    """

    def __init__(self, common_config, data, max_rank_shown=10):
        """
        Init method
        """
        self.exam = Exam(common_config, data.get_exam_config())
        self.df = data.get_df()
        # configure output
        data.create_output_dir()
        self.outdir, self.outfile_suffix, self.remove_log = data.get_output_config().values()

        # get names of default columns
        self.labels_default_cols = common_config.get_labels()
        self.labels_default_cols.append("Absence")  # add Absence column
        # get name of the column containing the total grade
        self.label_grade_col = common_config.get_label_grade_column()
        # get sheets names
        self.name_sheet_classe = common_config.get_name_sheet_classe()
        self.name_sheet_grades = common_config.get_name_sheet_grades()
        self.name_sheet_remarks = common_config.get_name_sheet_remarks()
        self.name_sheet_copy = common_config.get_name_sheet_copy()
        self.name_sheet_skills = common_config.get_name_sheet_skills()
        # get column names
        self.columns_sheet_remarks = get_name_columns(self.df[self.name_sheet_remarks])
        self.columns_sheet_copy = get_name_columns(self.df[self.name_sheet_copy])
        self.columns_sheet_skills = get_name_columns(self.df[self.name_sheet_skills])
        # get more detailed information on the grading scheme
        self.columns_grading_scheme = get_name_columns(
            self.df[self.name_sheet_grades].drop(columns=[self.label_grade_col])
        )

        self.grading_scheme = {}
        self.students = []
        self.classe_feedback_form = str()
        self.classe_feedback_form_w_absent = str()
        self.classe_feedback_form_anonymous = str()
        self.max_rank_shown = max_rank_shown

    def set_grading_scheme(self):
        """
        Helper method to set the grading scheme of the exam
        """
        for column in self.columns_grading_scheme:
            id_question = column.split("(")[0]
            if id_question[-1] == " ":
                id_question = id_question[:-1]  # remove blank if there is one
            marking = column.split("/")[1].split(")")[0]
            self.grading_scheme[id_question] = float(marking)
        self.exam.set_grading_scheme(self.grading_scheme)

    def set_students(self):
        """
        Helper method to set the students information
        """
        for _, row in self.df[self.name_sheet_classe].iterrows():
            rows = [row[label] for label in self.labels_default_cols]
            self.students.append(Student(*rows))
        # import the remaining pieces of information (grades, remarks, skills)
        for student, (_, row_grade), (_, row_remark), (_, row_copy), (_, row_skill) in zip(
            self.students,
            self.df[self.name_sheet_grades].iterrows(),
            self.df[self.name_sheet_remarks].iterrows(),
            self.df[self.name_sheet_copy].iterrows(),
            self.df[self.name_sheet_skills].iterrows(),
        ):

            student.set_grade(row_grade[self.label_grade_col])
            if not student.absent:
                student.set_rank(self.df[self.name_sheet_grades][self.label_grade_col])
            for column in self.columns_grading_scheme:
                id_question = column.split("(")[0]
                if id_question[-1] == " ":
                    id_question = id_question[:-1]  # remove blank if there is one
                student.set_schemed_grade(id_question, row_grade[column])
            for column in self.columns_sheet_remarks:
                student.set_remark(column, row_remark[column])
            for column in self.columns_sheet_copy:
                student.set_copy_remark(column, row_copy[column])
            for column in self.columns_sheet_skills:
                student.set_skill(column, row_skill[column])

        # update exam instance
        self.exam.set_students(self.students)
        self.exam.set_max_rank(self.df[self.name_sheet_grades][self.label_grade_col])

    def set_forms(self):
        """
        Helper method to set the feedback forms
        """
        for i, student in enumerate(self.students):
            # produce graphs
            if not student.absent:
                student.plot_grade_stats(self.exam, self.outdir)
            # first generate anonymous form for the whole class and save them in string variable
            anonymous_latex_output = LaTeXOutput(
                self.exam, student, self.outdir, self.max_rank_shown, anonymous=True
            )
            student.set_feedback_form(anonymous_latex_output.get_student_tex())
            if i == 0:
                self.classe_feedback_form_anonymous += anonymous_latex_output.get_preamble()
                self.classe_feedback_form_anonymous += "\n\\begin{document}\n\n"
            self.classe_feedback_form_anonymous += anonymous_latex_output.get_student_page()
            self.classe_feedback_form_anonymous += "\\newpage\n"
        # set the actual 'non-anonymous' forms
        for i, student in enumerate(self.students):
            latex_output = LaTeXOutput(self.exam, student, self.outdir, self.max_rank_shown)
            student.set_feedback_form(latex_output.get_student_tex())
            # for the whole classe now
            if not student.absent:
                if i == 0:
                    self.classe_feedback_form += latex_output.get_preamble()
                    self.classe_feedback_form += "\n\\begin{document}\n\n"
                self.classe_feedback_form += latex_output.get_student_page()
                self.classe_feedback_form += "\\newpage\n"

            if i == 0:
                self.classe_feedback_form_w_absent += latex_output.get_preamble()
                self.classe_feedback_form_w_absent += "\n\\begin{document}\n\n"

            self.classe_feedback_form_w_absent += latex_output.get_student_page()
            self.classe_feedback_form_w_absent += "\\newpage\n"

        self.classe_feedback_form += "\n\\end{document}"
        self.classe_feedback_form_w_absent += "\n\\end{document}"
        self.classe_feedback_form_anonymous += "\n\\end{document}"

    def add_average_student(self):
        """
        Helper method to add Alan SMITHEE
        """
        # feedback on the exam
        # (average of the whole classe as a fictitious student called Alan SMITHEE)
        # WARNING the number -1 must only be set for Alan SMITHEE !
        # set absent so it does not mess with quantities computation
        alan_smithee = Student(-1, "SMITHEE", "Alan", True)
        alan_smithee.set_grade(self.exam.get_mean())
        schemed_grades_classe = {}
        for i, (key, _) in enumerate(self.grading_scheme.items()):
            schemed_grades_classe[key] = self.exam.schemed_means[i]

        alan_smithee.schemed_grades = schemed_grades_classe
        alan_smithee.remarks = self.exam.remarks_classe
        alan_smithee.copy_remarks = self.exam.copy_remarks_classe
        alan_smithee.skills = self.exam.skills_classe
        alan_smithee.plot_grade_stats(self.exam, self.outdir)
        latex_output = LaTeXOutput(self.exam, alan_smithee, self.outdir, self.max_rank_shown)
        alan_smithee.set_feedback_form(latex_output.get_student_tex())

        self.students.append(alan_smithee)

    def write_output_files(self, compile_tex):
        """
        Helper method to write the output files

        Parameters
        ------------------------------------------------
        - compile_tex: bool
            A switch to activate autocompilation of LaTeX files
        """
        for student in self.students:
            name_out_file = f"{self.outdir}"
            # add a double 0 for Alan SMITHEE (makes the file easier to find)
            if student.number == -1:
                name_out_file += "00"
            name_out_file += f"{student.name}".replace(" ", "_")
            name_out_file += f"_{student.firstname}_{self.outfile_suffix}".replace(" ", "_")
            with open(f"{name_out_file}.tex", "w", encoding="utf-8") as file:
                file.write(student.feedback_form)
            if compile_tex:
                os.system(
                    f"pdflatex -halt-on-error -output-directory={self.outdir} {name_out_file}.tex"
                    f" > {self.outdir}log"
                )
                if self.remove_log:
                    os.system(f"rm {name_out_file}.aux {name_out_file}.log")
                    os.system(f"rm {self.outdir}log")

        # for the whole classe (for present students)
        name_out_file = f"{self.outdir}00{self.exam.classe}".replace(" ", "_")
        name_out_file += f"_{self.exam.name}_{self.outfile_suffix}".replace(" ", "_")
        # forms without absent students
        with open(f"{name_out_file}_WoAbsent.tex", "w", encoding="utf-8") as file:
            file.write(self.classe_feedback_form)
        if compile_tex:
            os.system(
                f"pdflatex -halt-on-error -output-directory={self.outdir} {name_out_file}"
                f"_WoAbsent.tex > {self.outdir}log"
            )
            if self.remove_log:
                os.system(f"rm {name_out_file}_WoAbsent.aux {name_out_file}_WoAbsent.log")
                os.system(f"rm {self.outdir}log")
        # all forms
        with open(f"{name_out_file}_All.tex", "w", encoding="utf-8") as file:
            file.write(self.classe_feedback_form_w_absent)
        if compile_tex:
            os.system(
                f"pdflatex -halt-on-error -output-directory={self.outdir} {name_out_file}_All.tex"
                f" > {self.outdir}log"
            )
            if self.remove_log:
                os.system(f"rm {name_out_file}_All.aux {name_out_file}_All.log")
                os.system(f"rm {self.outdir}log")
        # anonymous forms
        with open(f"{name_out_file}_Anonymous.tex", "w", encoding="utf-8") as file:
            file.write(self.classe_feedback_form_anonymous)
        if compile_tex:
            os.system(
                f"pdflatex -halt-on-error -output-directory={self.outdir} {name_out_file}"
                "_Anonymous.tex"
                f" > {self.outdir}log"
            )
            if self.remove_log:
                os.system(f"rm {name_out_file}_Anonymous.aux {name_out_file}_Anonymous.log")
                os.system(f"rm {self.outdir}log")

    def make(self, compile_tex=False):
        """
        Method to produce the feedback forms

        Parameters
        ------------------------------------------------
        - compile_tex: bool
            A switch to activate autocompilation of LaTeX files
        """
        self.set_grading_scheme()
        self.set_students()
        self.set_forms()
        self.add_average_student()
        self.write_output_files(compile_tex)
