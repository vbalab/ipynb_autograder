import json
from pathlib import Path

from openai import OpenAI
from pydantic import BaseModel, ValidationError
from jinja2 import Template
from typing import List
from configs.env import settings

from typing import Dict, Any


import markdown
from weasyprint import HTML

class Grader:
    def __init__(
        self,
        system_prompt_path: str,
#       output_schema_path: str
    ):
        self._client = OpenAI(api_key=settings.OPENAI_API_KEY.get_secret_value())
        prompt_text = Path(system_prompt_path).read_text()
        self._system_prompt = Template(prompt_text)
        self._output_schema = {
    "type": "object",
    "description": "Top-level object keyed by task titles.",
    "properties": {},  # REQUIRED by OpenAI
    "additionalProperties": {
        "type": "object",
        "description": "Evaluation result for a single task.",
        "properties": {
            "score": {
                "type": "number",
                "minimum": 0,
                "description": "Potential score awarded for this task."
            },
            "comment": {
                "type": "string",
                "minLength": 1,
                "description": "Explanation of places which requre doublechecking."
            }
        },
        "required": ["score", "comment"],
        "additionalProperties": False
    }
}


    def grade(self, task_list_path : List[str], reference_notebook_path: str, input_notebook_path: str):
        resp = self._client.responses.create(
            model="gpt-5-nano",
            input=[
                {"role": "system", "content": self._system_prompt.render(            items_to_check=task_list_path.read_text(encoding="utf-8"),
            input_notebook=input_notebook_path.read_text(encoding="utf-8"),
            reference_notebook=reference_notebook_path.read_text(encoding="utf-8"))},
            #    {"role": "user", "content": ground_truth_notebook_text},
            ],
            text={
                "format": {
                    "type": "json_schema",
                    "name": "task_structure",
                    "strict": True,
                    "schema": self._output_schema,
                }
            },
        )

        diff_json = json.loads(resp.output_text)

        return diff_json
 
    def generate_md_report(
        self,
        tasks_path: Path,
        results_path: Path,
        pdf_path: str,
    ) -> None:
        """
        Algorithmically generate markdown report and score table
        from task descriptions and grading results.
        """

        tasks_data: Dict[str, Any] = json.loads(tasks_path.read_text(encoding="utf-8"))
        results_data: Dict[str, Any] = json.loads(results_path.read_text(encoding="utf-8"))

        md_lines = ["# Отчет по проверке\n"]

        for task in tasks_data["tasks"]:
            title = task["title"]
            description = task["description"]
            max_score = task["maximumScore"]

            result = results_data.get(title, {})
            comment = result.get("comment", "Комментарий отсутствует.")
            score = result.get("score", 0)

            md_lines.extend([
                f"## {title}\n",
                f"**Условие:**  \n{description}\n",
                f"**Комментарий по проверке:**  \n{comment}\n",
                f"**Потенциальный балл:** {score} / {max_score}\n",
            ])

        md_lines.append("\n## Сводная таблица баллов\n")
        md_lines.append("| Задача | Балл | Максимум |")
        md_lines.append("|-------|------|----------|")

        for task in tasks_data["tasks"]:
            title = task["title"]
            max_score = task["maximumScore"]
            score = results_data.get(title, {}).get("score", 0)

            md_lines.append(f"| {title} | {score} | {max_score} |")

        #output_md_path.write_text("\n".join(md_lines), encoding="utf-8")

        # Преобразуем MD в HTML
        html_text = markdown.markdown("\n".join(md_lines), extensions=['tables', 'fenced_code'])

        # Генерируем PDF
        HTML(string=html_text).write_pdf(pdf_path)