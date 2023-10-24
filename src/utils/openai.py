from typing import List

import tiktoken

def get_tokens_from_text(text: str, model: str) -> List[int]:
    """
        Calcula los tokens utilizados para un texto según el modelo de OpenAI a utilizar.

        Args:
            text: El texto a evaluar.
            model: El modelo de OpenAI utilizado para realizar las consultas.

        Returns:
            Una lista de tokens convertidos del texto original.
    """

    encoder = tiktoken.encoding_for_model(model)

    return encoder.encode(text)

def get_token_length_from_text(text: str, model: str) -> int:
    """
        Calcula la cantidad de tokens utilizados para un texto según el modelo de OpenAI a utilizar.

        Args:
            text: El texto a evaluar.
            model: El modelo de OpenAI utilizado para realizar las consultas.

        Returns:
            Un entero representando la cantidad de tokens necesarios para el texto original.
    """
    return len(get_tokens_from_text(text, model))