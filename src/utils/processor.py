from types_ import ChatCompletionRequest

def get_fragment_extraction_prompt_for_text(model: str, text: str) -> ChatCompletionRequest:
    return {
        'model': model,
        'messages': [{ 'role': 'user', 'content': f'titulo, resumen y palabras_claves para el siguiente texto: "{text}"' }],
        'functions': [{
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
            'required': ['title', 'summary', 'tags'],
        }],
        'function_call': { 'name': 'get_fragment_data' }
    }