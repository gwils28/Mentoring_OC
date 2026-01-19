#!/usr/bin/env bash
# PreToolUse (Write|Edit|NotebookEdit) : data/raw/ est immuable. Les données brutes sont téléchargées
# et vérifiées par SHA-256 par le code du projet ; on ne les modifie jamais à la main.
f=$(jq -r '.tool_input.file_path // .tool_input.notebook_path // empty')
case "$f" in
  */data/raw/*)
    jq -n --arg f "$f" '{hookSpecificOutput: {hookEventName: "PreToolUse", permissionDecision: "deny",
      permissionDecisionReason: ("data/raw/ est immuable (" + $f + "). Écrire les sorties dans data/processed/, ou modifier le code de téléchargement dans src/<package>/io.py.")}}'
    ;;
esac
exit 0
