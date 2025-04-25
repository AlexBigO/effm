"""
Module containing the class used to define exam properties
"""

import numpy as np


# pylint:disable=too-many-instance-attributes
class Exam:
    """
    Class for the exam
    """

    def __init__(self, common_config, cfg) -> None:
        """
        Init method
        """
        self.field: str = cfg["field"]
        self.classe: str = cfg["classe"]
        self.date: str = cfg["date"]
        self.name: str = cfg["name"]

        self.levels: list[str] = common_config.get_levels()

        self.grading_scheme: dict = {}
        self.students: list = []
        self.n_present_students: int = 0
        self.max_rank: int = 0
        self.schemed_means: list = []
        self.schemed_std_devs: list = []
        self.schemed_err_mins: list = []
        self.schemed_err_maxs: list = []

        # information needed for Alan Smithee, a "mean" student :)
        self.remarks_classe: list = []
        self.copy_remarks_classe: list = []
        self.skills_classe: list = []

    def set_grading_scheme(self, grading_scheme: dict) -> None:
        """
        Helper method to set marking scheme of the exam

        Parameters
        ------------------------------------------------
        - grading_scheme: dict
            The marking scheme of the exam
        """
        self.grading_scheme = grading_scheme

    def __set_schemed_means_and_std_devs(self) -> None:
        """
        Helper method to set the schemed mean and standard deviation of the exam for each question
        """
        schemed_grades = []
        for key in self.grading_scheme.keys():
            schemed_grades.append(
                [student.schemed_grades[key] for student in self.students if not student.absent]
            )
        self.schemed_means = [np.mean(schemed_grade) for schemed_grade in schemed_grades]
        self.schemed_std_devs = [np.std(schemed_grade) for schemed_grade in schemed_grades]
        # get asymmetric errors
        for mean, std_dev, (key, scheme) in zip(
            self.schemed_means, self.schemed_std_devs, self.grading_scheme.items()
        ):
            err_min = std_dev if mean - std_dev >= 0 else mean
            err_max = std_dev if mean + std_dev <= scheme else scheme - mean
            self.schemed_err_mins.append(err_min)
            self.schemed_err_maxs.append(err_max)

    def __set_remarks_classe(self) -> None:
        """
        Helper method to retrieve the main remarks given to the students
        """
        remarks_classe = []
        break_loop = False
        for student in self.students:
            if break_loop:
                break
            for remark, switch in student.remarks:
                # store the label of boolean remarks only once
                # (as it is the same for all other students)
                if (isinstance(switch, bool) or switch in [0, 1]) and remark not in [
                    "Poursuivez vos efforts !"
                ]:
                    remarks_classe.append([remark, True])
                    break_loop = True
        self.remarks_classe = remarks_classe

    def __to_number(self, evaluation: str) -> int:
        """
        Helper method to convert skill evaluation in a number

        Parameters
        ------------------------------------------------
        - evaluation: str
            Evaluation level among
            "Dépasse les exigences", "Bien", "Acquis", "En voie d'acquisition", "Moyen", else

        Returns
        ------------------------------------------------
        - _: int
            The evaluation on a scale from 0 to 2 (to be later converted in smileys :D)
        """
        # return self.levels.index(evaluation)
        if evaluation in ["Dépasse les exigences"]:
            return 3
        if evaluation in ["Bien", "Acquis"]:
            return 2
        if evaluation in ["En voie d'acquisition", "Moyen"]:
            return 1
        return 0

    def __to_skill_evaluation(self, number: float) -> str:
        """
        Helper method to convert skill evaluation from number to string

        Parameters
        ------------------------------------------------
        - number: float
            Evaluation "grade" for a given skill

        Returns
        ------------------------------------------------
        - _: str
            The evaluation in string format (to be later converted in smileys :D)
        """
        if 2.5 < number <= 3:
            return "Dépasse les exigences"
        if 1.5 < number <= 2.5:
            return "Acquis"
        if 0.5 < number <= 1.5:
            return "En voie d'acquisition"
        return "Non acquis"

    def __to_copy_evaluation(self, number: float) -> str:
        """
        Helper method to convert copy evaluation in a number

        Parameters
        ------------------------------------------------
        - number: float
            Evaluation "grade" for a given aspect of the copy

        Returns
        ------------------------------------------------
        - _: str
            The evaluation in string format (to be later converted in smileys :D)
        """
        if 1.5 < number <= 2:
            return "Bien"
        if 0.5 < number <= 1.5:
            return "Moyen"
        return "Faible"

    def __set_copy_remarks_classe(self) -> None:
        """
        Helper method to retrieve the rounded mean of the copy remarks of the classe
        """
        copy_remarks = []
        present_students = [student for student in self.students if not student.absent]
        for istudent, student in enumerate(present_students):
            for iremark, (remark, evaluation) in enumerate(student.copy_remarks):
                if istudent == 0:
                    # shape the list of copy_remarks
                    copy_remarks.append([remark, self.__to_number(evaluation)])
                else:
                    copy_remarks[iremark][1] += self.__to_number(evaluation)
        for iremark, (_, number) in enumerate(copy_remarks):
            mean_number = float(number / self.n_present_students)
            mean_evaluation = self.__to_copy_evaluation(mean_number)
            copy_remarks[iremark][1] = mean_evaluation
        self.copy_remarks_classe = copy_remarks

    def __set_skills_classe(self) -> None:
        """
        Helper method to retrieve the rounded mean of the skills of the classe
        """
        skills = []
        present_students = [student for student in self.students if not student.absent]
        for istudent, student in enumerate(present_students):
            for iskill, (skill, evaluation) in enumerate(student.skills):
                if istudent == 0:
                    # shape the list of skills
                    skills.append([skill, self.__to_number(evaluation)])
                else:
                    skills[iskill][1] += self.__to_number(evaluation)
        for iskill, (_, number) in enumerate(skills):
            mean_number = float(number / self.n_present_students)
            mean_evaluation = self.__to_skill_evaluation(mean_number)
            skills[iskill][1] = mean_evaluation
        self.skills_classe = skills

    def set_students(self, students: list) -> None:
        """
        Helper method to set the students for this exam

        Parameters
        ------------------------------------------------
        - students: list(Student)
            List of all the students
        """
        self.students = students
        self.n_present_students = len([student for student in students if not student.absent])
        self.__set_schemed_means_and_std_devs()
        self.__set_remarks_classe()
        self.__set_copy_remarks_classe()
        self.__set_skills_classe()

    def get_mean(self):
        """
        Helper method to get the mean of the exam grade

        Returns
        ------------------------------------------------
        - _: float
            Mean of the exam grade
        """
        return np.mean([student.grade for student in self.students if not student.absent])

    def get_std_dev(self):
        """
        Helper method to get the standard deviation of the exam grade

        Returns
        ------------------------------------------------
        - _: float
            Standard deviation of the exam grade
        """
        return np.std([student.grade for student in self.students if not student.absent])

    def get_total_number_of_points(self):
        """
        Helper method to get the total number of possible points in the exam

        Returns
        ------------------------------------------------
        - _: float
            Total number of possible points in the exam
        """
        return np.sum(list(self.grading_scheme.values()))

    def set_max_rank(self, grades_classe) -> None:
        """
        Helper method to set the maximum rank
        (different from the number of students in case of ex aequo)
        """
        self.max_rank = len(list(set(grades_classe)))
