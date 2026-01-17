from grader.convert import ProcessRawJupyter
from grader.configs.paths import DIR_NOTEBOOK_IPYNB, DIR_NOTEBOOK_PROCESSED


if __name__ == "__main__":
    ProcessRawJupyter(DIR_NOTEBOOK_IPYNB / "test.ipynb", DIR_NOTEBOOK_PROCESSED)
