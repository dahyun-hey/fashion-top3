# 패션 TOP3 앱 - 개발 히스토리

## 프로젝트 개요
무신사, 지그재그의 실시간 인기 TOP3 상품을 크롤링하여 웹에서 보여주는 앱.
GitHub Pages로 배포되어 누구나 접속 가능.

- **공개 URL**: https://dahyun-hey.github.io/fashion-top3/
- **저장소**: https://github.com/dahyun-hey/fashion-top3
- **자동 업데이트**: GitHub Actions로 매일 3회 (09:00, 15:00, 21:00 KST)

---

## 파일 구조

```
fashion-top3/
├── index.html                  # 배포용 HTML (크롤링 데이터 내장, 자동생성)
├── crawl_fashion.py            # 크롤링 스크립트 (실행 시 index.html 재생성)
├── fashion-top3.html           # 초기 버전 HTML (로컬 서버용, 현재 미사용)
├── fashion_data.json           # 크롤링 결과 JSON (로컬 테스트용)
├── 옷 앱.txt                   # 최초 기획 메모
├── .github/
│   └── workflows/
│       └── update.yml          # GitHub Actions 자동 업데이트 워크플로우
```

---

## 개발 진행 순서

### 1단계: 기획 확인
- `옷 앱.txt` 메모 기반으로 요구사항 정리
- 에이블리, 무신사, 지그재그 TOP3 + 가격 + 바로가기 링크 + 썸네일

### 2단계: 정적 HTML 프로토타입 (fashion-top3.html)
- 샘플 데이터로 UI 먼저 구현
- 탭 전환 (전체/에이블리/무신사/지그재그)
- 카드형 레이아웃: 순위 + 썸네일 + 브랜드/상품명 + 할인율/가격 + 바로가기

### 3단계: 크롤링 API 조사
각 플랫폼의 데이터 접근 방법을 조사함.

| 플랫폼 | 방식 | 결과 |
|--------|------|------|
| **무신사** | REST API (`api.musinsa.com/api2/hm/web/v5/pans/ranking`) | 성공 |
| **지그재그** | GraphQL API (`api.zigzag.kr/api/2/graphql`, `GetSearchResult` 쿼리) | 성공 |
| **에이블리** | Selenium, undetected-chromedriver 등 시도 | 실패 (Cloudflare 차단) |

#### 무신사 API 상세
- **엔드포인트**: `https://api.musinsa.com/api2/hm/web/v5/pans/ranking?storeCode=musinsa&subPan=product`
- **방식**: GET 요청, JSON 응답
- **데이터 경로**: `data.modules[]` → `type: "MULTICOLUMN"` → `items[]` → `type: "PRODUCT_COLUMN"`
- **주요 필드**:
  - `info.brandName` - 브랜드명
  - `info.productName` - 상품명
  - `info.finalPrice` - 최종 가격
  - `info.discountRatio` - 할인율
  - `image.url` - 상품 이미지 URL
  - `image.rank` - 순위
  - `id` - 상품 ID (링크 생성용: `musinsa.com/products/{id}`)

#### 지그재그 GraphQL 상세
- **엔드포인트**: `https://api.zigzag.kr/api/2/graphql`
- **방식**: POST, GraphQL 쿼리
- **쿼리**: `GetSearchResult` with `input: { page_id: "best" }`
- **Fragment**: `UxGoodsCardItemPart on UxGoodsCardItem`
- **주요 필드**:
  - `shop_name` - 브랜드(쇼핑몰)명
  - `title` - 상품명
  - `final_price` - 최종 가격
  - `price` - 원래 가격
  - `discount_rate` - 할인율
  - `image_url` - 상품 이미지 URL
  - `catalog_product_id` - 상품 ID (링크: `zigzag.kr/catalog/products/{id}`)
- **참고**: 스키마 introspection은 차단됨. JS 번들에서 쿼리 구조 역분석함.

#### 에이블리 (실패 기록)
- `m.a-bly.com` 전체 403 (Cloudflare 보호)
- `api.a-bly.com` 엔드포인트 추측 시도 → 404
- Selenium headless → "잠시만 기다리십시오..." (Cloudflare challenge)
- undetected-chromedriver → ChromeDriver 버전 불일치로 실패
- **결론**: 앱 전용 플랫폼으로, 웹 크롤링 불가. 모바일 앱 패킷 분석 등 별도 접근 필요.

### 4단계: 크롤링 스크립트 (crawl_fashion.py)
- 무신사 + 지그재그 크롤링
- 크롤링 결과를 HTML에 직접 내장(JSON 인라인)하여 `index.html` 생성
- 별도 서버 없이 정적 파일 하나로 동작

### 5단계: GitHub Pages 배포
- `gh` CLI 설치 및 GitHub 로그인
- `fashion-top3` 저장소 생성 (public)
- GitHub Pages 활성화 (legacy 빌드, master 브랜치)
- **주의**: 최초 Pages 설정 시 `build_type: workflow`로 생성되어 빌드가 안 됨 → Pages 삭제 후 `build_type: legacy`로 재생성하여 해결

### 6단계: 자동 업데이트 (GitHub Actions)
- `.github/workflows/update.yml` 작성
- cron 스케줄: `0 0,6,12 * * *` (UTC) = 한국시간 09:00, 15:00, 21:00
- `workflow_dispatch`로 수동 실행도 가능
- push 시 `workflow` scope 필요 → `gh auth refresh -h github.com -s workflow`로 권한 추가

---

## 로컬 개발 환경

### 필요 패키지
```bash
pip install requests beautifulsoup4 lxml
```

### 로컬에서 크롤링 실행
```bash
cd Desktop/클로드
python crawl_fashion.py
```
→ `index.html`이 최신 데이터로 재생성됨

### 로컬에서 확인
```bash
python -m http.server 8000
# 브라우저에서 http://localhost:8000/index.html 접속
```

### 수동 배포
```bash
git add index.html
git commit -m "데이터 갱신"
git push
```

---

## 향후 개발 가능 사항

1. **에이블리 추가**: 모바일 앱 API 패킷 캡처(mitmproxy 등)로 엔드포인트 확보
2. **다른 플랫폼 추가**: 29CM, W컨셉 등
3. **카테고리 필터**: 상의/하의/신발 등 카테고리별 TOP3
4. **순위 변동 표시**: 이전 순위 대비 상승/하락 표시
5. **알림 기능**: 특정 브랜드/가격대 상품이 TOP3에 진입 시 알림

---

## 트러블슈팅 기록

| 문제 | 원인 | 해결 |
|------|------|------|
| GitHub Pages 404 | Pages가 `workflow` 빌드로 생성되어 빌드 미실행 | Pages 삭제 → `legacy` 모드로 재생성 |
| git push 인증 실패 | gh CLI 인증이 git에 연결 안 됨 | `gh auth setup-git` 실행 |
| workflow push 거부 | OAuth 토큰에 `workflow` scope 없음 | `gh auth refresh -h github.com -s workflow` |
| 지그재그 API 접근 | GraphQL introspection 차단 | JS 번들 파일에서 쿼리 구조 역분석 |
| 에이블리 크롤링 실패 | Cloudflare 보호 + 앱 전용 | 미해결 (향후 과제) |
| Python 출력 깨짐 | cp949 인코딩 문제 | `PYTHONIOENCODING=utf-8` 환경변수 설정 |
