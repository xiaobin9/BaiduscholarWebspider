
from langchain_openai import ChatOpenAI


import os
from dotenv import load_dotenv
load_dotenv()

def get_llm_model():
    model_map = {
        'openai': ChatOpenAI(

            temperature = os.getenv('TEMPERATURE'),
            max_tokens = os.getenv('MAX_TOKENS'),
        )
    }
    return model_map.get(os.getenv('LLM_MODEL'))


if __name__ == '__main__':
    llm_model = get_llm_model()
    print(llm_model.invoke(''))