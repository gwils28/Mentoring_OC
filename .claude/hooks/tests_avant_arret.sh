#!/usr/bin/env bash
# Stop : « rien n'est fini sans preuve ». Pour chaque projet dont src/ ou tests/ a changé depuis le dernier
# commit (fichiers modifiés ou nouveaux), lance pytest ; si un test échoue, Claude ne peut pas s'arrêter.
input=$(cat)
[[ $(jq -r '.stop_hook_active // false' <<<"$input") == "true" ]] && exit 0
root=$(git -C "${CLAUDE_PROJECT_DIR:-.}" rev-parse --show-toplevel 2>/dev/null) || exit 0
cd "$root" || exit 0

projets=$(git status --porcelain --untracked-files=all -- '*/src/*' '*/tests/*' \
  | sed -E 's/^.{3}//; s#/(src|tests)/.*##' | sort -u)
echecs=""
for p in $projets; do
  [[ -f "$p/pyproject.toml" ]] || continue
  if ! sortie=$(cd "$p" && uv run --quiet pytest -q 2>&1); then
    echecs+=$'\n'"### $p"$'\n'"$(tail -n 25 <<<"$sortie")"
  fi
done

if [[ -n "$echecs" ]]; then
  jq -n --arg r "Des tests échouent dans un projet modifié : corriger avant de terminer.$echecs" \
    '{decision: "block", reason: $r}'
fi
exit 0
