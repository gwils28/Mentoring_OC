#!/usr/bin/env bash
# Stop : « rien n'est fini sans preuve ». Pour chaque projet dont src/ ou tests/ a changé depuis le dernier
# commit (fichiers modifiés ou nouveaux), lance pytest ; si un test échoue, Claude ne peut pas s'arrêter.
input=$(cat)
[[ $(jq -r '.stop_hook_active // false' <<<"$input") == "true" ]] && exit 0
root=$(git -C "${CLAUDE_PROJECT_DIR:-.}" rev-parse --show-toplevel 2>/dev/null) || exit 0
cd "$root" || exit 0

# -z : entrées « XY chemin » séparées par NUL, chemins jamais entre guillemets (accents, espaces sûrs).
# Un renommage ou une copie (R, C) ajoute une entrée : l'ancien chemin, qu'on lit et ignore.
declare -A projets=()
while IFS= read -r -d '' entree; do
  etat=${entree:0:2} chemin=${entree:3}
  [[ "$etat" == *[RC]* ]] && IFS= read -r -d '' _ancien
  # projet = tout ce qui précède le premier /src/ ou /tests/
  projet=${chemin%%/src/*}
  autre=${chemin%%/tests/*}
  (( ${#autre} < ${#projet} )) && projet=$autre
  [[ "$projet" != "$chemin" ]] && projets["$projet"]=1
done < <(git -c core.quotePath=false status --porcelain -z --untracked-files=all -- '*/src/*' '*/tests/*')

echecs=""
for p in "${!projets[@]}"; do
  [[ -f "$p/pyproject.toml" ]] || continue
  sortie=$(cd "$p" && uv run --quiet pytest -q 2>&1)
  code=$?
  # 5 = aucun test collecté (projet tout juste initialisé) : rien à prouver, pas un échec
  if (( code != 0 && code != 5 )); then
    echecs+=$'\n'"### $p"$'\n'"$(tail -n 25 <<<"$sortie")"
  fi
done

if [[ -n "$echecs" ]]; then
  jq -n --arg r "Des tests échouent dans un projet modifié : corriger avant de terminer.$echecs" \
    '{decision: "block", reason: $r}'
fi
exit 0
