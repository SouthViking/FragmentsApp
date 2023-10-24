import os
from typing import Callable
from io import TextIOWrapper

from exceptions import FileNotFoundException, NotFileException

class FileManager:
    def get_file_content(self, absolute_file_path: str) -> str:
        """
            Abre el archivo especificado y extra su contenido.

            Args:
                absolute_file_path: La ruta absoluta del archivo a leer. (junto a su extensión)

            Returns:
                El contenido del archivo especificado en caso de que poder abrirlo correctamente.

            Raises:
                FileNotFoundException: Si la ruta del archivo no es correcta.
                NotFileException: Si la ruta especificada no corresponde a la de un archivo.
                Exception: En caso de cualquier otro tipo de error al momento de abrir y leer el archivo.
        """

        if not os.path.exists(absolute_file_path):
            raise FileNotFoundException('Error: La ruta del archivo no es correcta.')

        if not os.path.isfile(absolute_file_path):
            raise NotFileException('Error: La ruta especificada no corresponde a la de un archivo.')
        
        try:
            with open(absolute_file_path, 'r') as file:
                return file.read()

        except Exception as error:
            raise Exception(f'Error: Error inesperado durante la obtención del contenido del archivo ({absolute_file_path}): {str(error)}')
        
    def write_to_file(self, absolute_file_path: str, write_callback: Callable[[TextIOWrapper], None]):
        """
            Crea o sobrescribe el archivo especificado en `absolute_file_path` en caso de existir. Permite escribir dentro del archivo
            mediante la especificación del callback `write_callback`.

            Args:
                absolute_file_path: La ruta absoluta del archivo a escribir. (junto a su extensión)
                write_callback: La función de callback para ejecutar la escritura de contenidos. Recibe el archivo como input.
        """

        os.makedirs(os.path.dirname(absolute_file_path), exist_ok = True)

        with open(absolute_file_path, 'w', encoding = 'utf-8') as file:
            write_callback(file)