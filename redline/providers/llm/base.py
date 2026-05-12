from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class LLMProvider(ABC):
    @abstractmethod
    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> Dict[str, Any]:
        """
        Generates text based on prompt and system_prompt.
        Returns a dictionary with:
        - raw_text: str
        - parsed_data: Optional[Dict]
        - model_name: str
        - provider_name: str
        - metadata: Dict[str, Any]
        """
        pass
