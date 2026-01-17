import json

from grader.configs.paths import DIR_NOTEBOOK, DIR_PROMPTS, EnsurePaths
from grader.convert import ProcessJSONToLLMFriendlyText, ProcessRawJupyterToJSON
from grader.structure import DefineTaskStructure

if __name__ == "__main__":
    EnsurePaths()

    ProcessRawJupyterToJSON(DIR_NOTEBOOK / "reference.ipynb", DIR_NOTEBOOK)
    ProcessJSONToLLMFriendlyText(DIR_NOTEBOOK / "reference.json", DIR_NOTEBOOK)
    
    ProcessRawJupyterToJSON(DIR_NOTEBOOK / "student.ipynb", DIR_NOTEBOOK)
    ProcessJSONToLLMFriendlyText(DIR_NOTEBOOK / "student.json", DIR_NOTEBOOK)
    
    p = DIR_NOTEBOOK / "reference.txt"
    save = DIR_NOTEBOOK / "structure.txt"
    
    s: str = p.read_text(encoding="utf-8")
    task_structure = DefineTaskStructure(s)
    save.write_text(json.dumps(task_structure, indent=2, sort_keys=True))

    grader = Grader(os.getenv('OPENAI_API_KEY'), DIR_PROMPTS / 'grader.md')
    grading_json = grade.grade(DIR_NOTEBOOK / "structure.txt", DIR_NOTEBOOK / "reference.txt", DIR_NOTEBOOK / "student.txt")
    
    save = DIR_NOTEBOOK / "result.txt"
    save.write_text(json.dumps(task_structure, indent=2, sort_keys=True))