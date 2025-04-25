"""
Module containing the class used to define LaTeX output
"""


# pylint: disable=too-many-instance-attributes, too-few-public-methods
class LaTeXOutput:
    """
    Class to format the LaTeX output to be compiled with pdflatex
    """

    def __init__(self, exam, student, outdir, max_rank_shown) -> None:
        """
        Init method
        """

        self.exam = exam
        self.student = student
        self.outdir: str = outdir

        self.header: str = str()
        self.grade_details: str = str()
        self.remarks: str = str()
        self.copy_remarks: str = str()
        self.skills: str = str()

        self.max_rank_shown: int = max_rank_shown

    def get_preamble(self) -> str:
        """
        Helper method to set preamble

        Returns
        ------------------------------------------------
        - preamble: str
            The preamble of the .tex file
        """
        preamble = "\\documentclass[12pt, a4paper]{article}\n"
        preamble += (
            "\\usepackage{graphicx, xcolor, amsmath, amssymb, fontawesome, xspace, braket}\n"
        )
        preamble += (
            "\\usepackage[a4paper, left=1.5cm, right=1.5cm, top=1.5cm, bottom=1.5cm]{geometry}\n"
        )
        preamble += "\\definecolor{DarkRed}{rgb}{0.76, 0.23, 0.13}\n"
        preamble += "\\definecolor{DarkGreen}{rgb}{0.01, 0.75, 0.24}\n"
        preamble += "\\definecolor{DarkBlue}{rgb}{0.47, 0.62, 0.8}\n"
        preamble += "\\definecolor{DarkOrange}{rgb}{1.0, 0.55, 0.0}\n"
        return preamble

    def str_grade(self):
        """
        Helper method to show the grade with the at most two numbers after the comma

        Returns
        ------------------------------------------------
        - _str_grade: str
            The grade in string format
        """
        _str_grade = f"{self.student.grade:.2f}"
        if _str_grade[-1] == "0":
            if _str_grade[-2] == "0":
                return _str_grade[:-3]
            return _str_grade[:-1]
        return _str_grade

    def __header(self):
        """
        Helper method to set header

        Returns
        ------------------------------------------------
        - header: str
            The header of the .tex document environment
        """
        all_points = self.exam.get_total_number_of_points()
        header = (
            f"\\noindent\\begin{{minipage}}[c]{{0.31\\linewidth}}\\noindent {self.student.name}"
        )
        header += "\\end{minipage}\\hfill\n"
        header += f"\\begin{{minipage}}[c]{{0.31\\linewidth}}\\centering {self.exam.date}"
        header += " \\end{minipage}\\hfill\n"
        header += f"\\begin{{minipage}}[c]{{0.31\\linewidth}}\\hfill {self.exam.classe}"
        header += " \\end{minipage}\\hfill\n"
        header += "\n"
        header += "\\noindent\\begin{minipage}[c]{0.31\\linewidth}"
        header += f"\\noindent {self.student.firstname}"
        header += "\\end{minipage}\\hfill\n"
        header += "\\begin{minipage}[c]{0.31\\linewidth}\\hfill"
        header += f"({self.exam.n_present_students} étudiants)"
        header += "\\end{minipage}\n"
        header += f"\\begin{{center}} {self.exam.field} -- {self.exam.name}\\bigskip\n\n"
        if self.student.absent and self.student.number != -1:
            header += "{\\Large\\bf ABSENT}\\end{center}"
        else:
            header += f"{{\\Large\\bf \\fbox{{Note: {self.str_grade()}/{all_points:.0f}}}}}"
            header += "\\end{center}\n\n"
            header += "\\vspace*{-0.7cm}"
            if self.student.number != -1:
                if self.student.rank < self.max_rank_shown:
                    header += f"\\noindent Classement: {self.student.rank}"
                    if self.student.ex_aequo:
                        header += " \\textit{ex aequo}"
                    # header += f" / {self.exam.max_rank}"
            header += "\\hfill Classe:  $\\left("
            header += f"{self.exam.get_mean():.1f} \\pm {self.exam.get_std_dev():.1f}\\right)$"
            header += f"/{all_points:.0f}\n"

        return header

    def __grade_details(self):
        """
        Helper method to set grade details

        Returns
        ------------------------------------------------
        - grade_details: str
            The details on the student grade
        """
        name_plot_file = (
            self.outdir + self.student.name + "_" + self.student.firstname + "_GradeStats" + ".pdf"
        )
        grade_details = "\\noindent\\rule{\\linewidth}{.7pt}\\begin{center}"
        grade_details += "{\\large\\bf Détail de la note}\\end{center}"
        grade_details += "\n\n"
        grade_details += "\\begin{center}\n"
        grade_details += (
            f"\\includegraphics[keepaspectratio, width=\\linewidth]{{{name_plot_file}}}"
        )
        grade_details += "\\end{center}\n\n"

        return grade_details

    def __to_smiley(self, evaluation):
        """
        Helper method to convert evaluations into smileys
        """
        if evaluation in ["Dépasse les exigences"]:
            return "\\xspace\\color{DarkBlue}\\faRocket\\color{black}"
        if evaluation in ["Bien", "Acquis"]:
            return "\\xspace\\color{DarkGreen}\\faSmileO\\color{black}"
        if evaluation in ["En voie d'acquisition", "Moyen"]:
            return "\\xspace\\color{DarkOrange}\\faMehO\\color{black}"
        return "\\xspace\\color{DarkRed}\\faFrownO\\color{black}"

    def __remarks(self):
        """
        Helper method to set general remarks

        Returns
        ------------------------------------------------
        - remarks: str
            The general remarks about the student's exam
        """
        remarks = "\\noindent\\rule{\\linewidth}{.7pt}"
        remarks += "\\begin{center}{\\large\\bf Remarques générales}\\end{center}"
        remarks += "\n\n"
        for key, remark in self.student.remarks:
            # the 'in [0,1]' is a safety due to possible Excel formatting issues
            if isinstance(remark, bool) or remark in [0, 1]:
                if remark:
                    remarks += f"$\\triangleright$\\xspace {key}\n\n"
                else:
                    continue
            else:
                remarks += f"$\\triangleright$\\xspace {remark}\n\n"
        return remarks

    def __copy_remarks(self):
        """
        Helper method to set remarks about the copy

        Returns
        ------------------------------------------------
        - remarks: str
            The remarks about the student's copy
        """
        remarks = "\\noindent\\rule{\\linewidth}{.7pt}\\begin{center}"
        remarks += "{\\large\\bf Remarques sur la copie}\\end{center}"
        remarks += "\n\n"
        remarks += "\\begin{center}\n"
        for i, (key, remark) in enumerate(self.student.copy_remarks):
            if i == 0:
                remarks += "\\noindent "
            remarks += f"\\mbox{{{key}\\xspace{self.__to_smiley(remark)}}}\\hfill "
        remarks += "\n\\end{center}\n\n"
        return remarks

    def __skills(self):
        """
        Helper method to set skills

        Returns
        ------------------------------------------------
        - text: str
            The student's skills regarding the exam
        """
        skills = self.student.skills
        text = "\\noindent\\rule{\\linewidth}{.7pt}\\begin{center}"
        text += "{\\large\\bf Compétences exigibles}\\end{center}"
        text += "\n\n"
        nskills = len(skills)
        ncols = nskills
        if 4 <= nskills <= 6:
            ncols = 3
        elif 7 <= nskills <= 9:
            ncols = 3
        width = 1 / ncols - 0.1  # f"{1/ncols:.1f}"

        for i, (skill, evaluation) in enumerate(skills):
            # text += f"{i} \n"
            text += f"\\begin{{minipage}}[c]{{{width}\\linewidth}}\\centering\n"
            text += f"{skill}\\xspace{self.__to_smiley(evaluation)}\n"
            text += "\\end{minipage}"
            if i != 0 and (i + 1) % ncols == 0:
                text += "\\bigskip\n\n" if (i + 1) != nskills else "\n"
            else:
                text += "\\hfill\n" if (i + 1) != nskills else "\n"

        return text

    def get_student_page(self):
        """
        Helper method to get the tex page (w/o preamble nor \\end{document}) for a given student

        Returns
        ------------------------------------------------
        - tex: str
            The tex page (w/o preamble nor \\end{document}) for a given student
        """
        tex = "\\pagestyle{empty}\n"
        tex += self.__header()
        if self.student.absent and self.student.number != -1:
            return tex

        tex += self.__grade_details()
        tex += "\n"
        tex += self.__remarks()
        tex += "\n"
        tex += self.__copy_remarks()
        tex += "\n"
        tex += self.__skills()

        return tex

    def get_student_tex(self):
        """
        Helper method to get the output tex file content for a given student

        Returns
        ------------------------------------------------
        - tex: str
            The whole .tex file content
        """
        tex = self.get_preamble()
        tex += "\n\\begin{document}\n\n"
        tex += self.get_student_page()
        tex += "\n\\end{document}"

        return tex

    def get_exam_tex(self):
        """
        Helper method to get the output tex file content for the exam

        Returns
        ------------------------------------------------
        - tex: str
            The whole .tex file content
        """
        tex = self.get_preamble()
        tex += "\n\\begin{document}\n\n"
        tex += self.get_student_page()
        tex += "\n\\end{document}"

        return tex
