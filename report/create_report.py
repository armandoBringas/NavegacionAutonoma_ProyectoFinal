import nbformat as nbf
import os
import subprocess
import base64

def create_notebook(script_paths, notebook_paths, readme_path, logo_path, output_path):
    nb = nbf.v4.new_notebook()

    # Set metadata for the notebook
    nb.metadata['title'] = "Proyecto Final"
    nb.metadata['date'] = "22 de junio de 2024"

    # Cover Page with Logo using LaTeX in a raw cell
    cover_page = nbf.v4.new_raw_cell(
        r"""
        \begin{center}
        \includegraphics[width=0.5\textwidth]{""" + logo_path + r"""}
        \end{center}

        \begin{center}
        \huge \textbf{Clonación de Comportamiento (Behavioral Cloning) para Conducción Autónoma}
        \end{center}

        \begin{center}
        \Large \textbf{MR4010 Navegación Autónoma}
        \end{center}

        \vspace{1cm}

        \textbf{Docentes} \\
        - Dr. David Antonio Torres. \\
        - Mtra. Maricarmen Vázquez Rojí. \\
        - Tutor Prof. Luis Ángel Lozano Medina \\

        \vspace{1cm}

        \textbf{EQUIPO 13} \\

        \textbf{Integrantes} \\
        - Armando Bringas Corpus (A01200230). \\
        - Juan Sebastián Téllez López (A01793859). \\
        - Marcos Eduardo García Ortiz (A01276213). \\

        \vspace{1cm}

        \textbf{Fecha:} 22 de junio de 2024 \\

        \vspace{1cm}

        \textbf{Objetivo:} Aplicación de la mayoría de los conceptos relacionados con Aprendizaje Máquina, Redes Neuronales Profundas y la programación de vehículos autónomos. \\
        """
    )
    nb.cells.append(cover_page)

    # Add project information and links
    project_info = nbf.v4.new_markdown_cell(
        "# Links del proyecto\n"
        "- Repositorio de Github: [https://github.com/armandoBringas/NavegacionAutonoma_ProyectoFinal](https://github.com/armandoBringas/NavegacionAutonoma_ProyectoFinal)\n"
        "- Video en YouTube: TBD\n"
    )
    nb.cells.append(project_info)

    # Add README.md content
    with open(readme_path, 'r', encoding='utf-8') as readme_file:
        readme_content = readme_file.read()
    readme_cell = nbf.v4.new_markdown_cell(f"{readme_content}")
    nb.cells.append(readme_cell)

    # Add scripts
    for script_path in script_paths:
        with open(script_path, 'r', encoding='utf-8') as file:
            script_content = file.read()
        script_cell = nbf.v4.new_code_cell(script_content)
        description_cell = nbf.v4.new_markdown_cell(
            f"# Código (.py): {os.path.basename(script_path)}\n\nContenido y descripción del código:"
        )
        nb.cells.append(description_cell)
        nb.cells.append(script_cell)

    # Add content of other notebooks
    for notebook_path in notebook_paths:
        with open(notebook_path, 'r', encoding='utf-8') as f:
            other_nb = nbf.read(f, as_version=4)

        # Add a header for the included notebook
        header = nbf.v4.new_markdown_cell(f"# Libreta (.ipynb): {os.path.basename(notebook_path)}")
        nb.cells.append(header)

        # Append the cells from the other notebook
        nb.cells.extend(other_nb.cells)

    with open(output_path, 'w', encoding='utf-8') as f:
        nbf.write(nb, f)

# Paths to the scripts and notebooks you want to include
script_paths = [
    "../scripts/behavioral_cloning_and_sensors_driving.py",
    "../scripts/capture_controller_input.py",
]

notebook_paths = [
    "../notebooks/behavioral_cloning_training.ipynb"
]

readme_path = "../README.md"
logo_path = "img/Logo_Tec.png"
output_path = "Proyecto_Final_Equipo13.ipynb"

create_notebook(script_paths, notebook_paths, readme_path, logo_path, output_path)

# Convert the notebook to PDF
subprocess.run(["jupyter", "nbconvert", "--to", "pdf", output_path])
