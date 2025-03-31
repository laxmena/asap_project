import os
from typing import Optional
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic

from src.constants import ANTHROPIC_API_KEY_ENV, LLM_MODEL

class LLMSingleton:
    _instance: Optional[ChatAnthropic] = None

    @classmethod
    def get_instance(cls) -> ChatAnthropic:
        """Get or create the LLM instance."""
        if cls._instance is None:
            load_dotenv()
            cls._instance = ChatAnthropic(
                model=LLM_MODEL,
                anthropic_api_key=os.getenv(ANTHROPIC_API_KEY_ENV)
            )
        return cls._instance 
    
    