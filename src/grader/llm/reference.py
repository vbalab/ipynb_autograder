from pathlib import Path

from openai import OpenAI

from grader.core.configs.paths import PATH_STRUCTURE_PROMPT
from grader.core.configs.settings import settings
from grader.llm.convert import ProcessJSONToLLMFriendlyText, ProcessRawJupyterToJSON
from grader.llm.filenames import Filenames

_schema = {
    "type": "object",
    "properties": {
        "tasks": {
            "type": "array",
            "minItems": 1,
            "items": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "minLength": 1,
                        "description": "Short task name.",
                    },
                    "description": {
                        "type": "string",
                        "minLength": 1,
                        "description": "What the student needs to do for this task, derived from the ground-truth notebook.",
                    },
                    "maximumScore": {
                        "type": "number",
                        "minimum": 0,
                        "description": "Max score available for this task. Use notebook's grading if present; otherwise assign a reasonable max.",
                    },
                },
                "required": ["title", "description", "maximumScore"],
                "additionalProperties": False,
            },
        }
    },
    "required": ["tasks"],
    "additionalProperties": False,
}


_structure_system_prompt = PATH_STRUCTURE_PROMPT.read_text()


def DefineReferenceTaskStructure(
    client: OpenAI,
    model: str,
    directory_path: Path,
) -> None:
    llm_friendly_ipynb_path = directory_path / Filenames.llm_friendly.value
    llm_friendly_ipynb = llm_friendly_ipynb_path.read_text()

    resp = client.responses.create(
        # model="gpt-5",
        # model="gpt-5-nano",
        model=model,
        input=[
            {"role": "system", "content": _structure_system_prompt},
            {"role": "user", "content": llm_friendly_ipynb},
        ],
        text={
            "format": {
                "type": "json_schema",
                "name": "task_structure",
                "strict": True,
                "schema": _schema,
            }
        },
    )

    task_structure_path = directory_path / Filenames.task_structure.value
    task_structure_path.write_text(resp.output_text)


def ProcessReference(
    directory_path: Path,
) -> None:
    ProcessRawJupyterToJSON(directory_path)
    ProcessJSONToLLMFriendlyText(directory_path)

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=settings.OPENROUTER_API_KEY.get_secret_value(),
    )
    # model = "gpt-5-nano"
    model = "deepseek/deepseek-v3.2"
    DefineReferenceTaskStructure(client, model, directory_path)
