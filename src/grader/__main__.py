from grader.configs.paths import DIR_NOTEBOOK, EnsurePaths
from grader.convert import ProcessJSONToLLMFriendly, ProcessRawJupyterToJSON

if __name__ == "__main__":
    EnsurePaths()

    ProcessRawJupyterToJSON(DIR_NOTEBOOK / "test.ipynb", DIR_NOTEBOOK)
    ProcessJSONToLLMFriendly(DIR_NOTEBOOK / "test.json", DIR_NOTEBOOK)
