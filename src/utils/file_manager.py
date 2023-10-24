import os
from typing import Callable
from io import TextIOWrapper

from exceptions import FileNotFoundException, NotFileException

class FileManager:
    def __init__(self, base_path: str) -> None:
        self.base_path = base_path

    def set_base_path(self, base_path: str):
        if not os.path.exists(base_path):
            os.makedirs(base_path)

        self.base_path = base_path

    def get_full_path(self, file_with_extension: str) -> str:
        return os.path.normpath(os.path.join(self.base_path, file_with_extension))

    def get_file_content(self, file_with_extension: str) -> str:
        """
            Abre el archivo especificado en `file_with_extension` para obtener su contenido.

            Args:
                file_with_extension: El nombre del archivo junto a la extensión. (Ej: `example.txt`) 

            Returns:
                El contenido del archivo especificado en caso de que poder abrirlo correctamente.

            Raises:
                FileNotFoundException: Si la ruta del archivo no es correcta.
                NotFileException: Si la ruta especificada no corresponde a la de un archivo.
                Exception: En caso de cualquier otro tipo de error al momento de abrir y leer el archivo.
        """
        full_file_path = self.get_full_path(file_with_extension)

        if not os.path.exists(full_file_path):
            raise FileNotFoundException('Error: La ruta del archivo no es correcta.')

        if not os.path.isfile(full_file_path):
            raise NotFileException('Error: La ruta especificada no corresponde a la de un archivo.')
        
        try:
            with open(full_file_path, 'r') as file:
                return file.read()

        except Exception as error:
            raise Exception(f'Error: Error inesperado durante la obtención del contenido del archivo ({full_file_path}): {str(error)}')
        
    def write_to_file(self, file_with_extension: str, write_callback: Callable[[TextIOWrapper], None]):
        """
            Crea o sobrescribe el archivo especificado en `file_with_extension` en caso de existir. Permite escribir dentro del archivo
            mediante la especificación del callback `write_callback`.

            Args:
                file_with_extension: El nombre del archivo junto a la extensión. (Ej: `example.txt`)
                write_callback: La función de callback para ejecutar la escritura de contenidos. Recibe el archivo como input.
        """

        full_file_path = self.get_full_path(file_with_extension)

        with open(full_file_path, 'w', encoding = 'utf-8') as file:
            write_callback(file)