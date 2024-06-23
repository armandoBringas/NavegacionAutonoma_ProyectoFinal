
# Navegación Autónoma Proyecto Final

Este proyecto tiene como objetivo desarrollar un sistema de navegación autónoma utilizando clonación de comportamiento y datos de sensores. 
El repositorio está organizado de la siguiente manera:

## Estructura del Proyecto

```plaintext
NavegacionAutonoma_ProyectoFinal/
│
├── config/
│   └── environment.yml
│
├── data/
│   ├── train_images/
│   └── images.csv
│
├── models/
│   └── behavioral_cloning_training.keras
│
├── notebooks/
│   └── behavioral_cloning_training.ipynb
│
├── report/
│   
├── scripts/
│   ├── behavioral_cloning_and_sensors_driving.py
│   ├── capture_controller_input.py
│   └── create_report.py
│   
├── webots_worlds/
│   ├── city_traffic_2024_02_net/
│   ├── city_traffic_2024_01.wbt
│   └── city_traffic_2024_02.wbt
│
├── .gitignore
└── README.md
```

## Descripciones de Directorios

- **config/**: Contiene archivos de configuración.
  - **environment.yml**: Archivo de configuración del entorno para configurar dependencias.

- **data/**: Contiene archivos relacionados con los datos.
  - **train_images/**: Directorio para imágenes de entrenamiento.
  - **images.csv**: Archivo CSV que contiene metadatos de imágenes.

- **models/**: Contiene modelos entrenados.
  - **gear_fifth.keras**: Ejemplo de un archivo de modelo entrenado.

- **notebooks/**: Contiene cuadernos de Jupyter.
  - **behavioral_cloning_training.ipynb**: Cuaderno para entrenar el modelo de clonación de comportamiento.
  
- **report/**: Contiene script para generar el reporte final.

- **scripts/**: Contiene scripts de Python.
  - **behavioral_cloning_and_sensors_driving.py**: Script combinado para clonación de comportamiento y conducción con datos de sensores.
  - **capture_controller_input.py**: Script para capturar datos de entrada.
  - **create_report.py**: Script para crear informes.

- **webots_worlds/**: Contiene mundos de simulación de Webots.
- - **city_traffic_2024_02_nets/**: Directorio con las configuraciones de SUMO.
  - **city_traffic_2024_01.wbt**: Archivo del mundo de Webots para el escenario de tráfico de la ciudad 01.
  - **city_traffic_2024_02.wbt**: Archivo del mundo de Webots para el escenario de tráfico de la ciudad 02.

- **.gitignore**: Especifica qué archivos/carpetas ignorar en el control de versiones.
- **README.md**: Archivo de documentación que explica el proyecto.

## Instrucciones de Configuración

Para configurar el entorno, ejecute el siguiente comando:

```bash
conda env create -f config/environment.yml
```

Active el entorno:

```bash
conda activate your_environment_name
```

## Secuencia de Uso

### Captura de Datos de Entrada

Para capturar datos de entrada, ejecute:

```bash
python scripts/capture_controller_input.py
```

### Entrenamiento del Modelo

Para entrenar el modelo de clonación de comportamiento, ejecute el cuaderno de Jupyter:

```bash
jupyter notebook notebooks/behavioral_cloning_training.ipynb
```

### Conducción Usando el Modelo

Para conducir usando el modelo de clonación de comportamiento entrenado, ejecute:

```bash
python scripts/behavioral_cloning_and_sensors_driving.py
```


## Simulaciones de Webots

Para usar los mundos de simulación de Webots, abra los archivos `.wbt` ubicados en el directorio `webots_worlds/` con Webots.
