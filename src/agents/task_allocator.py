import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from src.utils.redis import RedisUtils
from src.utils.llm import LLMSingleton
from src.utils.logging_utils import LoggerSetup

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TaskAllocator:
    def __init__(self, session_id: Optional[str] = None):
        """Initialize TaskAllocator with Redis connection and LLM setup."""
        self.redis_utils = RedisUtils()
        self.llm = LLMSingleton.get_instance()
        self.logger = LoggerSetup.get_logger(session_id=session_id, name=__name__)

    def _construct_payload(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Construct payload for LLM prompt."""
        self.logger.info("[TASK ALLOCATOR] Constructing payload for task")
        bots_metadata = self.redis_utils.get_all_bots_metadata()
        return {
            "tasks": [task],
            "bots_metadata": bots_metadata
        }

    def _get_prompt_template(self) -> Optional[str]:
        """Read and prepare the prompt template."""
        try:
            self.logger.info("[TASK ALLOCATOR] Reading prompt template")
            with open("prompts/task_allocator_prompt.txt", "r") as f:
                prompt_template = f.read()
            return prompt_template
        except Exception as e:
            self.logger.error(f"[TASK ALLOCATOR] Error reading prompt template: {str(e)}")
            return None

    def _replace_payload_in_prompt(self, prompt_template: str, payload: Dict[str, Any]) -> str:
        """Replace the payload section in the prompt template."""
        try:
            payload_str = json.dumps(payload, indent=4, ensure_ascii=False, default=str)
            return prompt_template.replace("<replace_payload>", payload_str)
        except Exception as e:
            self.logger.error(f"[TASK ALLOCATOR] Error replacing payload in prompt: {str(e)}")
            return ""

    def _dispatch_task(self, llm_response: Dict[str, Any]) -> bool:
        """Dispatch task to appropriate agent queue based on bot type."""
        self.logger.info("[TASK ALLOCATOR] Starting task dispatch")
        self.logger.debug(f"[TASK ALLOCATOR] LLM response for dispatch: {json.dumps(llm_response, indent=4)}")
        
        if not llm_response or not isinstance(llm_response, dict):
            self.logger.info("[TASK ALLOCATOR] LLM response is empty. No tasks are allocated")
            return False
        
        if "bot_type" not in llm_response:
            self.logger.info("[TASK ALLOCATOR] Bot type is not in LLM response. No tasks are allocated")
            return False
       
        try:
            bot_type = llm_response.get("bot_type")
            queue_name = f"{bot_type}_agent_task"
            
            llm_response["task_allocated_timestamp"] = datetime.now().isoformat()
            
            self.logger.info(f"[TASK ALLOCATOR] Dispatching task to {queue_name}")
            return self.redis_utils.enqueue_task(queue_name, llm_response)
        except Exception as e:
            self.logger.error(f"[TASK ALLOCATOR] Error dispatching task: {str(e)}")
            return False

    def _validate_task(self, task: Dict[str, Any]) -> bool:
        """Validate task data before processing."""
        self.logger.info("[TASK ALLOCATOR] Validating task")
        required_fields = ["task_id", "task_type", "lat", "long", "timestamp"]
        return all(field in task for field in required_fields)

    def process_task(self, payload: Dict[str, Any]) -> bool:
        """Process a single task and allocate it to an appropriate bot."""
        self.logger.info("[TASK ALLOCATOR] Starting task processing")
        # self.logger.debug(f"[TASK ALLOCATOR] Input payload: {json.dumps(payload, indent=4)}")
        
        tasks = payload.get("tasks")
        metadata = payload.get("metadata")
        
        if not isinstance(tasks, list):
            tasks = [tasks]
        
        try:
            for task in tasks:
                if not self._validate_task(task):
                    self.logger.error(f"[TASK ALLOCATOR] Invalid task data: {json.dumps(task, indent=4)}")
                    return False

                self.logger.info(f"[TASK ALLOCATOR] Processing task {task.get('task_id')}")

                payload = self._construct_payload(task)
                self.logger.debug(f"[TASK ALLOCATOR] Constructed payload: {json.dumps(payload, indent=4)}")

                prompt_template = self._get_prompt_template()
                if not prompt_template:
                    self.logger.error("[TASK ALLOCATOR] Failed to get prompt template")
                    return False

                prompt = self._replace_payload_in_prompt(prompt_template, payload)
                if not prompt:
                    self.logger.error("[TASK ALLOCATOR] Failed to prepare prompt")
                    return False

                self.logger.info("[TASK ALLOCATOR] Invoking LLM")
                response = self.llm.invoke(prompt)
                # self.logger.debug(f"[TASK ALLOCATOR] LLM Response: {response.content}")

                try:
                    llm_response = json.loads(response.content)
                    self.logger.info(f"[TASK ALLOCATOR] Parsed LLM response: {json.dumps(llm_response, indent=4)}")
                except json.JSONDecodeError as e:
                    self.logger.error(f"[TASK ALLOCATOR] Error parsing LLM response: {str(e)}")
                    return False

                success = self._dispatch_task(llm_response)
                if success:
                    self.logger.info(f"[TASK ALLOCATOR] Successfully dispatched task {task.get('task_id')}")
                else:
                    self.logger.error(f"[TASK ALLOCATOR] Failed to dispatch task {task.get('task_id')}")

            self.logger.info("[TASK ALLOCATOR] Task processing completed")
            return success

        except Exception as e:
            self.logger.error(f"[TASK ALLOCATOR] Error processing task: {str(e)}")
            return False 