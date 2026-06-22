# 🎰 LIVE LOTTO DRAW - 2026 스포츠 정보 통합 플랫폼

**실시간 로또 추첨, 월드컵, KBO, 스포츠 정보 및 게시판을 하나의 플랫폼에서 제공하는 통합 웹 애플리케이션입니다.**

## ✨ 주요 기능

### 🎲 로또
- 자동 번호 생성 (1~45번 중 6개)
- 보너스 번호 생성
- 실시간 애니메이션 표시

### ⚽ 2026 FIFA 월드컵
- **12개 그룹 전체 데이터** (48개국)
- 조별 순위 실시간 조회
- 경기 결과 및 일정
- 한국 팀 전용 통계 페이지

### ⚾ KBO 리그
- 실시간 경기 일정 및 결과
- 10초 자동 새로고침
- 경기 상태 표시 (종료/진행중/예정)

### 🏐 V리그 & ⚽ K리그
- 공사 중 페이지 (준비 예정)
- 실시간 알림 신청 기능

### 💬 게시판
- 회원 전용 게시물 작성
- 회원 정보 표시
- 최신 글 우선 표시

### 🔐 회원 관리
- 회원가입 (아이디, 비밀번호, 닉네임)
- 로그인/로그아웃
- 세션 기반 사용자 인증

## 📁 프로젝트 구조

```
lotto-generator/
├── backend/
│   ├── app.py                    # Flask 메인 애플리케이션
│   ├── requirements.txt          # Python 의존성
│   ├── .env                      # 환경 변수 (보안)
│   └── data/
│       ├── users.json            # 사용자 데이터
│       └── posts.json            # 게시물 데이터
├── frontend/
│   ├── index.html                # 🎰 로또 메인 페이지
│   ├── world_cup.html            # ⚽ 월드컵 페이지
│   ├── kbo.html                  # ⚾ KBO 페이지
│   ├── vleague.html              # 🏐 V리그 (공사중)
│   ├── kleague.html              # ⚽ K리그 (공사중)
│   ├── board.html                # 💬 게시판
│   ├── signup.html               # 회원가입
│   ├── login.html                # 로그인
│   ├── css/
│   │   └── style.css             # 전체 스타일시트
│   └── js/
│       └── script.js             # JavaScript 기능
├── Procfile                      # Heroku 배포 설정
├── runtime.txt                   # Python 버전
├── .env.example                  # 환경변수 샘플
├── .gitignore                    # Git 무시 파일
└── README.md                     # 이 파일
```

## 🚀 설치 및 실행

### 1️⃣ 시스템 요구사항
- Python 3.11 이상
- pip 또는 conda

### 2️⃣ 로컬 설치

```bash
# 저장소 클론
git clone <repository-url>
cd lotto-generator

# Python 가상 환경 생성
python -m venv venv

# 가상 환경 활성화
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# 의존성 설치
pip install -r backend/requirements.txt

# 환경 변수 설정
cp backend/.env.example backend/.env
# .env 파일에서 SECRET_KEY 수정 가능

# Flask 앱 실행
cd backend
python app.py
```

### 3️⃣ 브라우저 접속
```
http://localhost:5000
```

## 🌐 배포 (Heroku)

```bash
# Heroku 로그인
heroku login

# Heroku 앱 생성
heroku create your-app-name

# 배포
git push heroku main

# 앱 열기
heroku open
```

또는 다른 클라우드 플랫폼 (AWS, Google Cloud, Azure 등)에 배포할 수 있습니다.

## 🔌 API 엔드포인트

### 월드컵 API
```
GET  /api/world-cup/info                    # 월드컵 기본 정보
GET  /api/world-cup/standings               # 조별 순위
GET  /api/world-cup/standings?group=A       # 특정 조 순위
GET  /api/world-cup/matches                 # 경기 목록
GET  /api/world-cup/team/<팀이름>            # 팀 정보
GET  /api/world-cup/ko-round                # 논코-아웃 라운드
```

### 스포츠 API
```
GET  /api/sports/schedule                   # 전체 스포츠 일정
GET  /api/sports/schedule?league=kbo        # KBO 일정
GET  /api/kbo                               # KBO 경기 상세
```

### 회원 API
```
POST /api/signup                            # 회원가입
POST /api/login                             # 로그인
POST /api/logout                            # 로그아웃
GET  /api/profile                           # 사용자 프로필
```

### 게시판 API
```
GET  /api/posts                             # 게시물 목록
POST /api/posts                             # 게시물 작성
```

## 🎨 기술 스택

### Backend
- **Flask**: 경량 Python 웹 프레임워크
- **Flask-CORS**: 크로스 도메인 요청 처리
- **Requests**: HTTP 라이브러리
- **Gunicorn**: WSGI 애플리케이션 서버

### Frontend
- **HTML5**: 마크업
- **CSS3**: 스타일링 (그래디언트, 애니메이션)
- **JavaScript (ES6+)**: 상호작용 기능
- **Fetch API**: 비동기 HTTP 요청

## 🔒 보안

- 비밀번호 SHA256 해싱
- 세션 기반 인증
- CORS 설정
- 환경 변수로 민감 정보 관리

## 📝 사용 예시

### 1. 월드컵 정보 조회
```javascript
fetch('/api/world-cup/standings?group=A')
  .then(res => res.json())
  .then(data => console.log(data));
```

### 2. 회원가입
```javascript
fetch('/api/signup', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    username: 'user123',
    password: 'SecurePass123',
    nickname: '사용자닉네임'
  })
});
```

### 3. 게시물 작성
```javascript
fetch('/api/posts', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    title: '게시물 제목',
    body: '게시물 내용'
  })
});
```

## 🐛 트러블슈팅

### CORS 에러
- `Flask-CORS` 설정 확인
- 브라우저 개발자 도구에서 응답 헤더 확인

### 포트 충돌
```bash
# 다른 포트로 실행
python app.py --port 8000
```

### 데이터 초기화
```bash
# data 폴더의 JSON 파일 삭제 후 재시작
rm backend/data/*.json
```

## 📊 데이터 구조

### 사용자 데이터 (users.json)
```json
{
  "user123": {
    "password": "hashed_password",
    "nickname": "사용자닉네임"
  }
}
```

### 게시물 데이터 (posts.json)
```json
[
  {
    "id": 1,
    "title": "제목",
    "body": "내용",
    "author": "user123",
    "author_nickname": "닉네임",
    "date": "2026-06-22 10:30"
  }
]
```

## 🚀 향후 계획

- [ ] 데이터베이스 (MySQL/PostgreSQL) 연동
- [ ] OAuth2 소셜 로그인
- [ ] 이메일 인증
- [ ] 파일 업로드 기능
- [ ] 댓글 시스템
- [ ] 좋아요/추천 기능
- [ ] 모바일 앱
- [ ] 실시간 알림 (WebSocket)
- [ ] 통계 및 분석 대시보드

## 📄 라이선스

MIT License - 자유롭게 사용, 수정, 배포 가능

## 👤 기여자

이 프로젝트는 2026년을 기념하여 만들어졌습니다.

## 💬 지원

문제가 발생하거나 질문이 있으면 Issue를 생성해주세요.

---

**🌟 2026 월드컵을 준비하며 만든 최고의 스포츠 정보 플랫폼 🌟**

### 1. 백엔드 설정

```bash
cd backend
pip install -r requirements.txt
python app.py
```

백엔드는 `http://localhost:5000`에서 실행됩니다.

### 2. 프론트엔드 접속

브라우저에서 `http://localhost:5000`으로 접속하세요.

## API 엔드포인트

### 경기 일정 조회
- **URL**: `GET /api/sports/schedule?league=kleague|vleague|kbo`
- **응답**: JSON 배열

### 회원가입
- **URL**: `POST /api/signup`
- **요청**: `{ "username": "test", "password": "password" }`

### 로그인
- **URL**: `POST /api/login`
- **요청**: `{ "username": "test", "password": "password" }`

### 로그아웃
- **URL**: `POST /api/logout`

### 프로필 정보
- **URL**: `GET /api/profile`

### 게시판 조회 및 작성
- **URL**: `GET /api/posts`
- **URL**: `POST /api/posts`
- **요청**: `{ "title": "제목", "body": "내용" }`

## 기술 스택

- **백엔드**: Python Flask, Flask-CORS
- **프론트엔드**: HTML5, CSS3, JavaScript

## 요구사항

- Python 3.7 이상
- Flask
- Flask-CORS

## 라이선스

MIT License
