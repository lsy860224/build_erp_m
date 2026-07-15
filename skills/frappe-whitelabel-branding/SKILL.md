---
name: frappe-whitelabel-branding
description: ERPNext를 화이트라벨링(리브랜딩)할 때 사용. GPL v3 준수 범위, 상표 제한, 브랜딩 적용 방법, 메뉴명 한글화 방법을 다룬다.
---

# ERPNext 화이트라벨링 — 라이선스와 방법

## GPL v3 하에서 허용되는 것 / 금지되는 것

| 행위 | 허용 여부 |
|---|---|
| 코드 수정 (사내 비공개 사용) | ✅ 완전 허용, 소스 공개 의무 없음 |
| 로고/색상/이름 변경 (화이트라벨링) | ✅ 허용 |
| "ERPNext" 이름/로고를 자체 제품명·도메인에 사용 | ❌ 금지 (Frappe Technologies 상표) |
| 저작권 고지 완전 삭제 | ❌ 금지 (GPL v3 필수 유지 사항) |
| 사내 전용으로 웹 서비스처럼 운영(배포 아님) | ✅ 소스 공개 의무 없음 (AGPL 아닌 GPL이므로) |
| 제3자(타사)에게 커스텀 빌드를 넘기는 것 | ⚠️ "배포"로 간주되어 GPL 조건(소스 요청 시 제공 등) 적용 가능 — 법률 확인 권장 |

## 브랜딩 적용 3단계

### 1. hooks.py — 앱 정체성

```python
app_name = "babipa_erp"
app_title = "BABIPA MES"           # Desk 좌측 상단, 브라우저 탭 제목
app_logo_url = "/assets/babipa_erp/images/logo.png"
```

### 2. CSS — 색상/폰트

```css
/* public/css/theme.css */
:root { --primary-color: #1a3c6e; }
.navbar-brand img { max-height: 28px; }
```
`hooks.py`에 `app_include_css = "/assets/babipa_erp/css/theme.css"` 등록.

### 3. Translation — 메뉴/필드 라벨 한글화

DocType/필드의 내부 스키마 이름(fieldname)은 절대 바꾸지 않는다. 화면에 보이는
라벨만 Translation으로 교체한다.

```csv
Sales Order,수주
Purchase Order,발주
Quality Inspection,품질검사
Item,품목
```

```bash
bench --site erp.internal import-translations babipa_erp/translations/ko.csv
```

## 왜 스키마 리네임을 하면 안 되는가

Frappe에 "Rename DocType" 기능이 있지만:
- 표준 리포트/API가 원래 이름을 참조하는 경우가 많아 깨짐
- 향후 ERPNext 코어 업데이트 시 원래 이름 기준으로 패치가 들어오므로 충돌
→ **라벨(Translation)만 바꾸고 스키마 이름은 유지**하는 것이 유일한 안전한 방법.

## 체크리스트

- [ ] "ERPNext"가 신규 제품명/도메인에 없는가?
- [ ] 저작권 고지가 완전히 삭제되지 않았는가? (완전 삭제보다 footer에 최소 표기 권장)
- [ ] DocType/필드 스키마 이름은 그대로 두었는가?
- [ ] 브랜딩 변경이 코어 파일이 아니라 Custom App 안에서만 이루어졌는가?
