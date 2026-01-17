from grader.configs.paths import DIR_NOTEBOOK_IPYNB, DIR_NOTEBOOK_PROCESSED, EnsurePaths
from grader.convert import ProcessRawJupyter

if __name__ == "__main__":
    EnsurePaths()

    ProcessRawJupyter(DIR_NOTEBOOK_IPYNB / "test.ipynb", DIR_NOTEBOOK_PROCESSED)
