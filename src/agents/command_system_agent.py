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
from src.utils.logging_utils import LoggerSetup

class CommandSystemAgent:
    def __init__(self, session_id: Optional[str] = None):
        """Initialize CommandSystemAgent with Redis connection and LLM setup."""
        self.redis_utils = RedisUtils()
        self.llm = LLMSingleton.get_instance()
        self.logger = LoggerSetup.get_logger(session_id=session_id, name=__name__)

    def _get_prompt_template(self, data_type: str) -> Optional[str]:
        """Read and prepare the prompt template based on data type."""
        try:
            self.logger.info(f"[COMMAND SYSTEM AGENT] Getting prompt template for {data_type}")
            prompt_file = f"prompts/{data_type}_prompt.txt"
            with open(prompt_file, "r") as f:
                prompt_template = f.read()
            return prompt_template
        except Exception as e:
            self.logger.error(f"[COMMAND SYSTEM AGENT] Error reading prompt template for {data_type}: {str(e)}")
            return None

    def _replace_payload_in_prompt(self, prompt_template: str, payload: Dict[str, Any]) -> str:
        try:
            payload_str = json.dumps(payload, indent=4, ensure_ascii=False, default=str)
            return prompt_template.replace("<replace_payload>", payload_str)
        except Exception as e:
            self.logger.error(f"[COMMAND SYSTEM AGENT] Error replacing payload in prompt: {str(e)}")
            return ""

    def process_data(self, task_data: Dict[str, Any]) -> bool:
        """Process the data and return a boolean value."""
        self.logger.info("[COMMAND SYSTEM AGENT] Starting to process command system data")
        # self.logger.debug(f"[COMMAND SYSTEM AGENT] Input data: {json.dumps(task_data, indent=4)}")
        
        events = task_data.get("events")
        self.logger.info(f"[COMMAND SYSTEM AGENT] Processing {len(events)} events")

        prompt_template = self._get_prompt_template("command_system")
        if not prompt_template:
            self.logger.error("[COMMAND SYSTEM AGENT] Failed to get prompt template")
            return False

        prompt = self._replace_payload_in_prompt(prompt_template, {"events": events})
        # self.logger.debug(f"[COMMAND SYSTEM AGENT] Generated prompt: {prompt}")

        self.logger.info("[COMMAND SYSTEM AGENT] Invoking LLM")
        response = self.llm.invoke(prompt)
        self.logger.debug(f"[COMMAND SYSTEM AGENT] LLM Response: {json.dumps(json.loads(response.content), indent=4)}")

        task_allocator_payload = json.loads(response.content)
        
        self.logger.info("[COMMAND SYSTEM AGENT] Storing response in Redis")
        self.redis_utils.redis_client.set(RedisKeys.COMMAND_SYSTEM_RESPONSE.value, response.content)

        self.logger.info("[COMMAND SYSTEM AGENT] Forwarding to Task Allocator")
        self.redis_utils.enqueue_task(
            "task_allocator",
            task_allocator_payload
        )

        self.logger.info("[COMMAND SYSTEM AGENT] Processing completed successfully")
        return True

