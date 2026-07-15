#!/usr/bin/env bash
# commit_log.md를 현재 git 상태 기준으로 통째로 재생성한다.
# 실행: bash scripts/update-commit-log.sh
# - 커밋 시 .githooks/post-commit 훅이 자동 호출한다.
# - client-side git에는 post-push 훅이 없으므로, push 직후에는 반드시 이 스크립트를
#   한 번 더 수동 실행해 pushed 상태를 최신화해야 한다.
# - 원격 상태는 마지막 fetch 기준으로 판단한다. 최신 원격 상태를 반영하려면
#   이 스크립트 실행 전에 `git fetch`를 먼저 실행할 것.

set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

BRANCH=$(git rev-parse --abbrev-ref HEAD)
REMOTE_REF="origin/${BRANCH}"
HAS_REMOTE=1
git rev-parse --verify "$REMOTE_REF" >/dev/null 2>&1 || HAS_REMOTE=0

TMP_FILE=$(mktemp)

{
  echo "# Commit Log"
  echo ""
  echo "> 이 파일은 \`scripts/update-commit-log.sh\`가 자동 생성합니다. 직접 수정하지 마세요."
  echo "> 커밋 시 \`.githooks/post-commit\` 훅이 자동 갱신합니다. **push 직후에는 pushed 상태 반영을"
  echo "> 위해 \`bash scripts/update-commit-log.sh\`를 한 번 더 실행하세요.**"
  echo "> pushed 여부는 이 스크립트가 마지막으로 실행된 시점 기준 \`${REMOTE_REF}\`로 판단합니다 —"
  echo "> 최신 원격 상태를 반영하려면 실행 전에 \`git fetch\`를 먼저 실행하세요."
  echo ""
  echo "생성 시각: $(date '+%Y-%m-%d %H:%M:%S')"
  echo "브랜치: \`${BRANCH}\`"
  if [ "$HAS_REMOTE" -eq 0 ]; then
    echo ""
    echo "> ⚠️ \`${REMOTE_REF}\`를 찾을 수 없습니다 — 원격 추적 브랜치가 없거나 아직 fetch되지"
    echo "> 않았습니다. 모든 커밋이 미push로 표시됩니다."
  fi
  echo ""
  echo "| 날짜 | 커밋 | 메시지 | GitHub Push |"
  echo "|---|---|---|---|"
} > "$TMP_FILE"

git log --pretty=tformat:'%H%x09%ad%x09%s' --date=format:'%Y-%m-%d %H:%M' | \
while IFS=$'\t' read -r hash date subject; do
  pushed="❌"
  if [ "$HAS_REMOTE" -eq 1 ] && git merge-base --is-ancestor "$hash" "$REMOTE_REF" 2>/dev/null; then
    pushed="✅"
  fi
  short="${hash:0:7}"
  # 메시지 안의 파이프(|)가 표를 깨지 않도록 이스케이프
  safe_subject=$(printf '%s' "$subject" | sed 's/|/\\|/g')
  echo "| $date | \`$short\` | $safe_subject | $pushed |" >> "$TMP_FILE"
done

mv "$TMP_FILE" commit_log.md
echo "commit_log.md 갱신 완료 (브랜치: ${BRANCH}, 원격: ${REMOTE_REF} $([ "$HAS_REMOTE" -eq 1 ] && echo 발견 || echo 없음))"
