import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from src.utils.redis import RedisUtils
from src.utils.llm import LLMSingleton

logger = logging.getLogger(__name__)

class TaskAllocator:
    def __init__(self):
        """Initialize TaskAllocator with Redis connection and LLM setup."""
        self.redis_utils = RedisUtils()
        self.llm = LLMSingleton.get_instance()

    def _construct_payload(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Construct payload for LLM prompt."""
        bots_metadata = self.redis_utils.get_all_bots_metadata()
        return {
            "tasks": [task],
            "bots_metadata": bots_metadata
        }

    def _get_prompt_template(self) -> Optional[str]:
        """Read and prepare the prompt template."""
        try:
            with open("prompts/task_allocator_prompt.txt", "r") as f:
                prompt_template = f.read()
            return prompt_template
        except Exception as e:
            logger.error(f"Error reading prompt template: {str(e)}")
            return None

    def _replace_payload_in_prompt(self, prompt_template: str, payload: Dict[str, Any]) -> str:
        """Replace the payload section in the prompt template."""
        try:
            # Use ensure_ascii=False to handle non-ASCII characters
            # Use default=str to handle non-serializable objects
            payload_str = json.dumps(payload, indent=4, ensure_ascii=False, default=str)
            return prompt_template.replace("<replace_payload>", payload_str)
        except Exception as e:
            logger.error(f"Error replacing payload in prompt: {str(e)}")
            return ""

    def _dispatch_task(self, llm_response: Dict[str, Any]) -> bool:
        """Dispatch task to appropriate agent queue based on bot type."""
        try:
            bot_type = llm_response.get("bot_type")
            queue_name = f"{bot_type}_agent_task"
            
            # Add timestamp for task scheduling
            llm_response["task_allocated_timestamp"] = datetime.now().isoformat()
            
            return self.redis_utils.enqueue_task(queue_name, llm_response)
        except Exception as e:
            logger.error(f"Error dispatching task: {str(e)}")
            return False

    def _validate_task(self, task: Dict[str, Any]) -> bool:
        """Validate task data before processing."""
        required_fields = ["task_id", "task_type", "lat", "long", "timestamp"]
        return all(field in task for field in required_fields)

    def process_task(self, task: Dict[str, Any]) -> bool:
        """Process a single task and allocate it to an appropriate bot."""
        try:
            # Validate task data
            if not self._validate_task(task):
                logger.error(f"Invalid task data: {task}")
                return False

            logger.info(f"Processing task {task.get('task_id')}")

            # Construct payload
            payload = self._construct_payload(task)
            logger.debug(f"Constructed payload: {json.dumps(payload, ensure_ascii=False, default=str)}")

            # Get and prepare prompt
            prompt_template = self._get_prompt_template()
            if not prompt_template:
                return False

            prompt = self._replace_payload_in_prompt(prompt_template, payload)
            if not prompt:
                return False

            # Get LLM response
            response = self.llm.invoke(prompt)
            logger.debug(f"LLM Response: {response.content}")

            # Parse LLM response
            try:
                llm_response = json.loads(response.content)
                logger.info(f"LLM response: {llm_response}")
            except json.JSONDecodeError as e:
                logger.debug(f"LLM total response: {response}")
                logger.error(f"Error parsing LLM response: {str(e)}")
                return False

            # Dispatch task
            success = self._dispatch_task(llm_response)
            if success:
                logger.info(f"Successfully dispatched task {task.get('task_id')}")
            else:
                logger.error(f"Failed to dispatch task {task.get('task_id')}")

            return success

        except Exception as e:
            logger.error(f"Error processing task: {str(e)}")
            return False 