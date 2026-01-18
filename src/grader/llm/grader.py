import json
from pathlib import Path

from openai import OpenAI
from jinja2 import Template
from grader.core.configs.settings import settings
from typing import Any

import markdown
from weasyprint import HTML
from grader.core.configs.paths import PATH_GRADER_PROMPT
from grader.llm.convert import ProcessRawJupyterToJSON, ProcessJSONToLLMFriendlyText
from grader.llm.filenames import Filenames

class Grader:
    def __init__(self):
        self._client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=settings.OPENROUTER_API_KEY.get_secret_value(),
        )
        self._model = "deepseek/deepseek-v3.2"

        self._system_prompt = Template(PATH_GRADER_PROMPT.read_text())

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
                        "description": "Potential score awarded for this task.",
                    },
                    "comment": {
                        "type": "string",
                        "minLength": 1,
                        "description": "Explanation of places which requre doublechecking.",
                    },
                },
                "required": ["score", "comment"],
                "additionalProperties": False,
            },
        }

    def grade(
        self,
        task_list_path: list[str],
        reference_notebook_path: str,
        input_notebook_path: str,
    ) -> None:
        resp = self._client.responses.create(
            model=self._model,
            input=[
                {
                    "role": "system",
                    "content": self._system_prompt.render(
                        items_to_check=task_list_path.read_text(encoding="utf-8"),
                        input_notebook=input_notebook_path.read_text(encoding="utf-8"),
                        reference_notebook=reference_notebook_path.read_text(
                            encoding="utf-8"
                        ),
                    ),
                },
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

        save = input_notebook_path.parent / "result.txt"
        save.write_text(json.dumps(diff_json, indent=2, sort_keys=True))

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

        tasks_data: dict[str, Any] = json.loads(tasks_path.read_text(encoding="utf-8"))
        results_data: dict[str, Any] = json.loads(
            results_path.read_text(encoding="utf-8")
        )

        md_lines = ["# Отчет по проверке\n"]

        for task in tasks_data["tasks"]:
            title = task["title"]
            description = task["description"]
            max_score = task["maximumScore"]

            result = results_data.get(title, {})
            comment = result.get("comment", "Комментарий отсутствует.")
            score = result.get("score", 0)

            md_lines.extend(
                [
                    f"## {title}\n",
                    f"**Условие:**  \n{description}\n",
                    f"**Комментарий по проверке:**  \n{comment}\n",
                    f"**Потенциальный балл:** {score} / {max_score}\n",
                ]
            )

        md_lines.append("\n## Сводная таблица баллов\n")
        md_lines.append("| Задача | Балл | Максимум |")
        md_lines.append("|-------|------|----------|")

        for task in tasks_data["tasks"]:
            title = task["title"]
            max_score = task["maximumScore"]
            score = results_data.get(title, {}).get("score", 0)

            md_lines.append(f"| {title} | {score} | {max_score} |")

        # output_md_path.write_text("\n".join(md_lines), encoding="utf-8")

        # Преобразуем MD в HTML
        html_text = markdown.markdown(
            "\n".join(md_lines), extensions=["tables", "fenced_code"]
        )

        # Генерируем PDF
        HTML(string=html_text).write_pdf(pdf_path)

def GradeInputNotebook(directory_path):
    reference_path = directory_path / "reference"
    student_path = directory_path / "student"

    ProcessRawJupyterToJSON(student_path)
    ProcessJSONToLLMFriendlyText(student_path)

    grader = Grader()
    grader.grade(task_list_path=reference_path / Filenames.task_structure.value, reference_notebook_path=reference_path / Filenames.llm_friendly.value, input_notebook_path= student_path / Filenames.llm_friendly.value,)
    grader.generate_md_report(tasks_path=reference_path / Filenames.task_structure.value, results_path=student_path / "result.txt", pdf_path=student_path / "result.pdf")
