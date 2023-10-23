from enum import Enum
from typing import List, Union, TypedDict

class ElementType(Enum):
    CATEGORY = 'category'
    ARTICLE_LINK = 'article_link'
    ARTICLE = 'article'

class BaseInputElement(TypedDict):
    type: ElementType
    url: str

class CategoryElement(BaseInputElement):
    title: str

class ArticleLinkElement(BaseInputElement):
    title: str

class ArticleElement(BaseInputElement):
    text: str

class OpenAIModelsConfig(TypedDict):
    base: Union[str, None]
    embedding: Union[str, None]

class OpenAIConfig(TypedDict):
    api_key: str
    models: OpenAIModelsConfig

class DataFolderConfig(TypedDict):
    input_path: str
    output_path: str

class FragmentData(TypedDict):
    title: str
    tags: List[str]
    summary: str
    original_reference: str
    content: str
    related_fragments: List[str]