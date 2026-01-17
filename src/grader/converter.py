from __future__ import annotations

import base64
import json
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


def convert_friendly_to_llm(
    ipynb_file_path: str | Path, output_directory_path: str | Path
) -> str:
    """Return an LLM-friendly representation of a notebook.

    The function reads the notebook without executing it, collects markdown, code,
    and existing output, and writes any embedded images to the output directory.
    """

    notebook_path = Path(ipynb_file_path)
    output_directory = Path(output_directory_path)
    output_directory.mkdir(parents=True, exist_ok=True)

    notebook = nbformat.read(notebook_path, as_version=4)
    sections: list[str] = []

    for cell_index, cell in enumerate(notebook.cells, start=1):
        if cell.cell_type == "markdown":
            sections.append(f"### Markdown Cell {cell_index}\n")
            sections.append(str(cell.source).strip())
            sections.append("")
            continue

        if cell.cell_type == "code":
            sections.append(f"### Code Cell {cell_index}\n")
            sections.append("```python")
            sections.append(str(cell.source).rstrip())
            sections.append("```")

            outputs = cell.get("outputs", [])
            if outputs:
                sections.append("Output:")

            for output_index, output in enumerate(outputs, start=1):
                image_paths = _extract_images(
                    output,
                    output_directory=output_directory,
                    cell_index=cell_index,
                    output_index=output_index,
                )
                for image_path in image_paths:
                    sections.append(f"[Image saved: {image_path}]")

                for text in _iter_output_text(output):
                    sections.append(text.rstrip())

            sections.append("")
            continue

        sections.append(f"### {cell.cell_type.title()} Cell {cell_index}\n")
        sections.append(str(cell.source).strip())
        sections.append("")

    return "\n".join(section for section in sections if section)


def ConvertFriendlyToLLM(
    ipynb_file_path: str | Path, output_directory_path: str | Path
) -> str:
    """Backward compatible wrapper for convert_friendly_to_llm."""

    return convert_friendly_to_llm(ipynb_file_path, output_directory_path)
