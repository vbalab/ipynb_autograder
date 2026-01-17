import json

from grader.configs.paths import DIR_NOTEBOOK, EnsurePaths
from grader.convert import ProcessJSONToLLMFriendlyText, ProcessRawJupyterToJSON
from grader.structure import DefineTaskStructure

if __name__ == "__main__":
    EnsurePaths()

    ProcessRawJupyterToJSON(DIR_NOTEBOOK / "hw.ipynb", DIR_NOTEBOOK)
    ProcessJSONToLLMFriendlyText(DIR_NOTEBOOK / "hw.json", DIR_NOTEBOOK)

    p = DIR_NOTEBOOK / "hw.txt"
    save = DIR_NOTEBOOK / "hw_task_structure.txt"
    s: str = p.read_text(encoding="utf-8")
    task_structure = DefineTaskStructure(s)
    save.write_text(json.dumps(task_structure, indent=2, sort_keys=True))
