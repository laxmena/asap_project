import json
import logging
import requests
from typing import Dict, Any, Optional, List
from datetime import datetime
import os
import base64
from src.utils.redis import RedisUtils
from src.utils.llm import LLMSingleton
from src.constants import DataSourceType, DataType, RedisKeys, QueueNames
from time import sleep

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CommandSystemAgent:
    def __init__(self):
        """Initialize CommandSystemAgent with Redis connection and LLM setup."""
        self.redis_utils = RedisUtils()
        self.llm = LLMSingleton.get_instance()


    def _get_prompt_template(self, data_type: str) -> Optional[str]:
        """Read and prepare the prompt template based on data type."""
        try:
            logger.info(f"Getting prompt template for {data_type}")
            prompt_file = f"prompts/{data_type}_prompt.txt"
            with open(prompt_file, "r") as f:
                prompt_template = f.read()
            return prompt_template
        except Exception as e:
            logger.error(f"Error reading prompt template for {data_type}: {str(e)}")
            return None

    def _replace_payload_in_prompt(self, prompt_template: str, payload: Dict[str, Any]) -> str:
        try:
            payload_str = json.dumps(payload, indent=4, ensure_ascii=False, default=str)
            return prompt_template.replace("<replace_payload>", payload_str)
        except Exception as e:
            logger.error(f"Error replacing payload in prompt: {str(e)}")
            return ""


    def process_data(self, task_data: Dict[str, Any]) -> bool:
        """Process the data and return a boolean value."""
        logger.info("[COMMAND SYSTEM AGENT] Processing command system data")
        events = task_data.get("events")

        prompt_template = self._get_prompt_template("command_system")
        if not prompt_template:
            logger.error("Failed to get prompt template")
            return False

        prompt = self._replace_payload_in_prompt(prompt_template, {"events": events})
        logger.debug("Prompt: ", prompt)

        response = self.llm.invoke(prompt)

        # pretty print the response
        print(json.dumps(json.loads(response.content), indent=4))
        task_allocator_payload = json.loads(response.content)
        
        self.redis_utils.redis_client.set(RedisKeys.COMMAND_SYSTEM_RESPONSE.value, response.content)

        # Forward to Task Allocator
        self.redis_utils.enqueue_task(
            "task_allocator",
            task_allocator_payload
        )

        return True

