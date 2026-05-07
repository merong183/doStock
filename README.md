# doStock — 주식 종목 추천 앱

Next.js 14 프론트엔드와 FastAPI 백엔드로 구성된 모노레포입니다. 현재 API는 더미 데이터를 반환하며, PostgreSQL 스키마와 Alembic 마이그레이션 구조만 준비되어 있습니다.

## 사전 요구 사항

- Node.js 18+
- Python 3.10+
- Docker (로컬 PostgreSQL용)

## 1. PostgreSQL 실행

저장소 루트에서:

```bash
docker compose up -d
```

기본 접속 정보는 `docker-compose.yml`과 동일하게 맞춰 두었습니다 (`postgres` / `postgres`, DB 이름 `dostock`).

## 2. 백엔드 (FastAPI)

```bash
cd backend
python -m venv .venv
```

Windows PowerShell에서 가상환경 활성화:

```powershell
.\.venv\Scripts\Activate.ps1
```

패키지 설치 및 서버 실행:

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- API 문서: http://localhost:8000/docs  
- 헬스 체크: http://localhost:8000/health  

환경 변수는 `backend/.env`에서 설정합니다.

- `DATABASE_URL` — 예: `postgresql+asyncpg://postgres:postgres@localhost:5432/dostock`
- `ANTHROPIC_API_KEY` — 추후 AI 분석용
- `SERPER_API_KEY` — 추후 뉴스 검색용

DB 테이블 생성은 Postgres가 띄워진 뒤 Alembic으로 진행할 수 있습니다.

```bash
cd backend
alembic revision --autogenerate -m "init"
alembic upgrade head
```

## 3. 프론트엔드 (Next.js 14)

```bash
cd frontend
npm install
npm run dev
```

브라우저에서 http://localhost:3000 을 엽니다.

API 베이스 URL은 `frontend/.env.local`의 `NEXT_PUBLIC_API_URL`로 지정합니다 (기본값 개발 시 `http://localhost:8000`).

## 프로젝트 구조

```
frontend/     Next.js App Router, Tailwind
backend/      FastAPI, SQLAlchemy(async), Alembic
docker-compose.yml   로컬 PostgreSQL
```

## API 엔드포인트 (스켈레톤)

| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET | `/api/recommendations/today` | 오늘 추천 |
| GET | `/api/recommendations/history` | 추천 히스토리 |
| GET | `/api/stocks/{ticker}/news` | 종목 뉴스 |
| POST | `/api/scheduler/run` | 수동 트리거 (개발용) |

---

## 호스팅 (권장 조합)

에이전트가 사용자 계정에 직접 배포할 수는 없습니다. 아래는 **프론트 Vercel + API Render** 같은 무료/저비용 조합 예시입니다. DB는 Render PostgreSQL, Neon, Supabase 등 관리형 Postgres의 연결 문자열을 `DATABASE_URL`에 넣으면 됩니다 (`postgresql+asyncpg://...` 형식 유지).

### 백엔드 (Docker)

- `backend/Dockerfile`로 이미지 빌드 후 컨테이너에서 `uvicorn` 실행합니다.
- 로컬 확인: 빌드 컨텍스트는 **`backend`** 폴더여야 합니다.

저장소 루트에서:

```bash
docker build -t dostock-api -f backend/Dockerfile backend
docker run --rm -p 8000:8000 -e CORS_ORIGINS=https://YOUR_VERCEL_APP.vercel.app dostock-api
```

Windows PowerShell에서는 **`Docker Desktop`을 켠 뒤** 다음도 사용할 수 있습니다.

```powershell
.\scripts\build-backend-docker.ps1
```

**참고:** IDE나 CI 에이전트 셸에는 `docker`가 PATH에 없을 수 있습니다. 그 경우 로컬 터미널에서 실행하거나, Docker Desktop 설정에서 CLI 경로가 잡혀 있는지 확인하세요 (설치 후 터미널을 한 번 닫았다가 다시 열기).

- 루트의 `render.yaml`은 [Render Blueprint](https://render.com/docs/blueprint-spec) 예시입니다. Render에서 Git 저장소를 연결한 뒤 Blueprint로 추가하면 웹 서비스가 생성됩니다. 대시보드에서 **`CORS_ORIGINS`**(프론트 배포 URL), **`DATABASE_URL`** 등을 설정하세요.

### 프론트엔드 (Vercel)

저장소에는 `frontend/vercel.json`(기본 리전 `icn1`, 서울)과 선택 사항으로 GitHub Actions 워크플로(`.github/workflows/deploy-frontend-vercel.yml`)가 포함되어 있습니다.

**방법 A — 대시보드 (가장 단순)**

1. 코드가 있는 저장소를 GitHub 등에 푸시합니다.
2. [Vercel](https://vercel.com) → **Add New… → Project** → 저장소 Import.
3. **Root Directory**를 **`frontend`** 로 설정합니다 (모노레포 필수).
4. **Environment Variables**에 **`NEXT_PUBLIC_API_URL`** = 배포된 API 주소 (예: `https://dostock-api.onrender.com`, 끝 슬래시 없음).
5. **Deploy** 후 발급되는 URL(예: `https://프로젝트.vercel.app`)을 백엔드 **`CORS_ORIGINS`** 에 추가합니다.

**방법 B — Vercel CLI (로컬에서 한 번 로그인 후)**

```bash
cd frontend
npx vercel login
npx vercel        # 프리뷰
npx vercel --prod # 프로덕션
```

**방법 B′ — 토큰만으로 비대화형 배포 (CI와 동일)**

[토큰](https://vercel.com/account/tokens)과 프로젝트 **Settings → General**의 Organization ID / Project ID를 받은 뒤 PowerShell에서:

```powershell
$env:VERCEL_TOKEN = "…"
$env:VERCEL_ORG_ID = "…"
$env:VERCEL_PROJECT_ID = "…"
.\scripts\deploy-vercel.ps1
```

처음에는 브라우저에서 프로젝트/팀을 연결하라는 안내가 나올 수 있습니다. 이후에도 **`NEXT_PUBLIC_API_URL`** 은 Vercel 대시보드 프로젝트 Settings → Environment Variables에서 설정하세요.

**방법 C — GitHub Actions 자동 배포**

1. Vercel에서 프로젝트를 만든 뒤 **Settings → General**에서 **Organization ID**, **Project ID**를 복사합니다.
2. **Account → Tokens**에서 배포용 토큰을 만듭니다.
3. GitHub 저장소 → **Settings → Secrets and variables → Actions**에 다음을 등록합니다: `VERCEL_TOKEN`, `VERCEL_ORG_ID`, `VERCEL_PROJECT_ID`.
4. `main`(또는 `master`)에 `frontend/` 변경을 푸시하면 워크플로가 프로덕션 배포를 실행합니다.

### CORS

백엔드는 기본으로 `localhost:3000`을 허용하고, 프로덕션 프론트 도메인은 환경 변수 **`CORS_ORIGINS`** 에 쉼표로 나열합니다 (예: `https://xxx.vercel.app`).

### 마이그레이션

관리형 Postgres를 쓰는 경우, 로컬 또는 CI에서 `DATABASE_URL`을 프로덕션 값으로 두고 `alembic upgrade head`를 한 번 실행하면 됩니다 (운영 DB에 직접 접근 가능한 환경에서만 실행할 것).
