import os
import json
import random
import logging
import hashlib
from datetime import datetime
from flask import Flask, jsonify, render_template, request, session, redirect, url_for, abort
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup

# ==========================================
# 1. 애플리케이션 초기화 및 설정
# ==========================================
app = Flask(
    __name__, 
    static_folder='../frontend', 
    static_url_path='', 
    template_folder='../frontend'
)
CORS(app)

# 세션 및 보안을 위한 시크릿 키 설정
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-12345678')

# 로깅 설정
logging.basicConfig(level=logging.INFO)

# 파일 데이터 저장 경로 설정
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
USERS_FILE = os.path.join(DATA_DIR, 'users.json')
POSTS_FILE = os.path.join(DATA_DIR, 'posts.json')

# 로또 상수
LOTTO_MIN = 1
LOTTO_MAX = 45
LOTTO_COUNT = 6

# 스포츠 일정/결과 모의 데이터 (Mock Data)
SPORT_SCHEDULES = {
    'kleague': [
        {'date': '2026-05-30', 'home': '울산 현대', 'away': '전북 현대', 'time': '19:00'},
        {'date': '2026-05-31', 'home': 'FC 서울', 'away': '수원 삼성', 'time': '19:30'},
        {'date': '2026-06-01', 'home': '포항 스틸러스', 'away': '대구 FC', 'time': '18:00'}
    ],
    'vleague': [
        {'date': '2026-05-29', 'home': '현대캐피탈', 'away': '대한항공', 'time': '18:00'},
        {'date': '2026-05-30', 'home': 'KB손해보험', 'away': 'OK금융그룹', 'time': '19:00'},
        {'date': '2026-05-31', 'home': '우리카드', 'away': '삼성화재', 'time': '17:30'}
    ],
    'kbo': [
        {'date': '2026-05-29', 'home': 'LG 트윈스', 'away': '두산 베어스', 'time': '18:30', 'score': '3 - 2', 'status': '종료'},
        {'date': '2026-05-29', 'home': 'KIA 타이거즈', 'away': 'NC 다이노스', 'time': '18:30', 'score': '1 - 4', 'status': '5회'},
        {'date': '2026-05-29', 'home': 'SSG 랜더스', 'away': '키움 히어로즈', 'time': '18:30', 'score': '0 - 0', 'status': '경기전'}
    ]
}

# ========== 2026 FIFA 월드컵 데이터 ==========
WORLD_CUP_2026 = {
    'info': {
        'year': 2026,
        'name': 'FIFA World Cup 2026',
        'hosts': ['캐나다', '미국', '멕시코'],
        'start_date': '2026-06-12',
        'end_date': '2026-07-12',
        'teams_count': 48,
        'status': '진행중'
    },
    'groups': {
        'A': [
            {'name': '아르헨티나', 'flag': '🇦🇷', 'played': 2, 'wins': 2, 'draws': 0, 'losses': 0, 'gf': 5, 'ga': 1, 'points': 6},
            {'name': '프랑스', 'flag': '🇫🇷', 'played': 2, 'wins': 1, 'draws': 1, 'losses': 0, 'gf': 3, 'ga': 1, 'points': 4},
            {'name': '한국', 'flag': '🇰🇷', 'played': 2, 'wins': 0, 'draws': 1, 'losses': 1, 'gf': 2, 'ga': 4, 'points': 1},
            {'name': '사우디아라비아', 'flag': '🇸🇦', 'played': 2, 'wins': 0, 'draws': 0, 'losses': 2, 'gf': 1, 'ga': 5, 'points': 0}
        ],
        'B': [
            {'name': '독일', 'flag': '🇩🇪', 'played': 2, 'wins': 2, 'draws': 0, 'losses': 0, 'gf': 6, 'ga': 0, 'points': 6},
            {'name': '스페인', 'flag': '🇪🇸', 'played': 2, 'wins': 1, 'draws': 1, 'losses': 0, 'gf': 4, 'ga': 2, 'points': 4},
            {'name': '캐나다', 'flag': '🇨🇦', 'played': 2, 'wins': 0, 'draws': 1, 'losses': 1, 'gf': 1, 'ga': 4, 'points': 1},
            {'name': '일본', 'flag': '🇯🇵', 'played': 2, 'wins': 0, 'draws': 0, 'losses': 2, 'gf': 1, 'ga': 6, 'points': 0}
        ],
        'C': [
            {'name': '브라질', 'flag': '🇧🇷', 'played': 2, 'wins': 2, 'draws': 0, 'losses': 0, 'gf': 7, 'ga': 1, 'points': 6},
            {'name': '포르투갈', 'flag': '🇵🇹', 'played': 2, 'wins': 1, 'draws': 1, 'losses': 0, 'gf': 3, 'ga': 2, 'points': 4},
            {'name': '우루과이', 'flag': '🇺🇾', 'played': 2, 'wins': 0, 'draws': 1, 'losses': 1, 'gf': 2, 'ga': 3, 'points': 1},
            {'name': '파나마', 'flag': '🇵🇦', 'played': 2, 'wins': 0, 'draws': 0, 'losses': 2, 'gf': 0, 'ga': 6, 'points': 0}
        ],
        'D': [
            {'name': '네덜란드', 'flag': '🇳🇱', 'played': 2, 'wins': 2, 'draws': 0, 'losses': 0, 'gf': 5, 'ga': 1, 'points': 6},
            {'name': '영국', 'flag': '🇬🇧', 'played': 2, 'wins': 1, 'draws': 1, 'losses': 0, 'gf': 3, 'ga': 2, 'points': 4},
            {'name': '모로코', 'flag': '🇲🇦', 'played': 2, 'wins': 0, 'draws': 1, 'losses': 1, 'gf': 2, 'ga': 3, 'points': 1},
            {'name': '볼리비아', 'flag': '🇧🇴', 'played': 2, 'wins': 0, 'draws': 0, 'losses': 2, 'gf': 1, 'ga': 5, 'points': 0}
        ],
        'E': [
            {'name': '벨기에', 'flag': '🇧🇪', 'played': 2, 'wins': 1, 'draws': 1, 'losses': 0, 'gf': 4, 'ga': 2, 'points': 4},
            {'name': '루마니아', 'flag': '🇷🇴', 'played': 2, 'wins': 1, 'draws': 0, 'losses': 1, 'gf': 3, 'ga': 3, 'points': 3},
            {'name': '세르비아', 'flag': '🇷🇸', 'played': 2, 'wins': 1, 'draws': 0, 'losses': 1, 'gf': 2, 'ga': 2, 'points': 3},
            {'name': '알바니아', 'flag': '🇦🇱', 'played': 2, 'wins': 0, 'draws': 1, 'losses': 1, 'gf': 1, 'ga': 3, 'points': 1}
        ],
        'F': [
            {'name': '이탈리아', 'flag': '🇮🇹', 'played': 2, 'wins': 2, 'draws': 0, 'losses': 0, 'gf': 5, 'ga': 1, 'points': 6},
            {'name': '노르웨이', 'flag': '🇳🇴', 'played': 2, 'wins': 1, 'draws': 0, 'losses': 1, 'gf': 3, 'ga': 2, 'points': 3},
            {'name': '그리스', 'flag': '🇬🇷', 'played': 2, 'wins': 0, 'draws': 2, 'losses': 0, 'gf': 2, 'ga': 2, 'points': 2},
            {'name': '튀르키예', 'flag': '🇹🇷', 'played': 2, 'wins': 0, 'draws': 0, 'losses': 2, 'gf': 1, 'ga': 6, 'points': 0}
        ],
        'G': [
            {'name': '멕시코', 'flag': '🇲🇽', 'played': 2, 'wins': 1, 'draws': 1, 'losses': 0, 'gf': 3, 'ga': 2, 'points': 4},
            {'name': '호주', 'flag': '🇦🇺', 'played': 2, 'wins': 1, 'draws': 0, 'losses': 1, 'gf': 2, 'ga': 2, 'points': 3},
            {'name': '폴란드', 'flag': '🇵🇱', 'played': 2, 'wins': 0, 'draws': 2, 'losses': 0, 'gf': 2, 'ga': 2, 'points': 2},
            {'name': '사우스 아프리카', 'flag': '🇿🇦', 'played': 2, 'wins': 0, 'draws': 1, 'losses': 1, 'gf': 1, 'ga': 2, 'points': 1}
        ],
        'H': [
            {'name': '포르투갈', 'flag': '🇵🇹', 'played': 2, 'wins': 2, 'draws': 0, 'losses': 0, 'gf': 6, 'ga': 1, 'points': 6},
            {'name': '스웨덴', 'flag': '🇸🇪', 'played': 2, 'wins': 1, 'draws': 0, 'losses': 1, 'gf': 3, 'ga': 3, 'points': 3},
            {'name': '슬로바키아', 'flag': '🇸🇰', 'played': 2, 'wins': 0, 'draws': 1, 'losses': 1, 'gf': 2, 'ga': 4, 'points': 1},
            {'name': '룩셈부르크', 'flag': '🇱🇺', 'played': 2, 'wins': 0, 'draws': 1, 'losses': 1, 'gf': 1, 'ga': 4, 'points': 1}
        ],
        'I': [
            {'name': '프랑스', 'flag': '🇫🇷', 'played': 2, 'wins': 1, 'draws': 1, 'losses': 0, 'gf': 3, 'ga': 2, 'points': 4},
            {'name': '덴마크', 'flag': '🇩🇰', 'played': 2, 'wins': 1, 'draws': 0, 'losses': 1, 'gf': 3, 'ga': 2, 'points': 3},
            {'name': '슬로베니아', 'flag': '🇸🇮', 'played': 2, 'wins': 0, 'draws': 2, 'losses': 0, 'gf': 1, 'ga': 1, 'points': 2},
            {'name': '카자흐스탄', 'flag': '🇰🇿', 'played': 2, 'wins': 0, 'draws': 1, 'losses': 1, 'gf': 1, 'ga': 3, 'points': 1}
        ],
        'J': [
            {'name': '이집트', 'flag': '🇪🇬', 'played': 2, 'wins': 1, 'draws': 1, 'losses': 0, 'gf': 3, 'ga': 1, 'points': 4},
            {'name': '모로코', 'flag': '🇲🇦', 'played': 2, 'wins': 1, 'draws': 0, 'losses': 1, 'gf': 2, 'ga': 2, 'points': 3},
            {'name': '코스타리카', 'flag': '🇨🇷', 'played': 2, 'wins': 0, 'draws': 2, 'losses': 0, 'gf': 2, 'ga': 2, 'points': 2},
            {'name': '뉴질랜드', 'flag': '🇳🇿', 'played': 2, 'wins': 0, 'draws': 1, 'losses': 1, 'gf': 1, 'ga': 3, 'points': 1}
        ],
        'K': [
            {'name': '우루과이', 'flag': '🇺🇾', 'played': 2, 'wins': 2, 'draws': 0, 'losses': 0, 'gf': 5, 'ga': 0, 'points': 6},
            {'name': '오스트리아', 'flag': '🇦🇹', 'played': 2, 'wins': 1, 'draws': 0, 'losses': 1, 'gf': 2, 'ga': 2, 'points': 3},
            {'name': '불가리아', 'flag': '🇧🇬', 'played': 2, 'wins': 0, 'draws': 1, 'losses': 1, 'gf': 1, 'ga': 3, 'points': 1},
            {'name': '우크라이나', 'flag': '🇺🇦', 'played': 2, 'wins': 0, 'draws': 1, 'losses': 1, 'gf': 1, 'ga': 4, 'points': 1}
        ],
        'L': [
            {'name': '칠레', 'flag': '🇨🇱', 'played': 2, 'wins': 1, 'draws': 1, 'losses': 0, 'gf': 4, 'ga': 2, 'points': 4},
            {'name': '이란', 'flag': '🇮🇷', 'played': 2, 'wins': 1, 'draws': 0, 'losses': 1, 'gf': 3, 'ga': 2, 'points': 3},
            {'name': '페루', 'flag': '🇵🇪', 'played': 2, 'wins': 0, 'draws': 2, 'losses': 0, 'gf': 2, 'ga': 2, 'points': 2},
            {'name': '홍콩', 'flag': '🇭🇰', 'played': 2, 'wins': 0, 'draws': 1, 'losses': 1, 'gf': 1, 'ga': 4, 'points': 1}
        ]
    },
    'matches': [
        {'id': 1, 'group': 'A', 'home': '아르헨티나', 'away': '사우디아라비아', 'date': '2026-06-13', 'time': '10:00', 'result': '3-1', 'status': '종료', 'stadium': '메트라폴리타노'},
        {'id': 2, 'group': 'A', 'home': '한국', 'away': '프랑스', 'date': '2026-06-13', 'time': '13:00', 'result': '1-2', 'status': '종료', 'stadium': '뮤추얼 오브 오마하'},
        {'id': 3, 'group': 'B', 'home': '독일', 'away': '일본', 'date': '2026-06-14', 'time': '10:00', 'result': '3-0', 'status': '종료', 'stadium': '에릭슨 스타디움'},
        {'id': 4, 'group': 'B', 'home': '스페인', 'away': '캐나다', 'date': '2026-06-14', 'time': '13:00', 'result': '2-1', 'status': '종료', 'stadium': '뮤추얼 오브 오마하'},
        {'id': 5, 'group': 'C', 'home': '브라질', 'away': '파나마', 'date': '2026-06-15', 'time': '10:00', 'result': '4-0', 'status': '종료', 'stadium': '산 엘리에로'},
        {'id': 6, 'group': 'C', 'home': '포르투갈', 'away': '우루과이', 'date': '2026-06-15', 'time': '13:00', 'result': '1-1', 'status': '종료', 'stadium': '메트라폴리타노'},
        {'id': 7, 'group': 'D', 'home': '네덜란드', 'away': '볼리비아', 'date': '2026-06-16', 'time': '10:00', 'result': '3-0', 'status': '종료', 'stadium': '에릭슨 스타디움'},
        {'id': 8, 'group': 'D', 'home': '영국', 'away': '모로코', 'date': '2026-06-16', 'time': '13:00', 'result': '2-0', 'status': '종료', 'stadium': '뮤추얼 오브 오마하'},
        {'id': 9, 'group': 'A', 'home': '아르헨티나', 'away': '프랑스', 'date': '2026-06-21', 'time': '16:00', 'result': '미결정', 'status': '예정', 'stadium': '메트라폴리타노'},
        {'id': 10, 'group': 'B', 'home': '독일', 'away': '스페인', 'date': '2026-06-22', 'time': '16:00', 'result': '미결정', 'status': '예정', 'stadium': '뮤추얼 오브 오마하'},
    ],
    'ko_round': [
        {'round': '16강', 'matches': []},
        {'round': '8강', 'matches': []},
        {'round': '4강', 'matches': []},
        {'round': '결승', 'matches': []}
    ]
}


# ==========================================
# 2. 유틸리티 함수 (파일 I/O 및 데이터 처리)
# ==========================================
def ensure_data_files():
    """데이터 저장용 폴더 및 JSON 기본 파일 생성"""
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(USERS_FILE):
        save_json(USERS_FILE, {})
    if not os.path.exists(POSTS_FILE):
        save_json(POSTS_FILE, [])


def load_json(path, default):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return default


def save_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def hash_password(raw_password):
    """비밀번호 안전하게 해싱"""
    return hashlib.sha256(raw_password.encode('utf-8')).hexdigest()


def generate_anonymous_id():
    """익명 ID 생성 (예: 익명-A1B2C3D4)"""
    random_hash = hashlib.md5(str(datetime.now().timestamp()).encode()).hexdigest()[:8].upper()
    return f"익명-{random_hash}"


def get_current_user():
    """세션 기반 현재 사용자 확인"""
    username = session.get('username')
    if not username:
        return None
    users = load_json(USERS_FILE, {})
    return {'username': username} if username in users else None


# ==========================================
# 3. 웹 페이지 렌더링 라우트 (HTML 라우팅)
# ==========================================
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/auth')
def auth():
    return redirect(url_for('login_page'))


@app.route('/signup')
def signup_page():
    return render_template('signup.html')


@app.route('/login')
def login_page():
    return render_template('login.html')


@app.route('/board')
def board_page():
    return render_template('board.html')


@app.route('/toto')
def toto_page():
    return render_template('toto.html')


@app.route('/lotto')
def lotto_page():
    return render_template('lotto.html')


@app.route('/roto')
def roto_redirect():
    return redirect(url_for('lotto_page'))


@app.route('/world-cup')
def world_cup_page():
    return render_template('world_cup.html')


@app.route('/league/<league_name>')
def league_page(league_name):
    if league_name not in ('kleague', 'vleague', 'kbo'):
        abort(404)
    return render_template('league.html', league=league_name)


# ==========================================
# 4. REST API 라우트
# ==========================================

# [API] 스포츠 경기 일정 및 결과 반환
@app.route('/api/sports/schedule', methods=['GET'])
def get_sports_schedule():
    league = request.args.get('league')
    if league:
        schedule = SPORT_SCHEDULES.get(league)
        if schedule is None:
            return jsonify({'error': '존재하지 않는 리그입니다.'}), 400
        return jsonify(schedule), 200
    return jsonify(SPORT_SCHEDULES), 200


# ========== 월드컵 2026 API 엔드포인트 ==========
@app.route('/api/world-cup/info', methods=['GET'])
def get_world_cup_info():
    """월드컵 기본 정보 조회"""
    return jsonify(WORLD_CUP_2026['info']), 200


@app.route('/api/world-cup/standings', methods=['GET'])
def get_world_cup_standings():
    """월드컵 조별 순위 조회"""
    group = request.args.get('group', None)
    if group:
        if group not in WORLD_CUP_2026['groups']:
            return jsonify({'error': '존재하지 않는 조입니다.'}), 400
        return jsonify({group: WORLD_CUP_2026['groups'][group]}), 200
    return jsonify(WORLD_CUP_2026['groups']), 200


@app.route('/api/world-cup/matches', methods=['GET'])
def get_world_cup_matches():
    """월드컵 경기 조회"""
    status = request.args.get('status', None)  # 'completed', 'upcoming', 'all'
    group = request.args.get('group', None)
    
    matches = WORLD_CUP_2026['matches']
    
    if group:
        matches = [m for m in matches if m['group'] == group]
    
    if status == 'completed':
        matches = [m for m in matches if m['status'] == '종료']
    elif status == 'upcoming':
        matches = [m for m in matches if m['status'] == '예정']
    
    return jsonify({'matches': matches}), 200


@app.route('/api/world-cup/team/<team_name>', methods=['GET'])
def get_team_info(team_name):
    """특정 팀 정보 조회"""
    for group, teams in WORLD_CUP_2026['groups'].items():
        for team in teams:
            if team['name'] == team_name:
                return jsonify({'group': group, 'team': team}), 200
    return jsonify({'error': '팀을 찾을 수 없습니다.'}), 404


@app.route('/api/world-cup/ko-round', methods=['GET'])
def get_ko_round():
    """논코-아웃 라운드 정보"""
    return jsonify(WORLD_CUP_2026['ko_round']), 200


# [API] 특정 KBO 전용 API 단독 제공 버전 (필요시 사용)
@app.route('/api/kbo', methods=['GET'])
def get_kbo_data():
    return jsonify({'games': SPORT_SCHEDULES['kbo']}), 200
@app.route('/kbo')
def kbo():
    return render_template('kbo.html')

# [API] 회원가입
@app.route('/api/signup', methods=['POST'])
def signup():
    ensure_data_files()
    data = request.get_json() or {}
    username = str(data.get('username', '')).strip()
    password = str(data.get('password', '')).strip()
    nickname = str(data.get('nickname', '')).strip()
    
    if not username or not password or not nickname:
        return jsonify({'error': '아이디, 비밀번호, 닉네임을 모두 입력하세요.'}), 400

    users = load_json(USERS_FILE, {})
    if username in users:
        return jsonify({'error': '이미 존재하는 아이디입니다.'}), 400

    users[username] = {
        'password': hash_password(password),
        'nickname': nickname
    }
    save_json(USERS_FILE, users)
    session['username'] = username
    return jsonify({'message': '회원가입이 완료되었습니다.', 'username': username, 'nickname': nickname}), 201


# [API] 로그인
@app.route('/api/login', methods=['POST'])
def login():
    ensure_data_files()
    data = request.get_json() or {}
    username = str(data.get('username', '')).strip()
    password = str(data.get('password', '')).strip()
    
    users = load_json(USERS_FILE, {})
    if username not in users or users[username]['password'] != hash_password(password):
        return jsonify({'error': '아이디 또는 비밀번호가 잘못되었습니다.'}), 401

    session['username'] = username
    return jsonify({'message': '로그인 성공', 'username': username}), 200


# [API] 로그아웃
@app.route('/api/logout', methods=['POST'])
def logout():
    session.pop('username', None)
    return jsonify({'message': '로그아웃 되었습니다.'}), 200


# [API] 회원 프로필 조회
@app.route('/api/profile', methods=['GET'])
def profile():
    user = get_current_user()
    if not user:
        return jsonify({'logged_in': False}), 200
    
    users = load_json(USERS_FILE, {})
    user_info = users.get(user['username'], {})
    return jsonify({
        'logged_in': True,
        'username': user['username'],
        'nickname': user_info.get('nickname', user['username'])
    }), 200


# [API] 게시판 조회 및 등록
@app.route('/api/posts', methods=['GET', 'POST'])
def handle_posts():
    ensure_data_files()
    post_list = load_json(POSTS_FILE, [])
    
    if request.method == 'GET':
        # 페이징 파라미터
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 20, type=int)
        
        # 최신글 먼저 정렬
        post_list_reversed = list(reversed(post_list))
        
        # 전체 페이지 수 계산
        total_posts = len(post_list_reversed)
        total_pages = (total_posts + limit - 1) // limit
        
        # 페이지 유효성 체크
        if page < 1:
            page = 1
        if page > total_pages and total_pages > 0:
            page = total_pages
        
        # 페이징 계산
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        paginated_posts = post_list_reversed[start_idx:end_idx]
        
        return jsonify({
            'posts': paginated_posts,
            'current_page': page,
            'total_pages': total_pages,
            'total_posts': total_posts,
            'posts_per_page': limit
        }), 200

    # POST 요청 (새 글 작성) - 로그인 필요 없음 (익명)
    data = request.get_json() or {}
    title = str(data.get('title', '')).strip()
    body = str(data.get('body', '')).strip()
    password = str(data.get('password', '')).strip()  # 삭제용 비밀번호
    
    if not title or not body:
        return jsonify({'error': '제목과 내용을 모두 입력하세요.'}), 400
    
    if not password or len(password) < 4:
        return jsonify({'error': '게시글 삭제용 비밀번호는 4자 이상이어야 합니다.'}), 400
    
    # 순차 고유 ID 생성
    next_id = max([p['id'] for p in post_list], default=0) + 1
    anonymous_id = generate_anonymous_id()

    new_post = {
        'id': next_id,
        'title': title,
        'body': body,
        'author': anonymous_id,
        'password_hash': hash_password(password),
        'date': datetime.now().strftime('%Y-%m-%d %H:%M')
    }
    post_list.append(new_post)
    save_json(POSTS_FILE, post_list)
    return jsonify({'message': '게시물이 등록되었습니다.', 'post': new_post}), 201


# [API] 게시글 삭제 (비밀번호 확인)
@app.route('/api/posts/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    ensure_data_files()
    post_list = load_json(POSTS_FILE, [])
    
    data = request.get_json() or {}
    password = str(data.get('password', '')).strip()
    
    # 게시글 찾기
    post_index = None
    for idx, post in enumerate(post_list):
        if post['id'] == post_id:
            post_index = idx
            break
    
    if post_index is None:
        return jsonify({'error': '게시물을 찾을 수 없습니다.'}), 404
    
    # 비밀번호 확인
    post = post_list[post_index]
    if post.get('password_hash') != hash_password(password):
        return jsonify({'error': '비밀번호가 일치하지 않습니다.'}), 401
    
    # 삭제
    del post_list[post_index]
    save_json(POSTS_FILE, post_list)
    return jsonify({'message': '게시물이 삭제되었습니다.'}), 200


# [API] 로또 번호 자동 생성
@app.route('/api/lotto/generate', methods=['GET'])
def generate_lotto():
    # 번호 추출
    numbers = random.sample(range(LOTTO_MIN, LOTTO_MAX + 1), LOTTO_COUNT)
    numbers.sort()
    
    # 보너스 번호 추출
    candidates = [n for n in range(LOTTO_MIN, LOTTO_MAX + 1) if n not in numbers]
    bonus = random.choice(candidates)
    
    return jsonify({'numbers': numbers, 'bonus': bonus}), 200


# ==========================================
# 5. 실행 실행
# ==========================================
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)