import base64
import json
from collections.abc import Iterable
from pathlib import Path

import nbformat


def _IterOutputText(output: nbformat.NotebookNode) -> Iterable[str]:
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


def _ExtractImages(
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


def ProcessRawJupyterToJSON(
    ipynb_file_path: Path,
    output_directory_path: Path,
) -> None:
    """
    The function reads the notebook without executing it,
    creates json consisting of cells' markdown, code, and existing output,
    and writes any embedded images to the output directory.
    """
    output_directory_path.mkdir(parents=True, exist_ok=True)

    notebook = nbformat.read(ipynb_file_path, as_version=4)
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
                output_texts.extend(_IterOutputText(output))
                output_images.extend(
                    _ExtractImages(
                        output, output_directory_path, cell_index, output_index
                    )
                )
            cell_payload["output_texts"] = output_texts
            cell_payload["output_images"] = output_images

        cells_payload.append(cell_payload)

    json_payload = {
        "source_file": str(ipynb_file_path),
        "cells": cells_payload,
    }

    json_path = output_directory_path / f"{ipynb_file_path.stem}.json"
    json_path.write_text(json.dumps(json_payload, indent=2, sort_keys=True))


def ProcessJSONToLLMFriendlyText(  # noqa: PLR0912, PLR0915
    json_file_path: Path,
    output_directory_path: Path,
) -> None:
    """
    The function converts ProcessRawJupyter JSON into a text format that is easy for LLMs
    to read and analyze. It returns the formatted text and optionally writes it to disk.
    """
    payload = json.loads(json_file_path.read_text())

    cells = payload.get("cells", [])

    lines: list[str] = []
    lines.append(f"Total cells: {len(cells)}")

    for cell in cells:
        cell_index = cell.get("cell_index", "unknown")
        cell_type = cell.get("cell_type", "unknown")
        lines.append("")
        lines.append(f"<----- Cell {cell_index} ({cell_type}) ----->")

        if cell_type == "markdown":
            source = cell.get("source", "")
            if source:
                lines.append("```md")
                lines.append(str(source).rstrip())
                lines.append("```")
            else:
                lines.append("Markdown: <empty>")
            continue

        if cell_type == "code":
            source_code = cell.get("source_code", "")
            lines.append("```py")
            lines.append(str(source_code).rstrip())
            lines.append("```")

            lines.append("")
            output_texts = cell.get("output_texts", [])
            if output_texts:
                lines.append("Outputs:")
                for output_index, output_text in enumerate(output_texts, start=1):
                    lines.append(f"- Output {output_index}:")
                    lines.append("```text")
                    lines.append(str(output_text).rstrip())
                    lines.append("```")
            else:
                lines.append("Outputs: <none>")

            lines.append("")
            output_images = cell.get("output_images", [])
            if output_images:
                lines.append("Output images:")
                for image_path in output_images:
                    lines.append(f"- {image_path}")
            else:
                lines.append("Output images: <none>")
            continue

        source = cell.get("source", "")
        if source:
            lines.append("Content:")
            lines.append("```text")
            lines.append(str(source).rstrip())
            lines.append("```")
        else:
            lines.append("Content: <empty>")

    rendered_text = "\n".join(lines).rstrip() + "\n"

    output_path = Path(output_directory_path / f"{json_file_path.stem}.txt")
    output_path.write_text(rendered_text)
