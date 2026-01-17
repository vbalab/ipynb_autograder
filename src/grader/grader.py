import json
from pathlib import Path

from openai import OpenAI
from pydantic import BaseModel, ValidationError
from jinja2 import Template
from typing import List

class Grader:
    def __init__(
        self,
        api_key: str,
        system_prompt_path: str,
        model: str = "deepseek/deepseek-r1-0528:free",
        base_url: str = "https://openrouter.ai/api/v1",
    ):
        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url,
        )
        self.model = model

        prompt_text = Path(system_prompt_path).read_text()
        self.prompt_template = Template(prompt_text)

    def grade(self, task_list_path : List[str], reference_notebook_path: str, input_notebook_path: str):

        
        rendered_prompt = self.prompt_template.render(
            items_to_check=task_list_path.read_text(encoding="utf-8"),
            input_notebook=input_notebook_path.read_text(encoding="utf-8"),
            reference_notebook=reference_notebook_path.read_text(encoding="utf-8")
        )
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": rendered_prompt},
            ],
            temperature=0.0,
        )
        result = response.choices[0].message.content
        
        return json.loads(     result.removeprefix("```json").removesuffix("```").strip() ) ) 
 