---
description: frappe-devops 에이전트를 호출해 폐쇄망(인트라넷 전용) Docker 배포 스크립트와 백업 체계를 생성한다
---

배포 환경 정보: $ARGUMENTS (예: 서버 사양, 인터넷 접근 가능한 스테이징 PC 유무, 사내 DNS 여부)

1. frappe-devops 에이전트에게 위임하여 다음을 순서대로 생성한다:
   - 인터넷 되는 PC에서 실행할 이미지 pull/save 스크립트
   - 사내망(폐쇄망) 서버에서 실행할 load/compose up 스크립트
   - `docker-compose.yml` (ERPNext + MariaDB + Redis + Custom App 마운트 포함)
2. 서버 규모에 맞는 하드웨어 사양 표를 함께 제시한다 (사용자가 입력한 예상 사용자 수 기준).
3. 사내 DNS/hosts 등록 및 자체서명 인증서 발급 절차를 포함한다.
4. 로컬/NAS 백업 crontab 스크립트와 분기별 복구 테스트 체크리스트를 포함한다.
5. 업데이트 정책(주기, 스테이징 검증 후 반입 절차)을 명시한다.
