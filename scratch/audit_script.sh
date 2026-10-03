#!/bin/bash
FILES=(
"AGENTS.md"
".agent/rules/anti-hallucination.md"
".agent/rules/domain-fit-gate.md"
".agent/rules/keyword-emphasis.md"
".agent/rules/output-format.md"
".agent/rules/pdf-page-limit.md"
".agent/rules/workflow.md"
"master-profile.md"
"templates/resume-template.md"
"templates/cover-letter-template.md"
)

for f in "${FILES[@]}"; do
    echo "========== STAT & CAT: $f =========="
    if [ -f "$f" ]; then
        stat -c '%y %n' "$f"
        cat -n "$f"
    else
        echo "Не смог прочитать файл $f, команда вернула ошибку: No such file or directory"
    fi
done
