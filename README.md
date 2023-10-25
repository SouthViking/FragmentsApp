
## FragmentsApp

Esta aplicación corresponde al desafío técnico para el proceso de selección en la posición de desarrollador Full-Stack de Adereso.

La aplicación permite generar fragmentos de información desde un archivo con artículos en formato JSON mediante la utilización de la API de OpenAI. Específicamente, se utiliza el texto de cada artículo para obtener información escencial y relevante del mismo, tales como:

- Título
- Resumen
- Tags, palabras claves o etiquetas
- Fragmentos relacionados (mediante el cálculo de similaridad utilizando embeddings)

Los fragmentos procesados posteriormente son exportados en formato jsonl.

### ⚙️ Instalación

El proyecto está escrito en lenguaje Python utilizando tanto librerías internas como de terceros. Para poder ejecutar el script es necesario seguir los siguientes pasos de instalación:

1. Asegurarse de tener Python 3.9 o superior instalado. (https://www.python.org/downloads/)


2. Las librerías y versiones utilizadas para el proyecto se encuentran dentro del archivo `requirements.txt` en la carpeta principal.

3. Ejecutar el siguiente comando, el cuál realizará la instalación de cada una de las librerías especificadas en el archivo `requirements.txt` de forma automática.

```console
pip3 install -r requirements.txt
```

**Nota**: El paso 3 puede realizarse tanto de forma local, es decir, instalando las librerías globalmente en el sistema o bien dentro de un entorno virtual de forma aislada (recomendado). Para conocer más acerca de la creación y uso de entornos virtuales en Python revisar: https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/

### 📁 Estructura del proyecto

La estructura detallada del proyecto es la que se muestra a continuación.

```
.
├── C:.
├── │   .env
├── │   .gitignore
├── │   README.md
├── │   requirements.txt
├── │   
└── └───src/
    ├── │   main.py
    ├── │   processor.py
    ├── │   
    ├── ├───data
    ├── │   ├───input
    ├── │   │       adereso_cda.jsonl
    ├── │   │       
    ├── │   └───output
    ├── ├───exceptions
    ├── │   │   file_manager.py
    ├── │   │   __init__.py
    ├── │           
    ├── ├───tests
    ├── │   │   test_processor.py
    ├── │   │   
    ├── │   ├───data
    ├── │   │       coherent_elements.jsonl
    ├── │           
    ├── ├───types_
    ├── │   │   openai.py
    ├── │   │   processor.py
    ├── │   │   __init__.py
    ├── │           
    ├── ├───utils
    ├── │   │   file_manager.py
    ├── │   │   openai.py
    ├── │   │   processor.py
    └── │   │   __init__.py
```

La carpeta raiz del proyecto contiene tanto el archivo de requerimientos (librerías a utilizar), como archivos de documentación, configuración de `.gitignore` y el archivo de entorno `.env`.

Dentro de la carpeta `src`, se encuentra el archivo principal `main.py` que funciona como entrypoint para la ejecución del script. Por otra parte `processor.py` contiene la funcionalidad principal para ejecutar el procesamiento de fragmentos.

#### Carpetas internas

A continuación se describe cada una de las carpetas internas en la carpeta `src`.

- **/data**: Carpeta utilizada para leer archivos de input para el script y para generar outputs de los fragmentos procesados. Es la carpeta de input/output por defecto en caso de que no se especifique lo contrario en el archivo de entorno.

- **/exceptions**: Carpeta que contiene definiciones de excepciones personalizadas.

- **/tests**: Carpeta que contiene los tests para el proyecto.

- **/types**: Definición de tipos útiles para el desarrollo utilizando la librería interna `typing`. Permiten poder tener mayor control de los tipos de variables utilizadas y su manejo.

- **/utils**: Carpeta que contiene funciones de utilidad tanto para el proceso de fragmentación como para el manejo de archivos.

**Nota**: El script generará por defecto logs en cada una de las ejecuciones, los cuales se guardarán en la carpeta `src/logs`.


### ⚙️ Ejecución

#### Configuración de archivo de entorno

El proyecto funciona mediante la lectura de ciertos datos importantes desde el archivo de entorno. Asegurarse de crear un archivo `.env` en la carpeta raíz del proyecto.

Los valores permitidos son los siguientes:

```
# [OPCIONAL] Carpeta desde donde leer el archivo de input. Por defecto se lee desde la carpeta data/input.
# INPUT_FOLDER_PATH=...

# [OPCIONAL] Carpeta para guardar los archivos con los fragmentos procesados. Por defecto se guardan en la carpeta data/output.
OUTPUT_FOLDER_PATH=...

# [REQUERIDO] Nombre del archivo a leer y procesar.
INPUT_FILE=adereso_cda.jsonl 

# [REQUERIDO] Modelo base a utilizar para la comunicación con OpenAI.
BASE_MODEL=gpt-3.5-turbo-0613

# [REQUERIDO] Modelo a utilizar para realizar el procesamiento de fragmentos relacionados.
EMBEDDING_MODEL=text-embedding-ada-002

# [REQUERIDO] Token de la API de OpenAI para interactuar con los endpoints.
OPENAI_API_KEY=<API_TOKEN>

# [REQUERIDO] Token de la API de OpenAI para interactuar con los endpoints para ser utilizado en pruebas.
OPENAI_TEST_API_KEY=<API_TOKEN>

# [REQUERIDO] Modelo base a utilizar para la comunicación con OpenAI.
BASE_TEST_MODEL=gpt-3.5-turbo-0613

# [REQUERIDO] Modelo a utilizar para realizar el procesamiento de fragmentos relacionados.
EMBEDDING_TEST_MODEL=text-embedding-ada-002
```

#### Ejecución del script

Una vez configurado el archivo de entorno, es posible ejecutar el programa.

Para ejecutar el script simplemente se debe ejecutar el archivo `main.py` ubicado en la carpeta `src` mediante alguno de los siguientes comandos:

```
py/python/python3 main.py
```

### Notas

1. El código está escrito completamente en inglés siguiendo las buenas prácticas establecidas por el PEP-8. Los comentarios se encuentran en español más que nada para facilitar la revisión.

2. El código tiene varios puntos donde puede mejorarse, pero que por temas de tiempo y para no agregar complejidad se decidieron omitir. Ejemplos de mejoras pueden ser:

    - Agregar más tests para aumentar la cobertura en general, no sólo para el proceso de fragmentación.
    - Realizar refactorización de los métodos en la clase de procesamiento para poder separar responsabilidades en distintos métodos.
    - Para aumentar eficiencia en cuánto a la rapidéz de la ejecución, el proceso puede paralelizarse utilizando threading y aprovechando el hecho de que no existen secciones críticas por proteger.

### 🤔 Dudas

Cualquier tipo de duda o problema con cualquiera de los pasos, no dudar en contactarme mediante el correo: seb.toro.severino@gmail.com