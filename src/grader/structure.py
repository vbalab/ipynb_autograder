import json

from openai import OpenAI

from grader.configs.env import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY.get_secret_value())

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


_system_prompt = """You are given the contents of a ground-truth Jupyter notebook solution. Your job is to derive an assessment rubric (task breakdown) based ONLY on what appears in that ground-truth solution.

Output MUST be valid JSON that matches this structure:
{
  "tasks": [
    { "title": string, "description": string, "maximumScore": number }
  ]
}

Rules:
- Create tasks that correspond to distinct parts of the ground-truth notebook task structure.
- If the notebook already defines a grading/points breakdown, mirror it exactly in maximumScore and task boundaries.
- If no grading is provided, assign reasonable maximumScore values and keep them consistent across tasks.
- Do not invent requirements that are not evidenced in the ground-truth notebook.
- Do not include any extra keys besides: title, description, maximumScore.
- Use concise titles and specific, checkable descriptions.
"""


def DefineTaskStructure(ground_truth_notebook_text: str):
    resp = client.responses.create(
        # model="gpt-5",
        model="gpt-5-nano",
        input=[
            {"role": "system", "content": _system_prompt},
            {"role": "user", "content": ground_truth_notebook_text},
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

    task_structure = json.loads(resp.output_text)

    return task_structure
