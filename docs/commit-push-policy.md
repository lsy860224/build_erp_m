# 커밋 로그 & 커밋/Push 필수 규칙

`CLAUDE.md` 절대 원칙 #7("빌드 트리거 발생 시 commit+push 필수")의 상세 버전.

## 커밋 로그 (`commit_log.md`) 메커니즘

이 저장소는 루트의 `commit_log.md`로 로컬 커밋의 GitHub push 여부를 추적한다.

- 커밋 시 `.githooks/post-commit` 훅이 `scripts/update-commit-log.sh`를 자동 호출해 갱신한다.
- **push 직후에는 반드시 `bash scripts/update-commit-log.sh`를 한 번 더 실행**해 pushed
  상태를 최신화한다 — client-side git에는 post-push 훅이 없어 자동화가 불가능하다.
- 최초 clone 시 `git config core.hooksPath .githooks`를 1회 실행해야 훅이 활성화된다.
- 최신 원격 상태를 반영하려면 스크립트 실행 전에 `git fetch`를 먼저 실행한다.

## 빌드 로그 (`docs/build-log.md`)

정식 빌드(`bench new-app babipa_erp` 이후 실제 인스턴스 조작) 시작 시점부터, 되돌리기
어렵거나 여러 사람에게 영향을 주는 시스템 상태 변경은 반드시 `docs/build-log.md`에
기록한다. 무엇이 기록 대상인지, 형식은 어떤지는 그 파일 자체가 스펙을 겸한다.

## 커밋/Push 필수 규칙

`docs/build-log.md`의 기록 대상 트리거(bench new-app/get-app/install-app/uninstall-app,
migrate, DocType/Custom Field/fixture 변경, 배포·재기동, backup 등 시스템 상태를
변경하는 작업)가 발생하면, 작업을 완료하고 검증한 뒤 **반드시 git commit + GitHub push까지
수행한다** — 별도로 사용자 확인을 기다리지 않는다(`CLAUDE.md` 자체가 사전 승인이다).

### 절차

1. 변경사항을 커밋한다. 커밋 메시지에 무엇을·왜 변경했는지 명확히 남긴다.
2. `docs/build-log.md`에 해당 작업을 기록한다(별도 커밋이어도, 같은 커밋에 포함해도 무방).
3. `origin`에 push한다.
4. `bash scripts/update-commit-log.sh`를 실행해 `commit_log.md`의 pushed 상태를 갱신하고,
   그 결과도 커밋해 둔다.

### 예외 — 아래는 사전 승인 대상이 아니며, 항상 먼저 사용자에게 확인한다

- `git push --force`류 강제 push, `main` 브랜치 히스토리 재작성(rebase -i, reset --hard 후
  강제 push 등)
- 제3자(AU Co. 등)에게 소스/빌드를 넘기는 배포 — `docs/gplv3-compliance.md`의 제3자 배포
  조항이 발동하는 지점이므로 실제 조치 전 반드시 확인
- 되돌리기 어려운 파괴적 작업(`bench drop-site`, DB 강제 초기화 등 — `.claude/settings.json`에
  이미 deny 처리된 것들)
