import json
import base64
from pathlib import Path
from typing import Iterable

import nbformat


def _iter_output_text(output: nbformat.NotebookNode) -> Iterable[str]:
    output_type = output.get("output_type")
    if output_type == "stream":
        text = output.get("text", "")
        if text:
            yield str(text)
        return

    if output_type in {"execute_result", "display_data"}:
        data = output.get("data", {})
        if isinstance(data, dict):
            text = data.get("text/plain")
            if text:
                yield str(text)
            json_data = data.get("application/json")
            if json_data:
                yield json.dumps(json_data, indent=2, sort_keys=True)
        return

    if output_type == "error":
        traceback = output.get("traceback", [])
        if traceback:
            yield "\n".join(str(line) for line in traceback)


def _extract_images(
    output: nbformat.NotebookNode,
    output_directory: Path,
    cell_index: int,
    output_index: int,
) -> list[str]:
    saved_paths: list[str] = []
    data = output.get("data", {})
    if not isinstance(data, dict):
        return saved_paths

    for mime_type, extension in (("image/png", "png"), ("image/jpeg", "jpg")):
        payload = data.get(mime_type)
        if not payload:
            continue
        image_bytes = base64.b64decode(payload)
        filename = f"cell_{cell_index:03d}_output_{output_index:02d}.{extension}"
        file_path = output_directory / filename
        file_path.write_bytes(image_bytes)
        saved_paths.append(str(file_path))

    return saved_paths


# TODO: implement (you can change `_iter_output_text` & `_extract_images`)
def process_raw_ipynb(
    ipynb_file_path: str | Path, output_directory_path: str | Path
) -> None:
    """
    The function reads the notebook without executing it,
    creates json consisting of cells' markdown, code, and existing output,
    and writes any embedded images to the output directory.
    """
    ...

if __name__ == "__main__":
    process_raw_ipynb("notebooks/test.ipynb", "notebooks/output")
