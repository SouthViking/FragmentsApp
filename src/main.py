import os

from dotenv import load_dotenv

from processor import FragmentsProcessor
from types_ import DataFolderConfig, OpenAIConfig

def main():
    load_dotenv()

    current_dir_path = os.path.dirname(os.path.realpath(__file__))
    default_input_path = os.path.normpath(os.path.join(current_dir_path, 'data', 'input'))
    default_output_path = os.path.normpath(os.path.join(current_dir_path, 'data', 'output'))

    folders_config: DataFolderConfig  = {
        'input_path': os.environ.get('INPUT_FOLDER_PATH', default_input_path),
        'output_path': os.environ.get('OUTPUT_FOLDER_PATH', default_output_path),
    }

    openai_config: OpenAIConfig = {
        'api_key': os.environ.get('OPENAI_API_KEY', None),
        'models': {
            'base': os.environ.get('BASE_MODEL', None),
            'embedding': os.environ.get('EMBEDDING_MODEL', None),
        }
    }

    processor = FragmentsProcessor(folders_config, openai_config)
    fragments = processor.generate_fragments_from_file(os.environ.get('INPUT_FILE'))
    processor.export_fragments(fragments)

if __name__ == '__main__':
    main()