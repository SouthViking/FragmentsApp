from typing import List

import tiktoken

# TODO: Agregar doc strings
def get_tokens_from_text(text: str, model: str) -> List[int]:
    encoder = tiktoken.encoding_for_model(model)

    return encoder.encode(text)

# TODO: Agregar doc strings
def get_token_length_from_text(text: str, model: str) -> int:
    return len(get_tokens_from_text(text, model))