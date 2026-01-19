#!/usr/bin/env bash
# PostToolUse (Write|Edit) : formate avec ruff tout fichier .py modifié, depuis le projet uv qui le contient
# (chaque projet a son pyproject.toml et sa configuration ruff).
f=$(jq -r '.tool_response.filePath // .tool_input.file_path // empty')
[[ "$f" == *.py && -f "$f" ]] || exit 0
dir=$(dirname "$f")
while [[ "$dir" != "/" && ! -f "$dir/pyproject.toml" ]]; do dir=$(dirname "$dir"); done
[[ -f "$dir/pyproject.toml" ]] || exit 0
cd "$dir" && uv run --quiet ruff format --quiet "$f"
