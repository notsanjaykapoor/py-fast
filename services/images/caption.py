import dataclasses
import os

import llama_cpp
import llama_cpp.llama_chat_format

@dataclasses.dataclass
class Struct:
    code: int
    response: dict
    text: str


def caption(uri: str) -> Struct:
    """
    run one shot query to caption the specified image
    """
    struct = Struct(
        code=0,
        response={},
        text="",
    )

    chat_handler = llama_cpp.llama_chat_format.Llava16ChatHandler(
        clip_model_path=os.environ.get("APP_MODEL_CLIP_PATH"),
    )

    llm = llama_cpp.Llama(
        model_path=os.environ.get("APP_LLM_LAVA_PATH"),
        chat_handler=chat_handler,
        n_ctx=4096, # large context for image embeddings
    )

    llm_response = llm.create_chat_completion(
        messages = [
            {"role": "system", "content": "You are an assistant who perfectly describes images."},
            {
                "role": "user",
                "content": [
                    {"type" : "text", "text": "What's in this image?"},
                    {"type": "image_url", "image_url": {"url": uri } }
                ]
            }
        ]
    )

    struct.response = llm_response
    struct.text = llm_response.get("choices")[0].get("message").get("content").strip()

    return struct
