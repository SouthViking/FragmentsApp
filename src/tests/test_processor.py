import json
import os
import sys
from typing import Any
import unittest

import random
from dotenv import load_dotenv

sys.path.append('../')

from processor import FragmentsProcessor
from types_ import DataFolderConfig, OpenAIConfig

def generate_random_elements(count: int, output_file_path: str) -> dict:
    elements = []
    possible_types = ['article', 'article_link', 'category']
    generated_types = { 'article': 0, 'article_link': 0, 'category': 0 }

    for _ in range(count):
        element = {}
        selected_type = random.choice(possible_types)

        generated_types[selected_type] += 1

        if selected_type != 'article':
            element['type'] = selected_type
            element['url'] = 'some url'
            element['title'] = 'some title'

        else:
            element['type'] = 'article'
            element['url'] = 'some url'
            element['text'] = 'some text'

        elements.append(element)

    with open(output_file_path, 'w') as file:
        for element in elements:
            json.dump(element, file)
            file.write('\n')

    return generated_types

class TestFragmentsProcessor(unittest.TestCase):
    """ Tests para el procesamiento de fragmentos. """
    test_data_folder_path: str = None
    fragment_processor: FragmentsProcessor = None

    @classmethod
    def setUpClass(cls):
        load_dotenv()

        cls.test_data_folder_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')

        if not os.path.exists(cls.test_data_folder_path):
            os.makedirs(cls.test_data_folder_path)

        folder_path_config: DataFolderConfig = {
            'input_path': cls.test_data_folder_path,
            'output_path': cls.test_data_folder_path,
        }

        openai_config: OpenAIConfig = {
            'api_key': os.environ.get('OPENAI_TEST_API_KEY'),
            'models': {
                'base': os.environ.get('BASE_TEST_MODEL'),
                'embedding': os.environ.get('EMBEDDING_TEST_MODEL'),
            }
        }

        cls.fragment_processor = FragmentsProcessor(folder_path_config, openai_config)

    def test_elements_sanitization_from_file(self):
        """ El proceso de sanitización debe filtrar según el tipo de elemento. """

        types_to_filter = ['article', 'article_link', 'category']
        output_file_path = os.path.normpath(os.path.join(self.test_data_folder_path, 'random_elements.jsonl'))

        generated_elements_count = generate_random_elements(20, output_file_path)

        for filter_type in types_to_filter:
            filtered_elements = self.fragment_processor.get_sanitized_elements_from_file(output_file_path, (filter_type, Any))
            
            expected_number_of_elements = generated_elements_count[filter_type]

            if len(filtered_elements) != expected_number_of_elements:
                raise Exception(f'La cantidad de elementos filtrados no es correcta. Actual: {len(filtered_elements)} / Esperado: {expected_number_of_elements}')

            for element in filtered_elements:
                if element.get('type') != filter_type:
                    raise Exception(f'Tipo de elemento no es el esperado. Actual: {element.get("type")} / Esperado: {filter_type}')
                

    def test_chat_completion_request_execution(self):
        """ El proceso de request a la API de OpenAI debe devolver una response válida. """
        
        response = self.fragment_processor.execute_chat_completion_request({
            'model': os.environ.get('BASE_TEST_MODEL'),
            'messages': [{ 'role': 'user', 'content': 'Hello world!' }]
        })

        self.assertIsNotNone(response, 'Se debe obtener una respuesta correcta al realizar una request simple.')


    def test_arguments_extraction_from_function_call_request(self):
        """ La extracción de argumentos desde la response de OpenAI debe entregar un diccionario válido. """

        response = self.fragment_processor.execute_chat_completion_request({
            'model': os.environ.get('BASE_TEST_MODEL'),
            'messages': [{ 'role': 'user', 'content': 'Hello world!' }]
        })
        arguments = self.fragment_processor.get_arguments_from_function_call_response(response)

        self.assertIsInstance(arguments, dict, 'El resultado debe ser un diccionario.')
        self.assertEqual(len(list(arguments.keys())), 0, 'Debe devolver un diccionario vacío en caso de que no se puedan extraer los argumentos de la response.')

        prompt_using_function_call = {
            'model': os.environ.get('BASE_TEST_MODEL'),
            'messages': [{ 'role': 'user', 'content': 'Extrae nombre, apellido y edad de la oración: "Me llamo Juan Perez y tengo 25 años"' }],
            'functions': [{
                'name': 'get_structured_data',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'name': { 'title': 'nombre', 'type': 'string' },
                        'last_name': { 'title': 'apellido', 'type': 'string' },
                        'age': { 'title': 'edad', 'type': 'number' }
                    },
                },
                'required': ['name', 'last_name', 'age'],
            }],
            'function_call': { 'name': 'get_structured_data' }
        }

        response = self.fragment_processor.execute_chat_completion_request(prompt_using_function_call)
        arguments = self.fragment_processor.get_arguments_from_function_call_response(response)

        self.assertIsInstance(arguments, dict, 'El resultado debe ser un diccionario.')
        self.assertNotEqual(len(list(arguments.keys())), 0, "Debe devolver un diccionario no vacío con los valores solicitados.")

        for field in ['name', 'last_name', 'age']:
            if arguments.get(field) is None:
                raise Exception(f'Campo esperado "{field}" no se encuentra presente en los argumentos. (campos: {list(arguments.keys())})')
            
    def test_fragment_generation(self):
        """ La generación de fragmentos debe tomar la información del elemento y mediante OpenAI obtener datos específicos. """

        input_file_path = os.path.normpath(os.path.join(self.test_data_folder_path, 'coherent_elements.jsonl'))

        elements = self.fragment_processor.get_sanitized_elements_from_file(input_file_path, ('article', Any))

        expected_fields = ['id', 'title', 'summary', 'tags', 'content', 'original_reference', 'tags']

        for index, element in enumerate(elements):
            fragment = self.fragment_processor.generate_fragment_from_element(element, index)

            self.assertIsInstance(fragment, dict, 'El fragmento generado debe ser un diccionario.')

            for field in expected_fields:
                if fragment.get(field) is None:
                    raise Exception(f'Campo {field} no encontrado en fragmento generado.')