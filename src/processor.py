import os
import json
from io import TextIOWrapper
from datetime import datetime
from urllib.parse import urlparse
from typing import List, Tuple, Type, TypeVar

import openai
from openai.embeddings_utils import get_embedding, distances_from_embeddings, indices_of_nearest_neighbors_from_distances

from utils import FileManager, get_token_length_from_text
from types_ import ArticleElement, ChatCompletionResponse, DataFolderConfig, ElementType, FragmentData, OpenAIConfig, OpenAIModelsConfig

T = TypeVar('T')

class FragmentsProcessor:
    # TODO: documentación
    MAX_TOKENS_TO_SEND = 1500
    MAX_RELATED_FRAGMENTS = 3

    def __init__(self, folder_paths: DataFolderConfig, openai_config: OpenAIConfig):
        openai.api_key = openai_config['api_key']
        self.models: OpenAIModelsConfig = openai_config['models']

        self.file_manager = FileManager()
        self.folders_config = folder_paths

    def process_file(self, file_with_extension: str):
        counter = 0
        fragments: List[FragmentData] = []

        absolute_file_path = os.path.normpath(os.path.join(self.folders_config['input_path'], file_with_extension))
        elements = self.get_sanitized_data_from_jsonl_file(absolute_file_path, (ElementType.ARTICLE.value, ArticleElement))        
        
        for index, element in enumerate(elements):
            if index == 5:
                break

            if get_token_length_from_text(element['text'], self.models['base']) > self.MAX_TOKENS_TO_SEND:
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
            fragment_data['id'] = counter
            fragment_data['content'] = element['text']
            fragment_data['original_reference'] = urlparse(element['url']).path[1:].split('/')[0]

            fragments.append(fragment_data)

            counter += 1

        self.calculate_fragments_relations(fragments, self.MAX_RELATED_FRAGMENTS)
        self.export_fragments(fragments)

    def calculate_fragments_relations(self, fragments: List[FragmentData], max_related_fragments: int):
        """
            Calcula los fragmentos relacionados y agrega su referencia a la información de cada uno.

            Args:
                fragments: La lista de fragmentos para calcular las relaciones con otros fragmentos.
                max_related_fragments: El número máximo de fragmentos relacionados a incluir en la información del fragmento.
        """
        embeddings: List[List[float]] = [get_embedding(fragment['content'], self.models['embedding']) for fragment in fragments]

        for index, fragment in enumerate(fragments):
            relation_distances = distances_from_embeddings(embeddings[index], embeddings, distance_metric = 'cosine')
            # Se utiliza [1:] intencionalmente para poder remover el primer valor, el cual corresponderá al mismo fragmento.
            indices_of_closest_fragments: List[int] = indices_of_nearest_neighbors_from_distances(relation_distances)[1:]

            fragment['related_fragments'] = []
            fragment['related_fragments_titles'] = []

            for related_fragment_index in indices_of_closest_fragments[:max_related_fragments]:
                fragment['related_fragments'].append(fragments[related_fragment_index]['id'])
                fragment['related_fragments_titles'].append(fragments[related_fragment_index]['title'])

    def export_fragments(self, fragments: List[FragmentData]):
        current_timestamp = datetime.now().replace(microsecond = 0).timestamp()
        absolute_output_file_path = os.path.normpath(os.path.join(self.folders_config['output_path'], f'fragments_{current_timestamp}.jsonl'))

        def fragments_writer_callback(file: TextIOWrapper):
            for fragment in fragments:
                json.dump(fragment, file, ensure_ascii = False, indent = 4)
                file.write('\n')

        self.file_manager.write_to_file(absolute_output_file_path, fragments_writer_callback)

    def get_sanitized_data_from_jsonl_file(self, absolute_file_path: str, element_type_target: Tuple[str, Type[T]]) -> List[T]:
        """
            Permite obtener los datos desde el archivo jsonl especificado y convertirlos a diccionarios válidos.

            Args:
                absolute_file_path: La ruta absoluta del archivo del cual se van a obtener los datos.
                element_type_target: Una tupla que contiene en primer lugar el nombre del tipo a filtrar y en segundi
                    lugar el tipo.
                    
            Returns:
                Retorna una lista de elementos filtrados, sanitizados y convertidos en diccionarios.
        """
        try:
            raw_jsonl_data = self.file_manager.get_file_content(absolute_file_path)
            raw_jsonl_data = list(raw_jsonl_data.strip().split('\n'))

            sanitized_elements: List[T] = []

            for i in range(len(raw_jsonl_data)):
                element = json.loads(raw_jsonl_data[i])

                if element_type_target[0] != element['type']:
                    continue

                sanitized_elements.append(element)

            return sanitized_elements
        
        except Exception as error:
            raise Exception(f'Error: Se ha producido un error durante la sanitización del archivo {absolute_file_path}: {str(error)}')