"""
Module containing the class used to define student properties
"""

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


# pylint:disable=too-many-instance-attributes
class Student:
    """
    Class for student
    """

    def __init__(self, number, name, firstname, absent):
        """
        Init method
        """
        self.number = number
        self.name = name
        self.firstname = firstname
        self.absent = bool(absent)

        self.grade = None
        self.rank = None
        self.ex_aequo = False
        self.remarks = []
        self.copy_remarks = []
        self.schemed_grades = {}
        self.skills = []

        self.feedback_form = ""

    def set_grade(self, grade):
        """
        Helper method to add grade
        """
        self.grade = grade

    def set_schemed_grade(self, key, schemed_grade):
        """
        Helper method to add a schemed grade
        """
        self.schemed_grades[key] = schemed_grade

    def set_remark(self, key, remark):
        """
        Helper method to add a general remark
        """
        # so we do not include the NaN cells that got deleted of df by na_filter=False
        if remark != "":
            self.remarks.append([key, remark])

    def set_copy_remark(self, key, remark):
        """
        Helper method to add a remark about the copy
        """
        self.copy_remarks.append([key, remark])

    def set_skill(self, key, skill):
        """
        Helper method to add a skill
        """
        self.skills.append([key, skill])

    # pylint:disable=too-many-locals
    def plot_grade_stats(self, exam, outdir):
        """
        Helper method to plot grade stats
        """
        width = 11.7  # adapt to a4paper
        figsize = (width, 0.5 * width)
        dpi = 100
        mpl.rc("lines", linewidth=2.5, markersize=18)
        mpl.rc("text", usetex=True)
        mpl.rc("font", family="Computer Modern", size=15)

        fig, ax = plt.subplots(figsize=figsize, dpi=dpi, tight_layout=True)
        ax.grid(True)

        # configure x axis
        x = [i for i, _ in enumerate(self.schemed_grades.items())]
        ax.set_xticks(x)
        ax.set_xticklabels([key for key, _ in self.schemed_grades.items()])
        xmin = float(x[0]) - 0.5
        xmax = float(x[-1]) + 0.5
        ax.set_xlim(xmin, xmax)
        ax.set_xlabel(r"Questions", fontsize=18)
        # configure y axis
        ymin = -0.25
        ymax = max(list(exam.grading_scheme.values())) + 0.45
        ax.set_ylim(ymin, ymax)
        ax.set_ylabel(r"Nombre de points", fontsize=18)

        # plot marking scheme
        exam_grading_scheme_values = list(exam.grading_scheme.values())
        for i, (abscissa, value) in enumerate(zip(x, exam_grading_scheme_values)):
            binning = np.linspace(abscissa - 0.45, abscissa + 0.45, 10)
            values = [value] * len(binning)
            label = None
            if i == 0:
                label = "Barème"
            ax.plot(
                binning,
                values,
                color="dimgray",
                linestyle="dashed",
                linewidth=3,
                label=label,
                zorder=4,
            )

        # plot schemed grades for the student
        ax.scatter(
            x, list(self.schemed_grades.values()), marker="*", color="red", label="Note", zorder=15
        )

        # plot the schemed mean (of the whole classe)
        ax.scatter(
            x,
            exam.schemed_means,
            facecolors="none",
            edgecolors="blue",
            linewidth=1.5,
            label="Moyenne de la classe",
            zorder=10,
        )
        # plot the schemed standard deviation (of the whole classe)
        ax.errorbar(
            x,
            exam.schemed_means,
            # exam.schemed_std_devs,
            yerr=[exam.schemed_err_mins, exam.schemed_err_maxs],
            fmt="none",
            color="purple",
            fillstyle="none",
            capsize=10,
            capthick=2,
            label="Écart-type de la classe",
            zorder=5,
        )
        # legend
        ax.legend(loc="upper center", ncol=4, fontsize=15, bbox_to_anchor=(0.5, 1.01))
        # save figure
        name_file = outdir + self.name + "_" + self.firstname + "_GradeStats" + ".pdf"
        fig.savefig(name_file)
        plt.close()

    def set_rank(self, grades_classe):
        """
        Helper method to get the rank of the student
        """
        # remove duplicates
        # print("Grades for rank:")
        # print(list(set(grades_classe)))
        # print("\n")
        grades_classe_wo_dupli = pd.Series(list(set(grades_classe))).dropna().values
        # sort this list
        sorted_grades_classe_wo_dupli = sorted(grades_classe_wo_dupli, reverse=True)
        # get the position of the student's grade in this list
        rank = 1 + sorted_grades_classe_wo_dupli.index(self.grade)
        self.rank = int(rank)
        # know if there is an ex aequo
        self.ex_aequo = (
            len([i + 1 for i, grade in enumerate(grades_classe) if grade == self.grade]) > 1
        )

    def set_feedback_form(self, feedback_form):
        """
        Helper method ...
        """
        self.feedback_form = feedback_form
