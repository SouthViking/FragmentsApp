import os

from exceptions import FileNotFoundException, NotFileException

class FileManager:
    def __init__(self, base_path: str) -> None:
        self.base_path = base_path

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
        full_file_path = os.path.normpath(os.path.join(self.base_path, file_with_extension))

        if not os.path.exists(full_file_path):
            raise FileNotFoundException('Error: La ruta del archivo no es correcta.')

        if not os.path.isfile(full_file_path):
            raise NotFileException('Error: La ruta especificada no corresponde a la de un archivo.')
        
        try:
            with open(full_file_path, 'r') as file:
                return file.read()

        except Exception as error:
            raise Exception(f'Error: Error inesperado durante la obtención del contenido del archivo ({full_file_path}): {str(error)}')