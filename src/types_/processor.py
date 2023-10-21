from enum import Enum
from typing import TypedDict

class DocumentType(Enum):
    CATEGORY = 'category'
    ARTICLE_LINK = 'article_link'
    ARTICLE = 'article'

class BaseInputDocument(TypedDict):
    type: DocumentType
    url: str

class CategoryDocument(BaseInputDocument):
    title: str

class ArticleLinkDocument(BaseInputDocument):
    title: str

class ArticleDocument(BaseInputDocument):
    text: str