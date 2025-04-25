<img src="./effm_logo.pdf" width="200" />

# Introduction

Exam Feedback Form Maker (effm) to create feedback forms for students after an exam.

# Installation

## Download this folder

You can use `git clone` command as follows:

```
git clone --branch main <repo>
```

## Create a virtual environment

One can use a `conda` environment:
- create a new environement:
```
conda env create -f environment.yml
```
- update an existing environment:
```
conda env update --name effm_env --file environment.yml --prune
```

## Install the package
To do so, use the `compile.sh` script.

# How to use

This package is there to facilitate and automatise the production of feedback forms for students after an exam. It provides two main functionalities:
- produce a templated Excel file to be filled with grades and some remarks;
- use this filled Excel file to produce individual feedback forms for every students in a given group

Each step relies on the use of `yaml` configuration files (i.e. `.yml` files).

## Produce a templated Excel file

One should follow the script `tutorials/make_excel_template.py` using `yaml` configuration file with the same structure as `tutorials/config_excel_template.yml`.

### Script

There is basically nothing to change to the script other than the name of the configuration file.

### Configuration file

Use the file `tutorials/config_excel_template.yml` as a starting point and build your own configuration from it (e.g. modify grading scheme, add remarks, comments on the copy, skills).

All the elements are documented inside this example file, but we draw the main elements/advantages of this part of the package in what follows:
- `Input`: one can define a (almost) blank templated Excel file without importing directly the students information OR one can also draw students information (number, last name, firstname) from another Excel file and directly copy it in our new templated Excel file
- `name_out_file`: the name of the templated Excel file that will be produced
- `Sheets`: the package works with a convention of 5 sheets:
    - a sheet for the `Classe`: information on the students
    - a sheet for the `Grades`: grading scheme and total grade
    - a sheet for the `Remarks
    - a sheet for the comments on the `Copy`
    - a sheet for the `Skills`
- `GradingScheme`: this is where one shall define the questions labels and what is the grading scheme for each question. The package does the rest of the job
- `Remarks`:
    - this is where one can define 'common' remarks (i.e. remarks that the teacher expectes to give to a non-negligible number of students a priori to the exam evaluation).
    - these remarks can be filled automatically according to the percentage of achievement on a question or a group of questions.
    *Example: if questions 1.1 and 1.2 address a specific notion, one can activate the `autofill` for `questions: [1.1, 1.2]` with `criteria: <` and `threshold: 0.5`. This means that if a student has less than 50% of the points allocated to questions 1.1 and 1.2, this student will receive this specific remark.*
- `Copy`: these are comments on the copy (cannot be autofilled)
- `Skills`:
    - this is where one can define the skills evaluation in this exam.
    - these skills can be filled automatically according to the percentage of achievement on a question or a group of questions.
    *Example: if questions 1.1 and 1.2 address a specific skill, one can activate the `autofill` for `questions: [1.1, 1.2]` with `thresholds: [0.4, 0.8]`. This means that if a student has less than 40% (resp. more than 80%) of the points allocated to questions 1.1 and 1.2, this student will receive the lowest level (resp. highest level) on this skill. If it is between 40% and 80%, the student will receive the intermediate level on this skill.*

**Important remark: the text entries in the Excel file can be written in LaTeX format (e.g. equations or symbols between dollars) as these pieces of text will be copy-pasted in .tex files!**

## Produce the feedback forms

**Careful: one needs the configuration file used to produce the templated Excel file for this part, as the "template production" and "feedback form production" share a common configuration!**

One should follow the script `tutorials/make_forms.py` using **two** `yaml` configuration file**s**:
- the file used to generate the templated Excel file
- a file with the same structure as `tutorials/config_form.yml`. *Note: this second config file is not mandatory as one can choose to use a GUI instead of this config file!*

### Script

One only needs to modify the configurables defined under `if __name__ == "__main__":` as shown in `tutorials/make_forms.py`:
- `NAME_EXCEL_CFG`: name of the configuration file used to produce the templated Excel file
- `USE_GUI`: switch to activate GUI selection (or not)
- `NAME_FORM_CFG`: name of the configuration file for feedback form generation
- `COMPILE_TEX`: **very important** switch to enable automatic compilation of the produced .tex files to .pdf via `pdflatex`. *Advice: if pdf files are not produced, do not remove log files as they may contain information on some errors (e.g. if some text in the Excel file does not respect LaTeX syntax).*

### Configuration file

*This file is optional and can be replaced by dynamic selecting via GUI, as mentioned before.*

All the elements are documented inside the example `tutorials/config_form.yml` example file.