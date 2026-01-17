import json
import base64
from pathlib import Path
from typing import Iterable

import nbformat


def _iter_output_text(output: nbformat.NotebookNode) -> Iterable[str]:
    output_type = output.get("output_type")
    if output_type == "stream":
        text = output.get("text", "")
        if isinstance(text, list):
            text = "".join(text)
        if text:
            yield str(text)
        return

    if output_type in {"execute_result", "display_data"}:
        data = output.get("data", {})
        if isinstance(data, dict):
            text = data.get("text/plain")
            if isinstance(text, list):
                text = "".join(text)
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
        saved_paths.append(str(file_path.relative_to(output_directory)))

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
    ipynb_path = Path(ipynb_file_path)
    output_directory = Path(output_directory_path)
    output_directory.mkdir(parents=True, exist_ok=True)

    notebook = nbformat.read(ipynb_path, as_version=4)
    cells_payload: list[dict[str, object]] = []

    for cell_index, cell in enumerate(notebook.cells):
        cell_payload: dict[str, object] = {
            "cell_index": cell_index,
            "cell_type": cell.get("cell_type", "unknown"),
        }
        source = cell.get("source", "")
        if cell.get("cell_type") == "code":
            cell_payload["source_code"] = source
        else:
            cell_payload["source"] = source

        if cell.get("cell_type") == "code":
            output_texts: list[str] = []
            output_images: list[str] = []
            outputs = cell.get("outputs", [])
            for output_index, output in enumerate(outputs):
                output_texts.extend(_iter_output_text(output))
                output_images.extend(
                    _extract_images(output, output_directory, cell_index, output_index)
                )
            cell_payload["output_texts"] = output_texts
            cell_payload["output_images"] = output_images

        cells_payload.append(cell_payload)

    json_payload = {
        "source_file": str(ipynb_path),
        "cells": cells_payload,
    }

    json_path = output_directory / f"{ipynb_path.stem}.json"
    json_path.write_text(json.dumps(json_payload, indent=2, sort_keys=True))

if __name__ == "__main__":
    process_raw_ipynb("notebooks/test.ipynb", "notebooks/output")
