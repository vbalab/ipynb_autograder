from grader.configs.paths import DIR_NOTEBOOK_IPYNB, DIR_NOTEBOOK_PROCESSED, EnsurePaths
from grader.convert import ProcessRawJupyterToJSON

if __name__ == "__main__":
    EnsurePaths()

    ProcessRawJupyterToJSON(DIR_NOTEBOOK_IPYNB / "test.ipynb", DIR_NOTEBOOK_PROCESSED)
