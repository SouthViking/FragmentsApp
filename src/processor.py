import json
from typing import List, Tuple, Type, TypeVar

import openai

from utils import FileManager, get_token_length_from_text
from types_ import ArticleElement, ChatCompletionResponse, DataFolderConfig, ElementType, FragmentData, OpenAIConfig, OpenAIModelsConfig

T = TypeVar('T')

class FragmentsProcessor:
    # TODO: documentación
    MAX_TOKENS_TO_SEND = 1500

    def __init__(self, folder_paths: DataFolderConfig, openai_config: OpenAIConfig):
        openai.api_key = openai_config['api_key']
        self.models: OpenAIModelsConfig = openai_config['models']

        self.output_folder_path = folder_paths['output_path']
        self.file_manager = FileManager(folder_paths['input_path'])

    def process_file(self, file_with_extension: str):
        elements = self.get_sanitized_data_from_jsonl_file(file_with_extension, (ElementType.ARTICLE.value, ArticleElement))
        fragments: List[FragmentData] = []
        
        for element in elements:
            tokens_length = get_token_length_from_text(element['text'], self.models['base'])

            if tokens_length > self.MAX_TOKENS_TO_SEND:
                # TODO: Debido a que el texto es muy largo, hay que dividirlo y enviarlo por partes. (batch)
                # TODO: Agregar control igualmente del máximo de tokens permitidos por el modelo a utilizar.
                continue

            response: ChatCompletionResponse = openai.ChatCompletion.create(
                model = self.models['base'],
                messages = [{ 'role': 'user', 'content': f'titulo, resumen y palabras_claves del texto: "{element["text"]}"' }],
                functions = [
                    {
                        'name': 'get_fragment_data',
                        'description': 'Obtiene la información principal del elemento',
                        'parameters': {
                            'type': 'object',
                            'properties': {
                                'title': { 'title': 'titulo', 'type': 'string' },
                                'summary': { 'title': 'resumen', 'type': 'string' },
                                'tags': { 'title': 'palabras_claves', 'type': 'array', 'items': { 'type': 'string' } }
                            },
                        },
                        'required': ['title', 'summary', 'tags']
                    },
                ],
                function_call = { 'name': 'get_fragment_data' },
            )
            
            fragment_data: FragmentData = json.loads(response['choices'][0]['message']['function_call']['arguments'].strip().replace('\n', ''))
            fragment_data['content'] = element['text']
            # TODO: Definir referencia a artículo original

            fragments.append(fragment_data)

        self.calculate_fragments_relations(fragments)
        self.export_fragments(fragments)

    # TODO: Calcular relación con otros fragmentos
    def calculate_fragments_relations(self, fragments: List[FragmentData]):
        pass

    # TODO: Exportar fragmentos a carpeta de outputs
    def export_fragments(self, fragments: List[FragmentData]):
        pass
            
    # TODO: Agregar doc strings
    def get_sanitized_data_from_jsonl_file(self, file_with_extension: str, element_type_target: Tuple[str, Type[T]]) -> List[T]:
        try:
            raw_jsonl_data = self.file_manager.get_file_content(file_with_extension)
            raw_jsonl_data = list(raw_jsonl_data.strip().split('\n'))

            sanitized_elements: List[T] = []

            for i in range(len(raw_jsonl_data)):
                element = json.loads(raw_jsonl_data[i])

                if element_type_target[0] != element['type']:
                    continue

                sanitized_elements.append(element)

            return sanitized_elements
        
        except Exception as error:
            raise Exception(f'Error: Se ha producido un error durante la sanitización del archivo {file_with_extension}: {str(error)}')