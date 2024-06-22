import nbformat as nbf
import os
import subprocess


def create_notebook(script_paths, notebook_paths, output_path):
    nb = nbf.v4.new_notebook()

    # Cover Page
    cover_page = nbf.v4.new_markdown_cell(
        "# Project Report\n\n"
        "**Author:** Armando Bringas\n\n"
        "**Date:** June 22, 2024\n\n"
        "**Project Title:** Behavioral Cloning for Autonomous Driving\n\n"
        "**Description:** This report includes the scripts and detailed explanations of the behavioral cloning project for autonomous driving."
    )
    nb.cells.append(cover_page)

    # Add scripts
    for script_path in script_paths:
        with open(script_path, 'r', encoding='utf-8') as file:
            script_content = file.read()
        script_cell = nbf.v4.new_code_cell(script_content)
        description_cell = nbf.v4.new_markdown_cell(
            f"## Script: {os.path.basename(script_path)}\n\nDescription of the script.")
        nb.cells.append(description_cell)
        nb.cells.append(script_cell)

    # Add content of other notebooks
    for notebook_path in notebook_paths:
        with open(notebook_path, 'r', encoding='utf-8') as f:
            other_nb = nbf.read(f, as_version=4)

        # Add a header for the included notebook
        header = nbf.v4.new_markdown_cell(f"## Notebook: {os.path.basename(notebook_path)}")
        nb.cells.append(header)

        # Append the cells from the other notebook
        nb.cells.extend(other_nb.cells)

    with open(output_path, 'w', encoding='utf-8') as f:
        nbf.write(nb, f)


# Paths to the scripts and notebooks you want to include
script_paths = [
    "behavioral_cloning_driving.py",
    "capture_controller_input.py",
    "behavioral_cloning_and_sensors_driving.py"
]

notebook_paths = [
    "behavioral_cloning_training.ipynb"
]

output_path = "Proyecto_Final_Equipo13.ipynb"
create_notebook(script_paths, notebook_paths, output_path)

# Convert the notebook to PDF
subprocess.run(["jupyter", "nbconvert", "--to", "pdf", output_path])
