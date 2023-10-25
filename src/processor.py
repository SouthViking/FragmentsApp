import json
import os
import textwrap
import time
from datetime import datetime
from io import TextIOWrapper
from typing import List, Tuple, Type, TypeVar
from urllib.parse import urlparse

import openai
from openai.embeddings_utils import (
    distances_from_embeddings,
    get_embedding,
    indices_of_nearest_neighbors_from_distances,
)

from types_ import (
    ArticleElement,
    ChatCompletionRequest,
    ChatCompletionResponse,
    DataFolderConfig,
    ElementType,
    FragmentData,
    OpenAIConfig,
    OpenAIModelsConfig,
)
from utils import (
    FileManager,
    get_token_length_from_text,
    get_fragment_extraction_prompt_for_text,
)

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
    
    def generate_fragments_from_file(self, file_with_extension: str) -> List[FragmentData]:
        fragments: List[FragmentData] = []

        absolute_file_path = os.path.normpath(os.path.join(self.folders_config['input_path'], file_with_extension))
        elements = self.get_sanitized_elements_from_file(absolute_file_path, (ElementType.ARTICLE.value, ArticleElement))[:40]

        for index, element in enumerate(elements):
            fragment = self.generate_fragment_from_element(element, index)
            fragments.append(fragment)

        self.calculate_fragments_relations(fragments, 3)

        return fragments

    def generate_fragment_from_element(self, element: Type[T], id: int) -> FragmentData:
        fragment_data: FragmentData = {}
        fragment_data['id'] = id

        if get_token_length_from_text(element['text'], self.models['base']) > self.MAX_TOKENS_TO_SEND:
            # Como regla general especificada por OpenAI, un token corresponde aproximadamente a 4 caracteres.
            # En este caso se utiliza esa relación para poder separar el texto en partes de acuerdo al máximo de tokens especificado.
            text_chunks = textwrap.wrap(element['text'], self.MAX_TOKENS_TO_SEND * 4)

            tags = {}
            summary = []

            for index, text_chunk in enumerate(text_chunks):
                prompt = get_fragment_extraction_prompt_for_text(self.models['base'], text_chunk)
                response = self.execute_chat_completion_request(prompt)

                partial_fragment_data = self.get_arguments_from_function_call_response(response)

                if index == 0:
                    fragment_data['title'] = partial_fragment_data.get('title', '')

                for tag in partial_fragment_data.get('tags', []):
                    tags[tag.lower()] = 1
                    
                summary.append(partial_fragment_data.get('summary', ''))
            
            fragment_data['tags'] = list(tags.keys())
            fragment_data['summary'] = '\n'.join(summary)

        else:
            prompt = get_fragment_extraction_prompt_for_text(self.models['base'], element['text'])
            response = self.execute_chat_completion_request(prompt)

            partial_fragment_data = self.get_arguments_from_function_call_response(response)
            fragment_data.update(partial_fragment_data)
            
        fragment_data['content']= element['text']
        fragment_data['original_reference'] = urlparse(element['url']).path[1:].split('/')[0]

        return fragment_data

    def execute_chat_completion_request(self, request_data: ChatCompletionRequest):
        attempts = 3

        while attempts > 0:
            try:
                response: ChatCompletionResponse = openai.ChatCompletion.create(
                    model = request_data.get('model'),
                    messages = request_data.get('messages', []),
                    functions = request_data.get('functions', None),
                    function_call = request_data.get('function_call', None),
                    request_timeout = 60,
                )

                return response
                
            except Exception as error:
                print(f'Error: Se ha producido un error durante la comunicación con API de OpenAI: {str(error)}')
                attempts -= 1

                time.sleep(5)

        return None
    
    def get_arguments_from_function_call_response(self, response: ChatCompletionResponse) -> dict:
        if response is None:
            return {}

        try:
            arguments = json.loads(response['choices'][0]['message']['function_call']['arguments'].strip().replace('\n', ''))
            return arguments
        
        except Exception as error:
            print(f'Error durante la conversión de respuesta de OpenAI: {str(error)}')
            return {}

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

    def get_sanitized_elements_from_file(self, absolute_file_path: str, element_type_target: Tuple[str, Type[T]]) -> List[T]:
        """
            Permite obtener los datos desde el archivo jsonl especificado y convertirlos a diccionarios válidos.

            Args:
                absolute_file_path: La ruta absoluta del archivo del cual se van a obtener los datos.
                element_type_target: Una tupla que contiene en primer lugar el nombre del tipo a filtrar y en segundo
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