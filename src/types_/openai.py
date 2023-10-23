from typing import List, TypedDict, Union

class UsageData(TypedDict):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int

class FunctionCallData(TypedDict):
    name: str
    arguments: str

class MessageData(TypedDict):
    role: str
    content: Union[str, None]
    function_call: Union[FunctionCallData, None]

class ChoiceData(TypedDict):
    index: int
    message: MessageData
    finish_reason: str

class ChatCompletionResponse(TypedDict):
    id: str
    object: str
    created: int
    model: str
    choices: List[ChoiceData]
    usage: UsageData