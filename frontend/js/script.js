let canvas, ctx;
let balls = [];
let drawCount = 0;
let CANVAS_W = 420, CANVAS_H = 420;

const MAX_LINES = 5;

/* =========================
   배경 공 클래스
========================= */
class Ball {
    constructor(num) {
        this.num = num;
        this.radius = 16;
        this.x = Math.random() * (CANVAS_W - this.radius * 2) + this.radius;
        this.y = Math.random() * (CANVAS_H - this.radius * 2) + this.radius;
        // 더 넓게 흩날리도록 속도 범위 확대
        this.vx = (Math.random() - 0.5) * 10;
        this.vy = (Math.random() - 0.5) * 10;
    }

    move() {
        this.x += this.vx;
        this.y += this.vy;

        if (this.x < this.radius || this.x > CANVAS_W - this.radius) this.vx *= -1;
        if (this.y < this.radius || this.y > CANVAS_H - this.radius) this.vy *= -1;
    }

    draw() {
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
        ctx.fillStyle = getColor(this.num);
        ctx.fill();

        ctx.fillStyle = "white";
        ctx.font = "bold 12px Arial";
        ctx.textAlign = "center";
        ctx.textBaseline = "middle";
        ctx.fillText(this.num, this.x, this.y);
    }
}

/* =========================
   초기화 / 애니메이션
========================= */
function init() {
    balls = Array.from({ length: 45 }, (_, i) => new Ball(i + 1));
}

function animate() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    balls.forEach(b => {
        b.move();
        b.draw();
    });
    requestAnimationFrame(animate);
}

/* =========================
   로또 번호 생성
========================= */
function generateLottoNumbers() {
    const set = new Set();
    while (set.size < 6) {
        set.add(Math.floor(Math.random() * 45) + 1);
    }
    return Array.from(set).sort((a, b) => a - b);
}

/* =========================
   색상
========================= */
function getColor(n) {
    if (n <= 10) return "#f1c40f";
    if (n <= 20) return "#3498db";
    if (n <= 30) return "#2ecc71";
    if (n <= 40) return "#9b59b6";
    return "#e67e22";
}

function getColorClass(n) {
    if (n <= 10) return "c1";
    if (n <= 20) return "c2";
    if (n <= 30) return "c3";
    if (n <= 40) return "c4";
    return "c5";
}

/* =========================
   배관 애니메이션
========================= */
function moveToPipe(n) {
    return new Promise(resolve => {
        const tube = document.getElementById("tube");
        if (!tube) return resolve();

        const el = document.createElement("div");
        el.className = `ball-moving ${getColorClass(n)}`;
        el.innerText = n;

        el.style.top = "-40px";
        el.style.opacity = "0";

        tube.appendChild(el);

        requestAnimationFrame(() => {
            setTimeout(() => {
                el.style.transition = "all 0.45s ease";
                el.style.top = "10px";
                el.style.opacity = "1";
            }, 10);
        });

        setTimeout(() => {
            el.remove();
            resolve();
        }, 500);
    });
}

/* =========================
   1줄 생성
========================= */
async function startDraw() {
    if (drawCount >= MAX_LINES) {
        showResetConfirm();
        return;
    }

    const nums = generateLottoNumbers();
    const result = document.getElementById("result");

    const line = document.createElement("div");
    line.className = "line";
    line.innerHTML = `<strong>${drawCount + 1}줄</strong>`;
    result.appendChild(line);

    drawCount++;

    for (const n of nums) {
        await moveToPipe(n);

        const ball = document.createElement("div");
        ball.className = `ball ${getColorClass(n)}`;
        ball.innerText = n;
        line.appendChild(ball);
    }
}

/* =========================
   5줄 즉시
========================= */
function fastFive() {
    resetDraw();

    const result = document.getElementById("result");

    for (let i = 1; i <= 5; i++) {
        const line = document.createElement("div");
        line.className = "line";
        line.innerHTML = `<strong>${i}줄</strong>`;

        generateLottoNumbers().forEach(n => {
            const b = document.createElement("div");
            b.className = `ball ${getColorClass(n)}`;
            b.innerText = n;
            line.appendChild(b);
        });

        result.appendChild(line);
    }

    drawCount = 5;
}

/* =========================
   reset
========================= */
function resetDraw() {
    document.getElementById("result").innerHTML = "";
    drawCount = 0;
}

/* =========================
   팝업
========================= */
function showResetConfirm() {
    const popup = document.createElement("div");

    popup.style.cssText = `
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background: #111;
        color: #fff;
        padding: 20px;
        border-radius: 12px;
        z-index: 9999;
        text-align: center;
    `;

    popup.innerHTML = `
        <p>5줄 초과</p>
        <p>초기화하시겠습니까?</p>
        <button id="yesBtn">YES</button>
        <button id="noBtn">NO</button>
    `;

    document.body.appendChild(popup);

    document.getElementById("yesBtn").onclick = () => {
        resetDraw();
        popup.remove();
    };

    document.getElementById("noBtn").onclick = () => {
        popup.remove();
    };
}

/* =========================
   KBO API
========================= */
async function loadKBO() {
    const table = document.getElementById("scheduleTable");
    if (!table) return;

    try {
        const res = await fetch("/api/kbo");
        const data = await res.json();

        table.innerHTML = "";

        data.games.forEach(game => {
            const row = document.createElement("tr");

            row.innerHTML = `
                <td>${game.date}</td>
                <td>${game.time}</td>
                <td>${game.home}</td>
                <td>${game.away}</td>
                <td>${game.score || "-"}</td>
                <td>${game.status || "-"}</td>
            `;

            table.appendChild(row);
        });

    } catch (err) {
        console.log("KBO 실패", err);
        table.innerHTML = `<tr><td colspan="6">데이터 로딩 실패</td></tr>`;
    }
}

/* =========================
   사이트 통계 로드 (방문자 증가 포함)
========================= */
async function loadStats() {
    try {
        const last = localStorage.getItem('visitedAt');
        const now = Date.now();
        const DAY = 24 * 60 * 60 * 1000;

        if (!last || now - Number(last) > DAY) {
            await fetch('/api/visit', { method: 'POST' });
            localStorage.setItem('visitedAt', String(now));
        }

        const res = await fetch('/api/stats');
        const data = await res.json();

        const v = document.getElementById('statsVisits');
        const u = document.getElementById('statsUsers');
        const p = document.getElementById('statsPosts');

        if (v) v.innerText = data.visits ?? '-';
        if (u) u.innerText = data.users ?? '-';
        if (p) p.innerText = data.posts ?? '-';
    } catch (err) {
        console.log('통계 로드 실패', err);
    }
}

/* =========================
   스포츠 일정 렌더링
========================= */
async function loadSportsSchedules() {
    try {
        const res = await fetch('/api/sports/schedule');
        const data = await res.json();
        const panel = document.getElementById('sportsPanel');
        if (!panel) return;

        panel.innerHTML = '';
        Object.entries(data).forEach(([league, games]) => {
            const card = document.createElement('div');
            card.className = 'kbo-card';
            const title = document.createElement('h3');
            title.style.marginBottom = '8px';
            title.style.color = '#fff';
            title.innerText = league.toUpperCase();
            card.appendChild(title);

            const tbl = document.createElement('table');
            tbl.className = 'schedule-table';
            const thead = document.createElement('thead');
            thead.innerHTML = `<tr><th>날짜</th><th>시간</th><th>홈</th><th>원정</th><th>스코어</th><th>상태</th></tr>`;
            tbl.appendChild(thead);
            const tbody = document.createElement('tbody');
            (games || []).forEach(g => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${g.date || '-'}</td>
                    <td>${g.time || '-'}</td>
                    <td>${g.home || '-'}</td>
                    <td>${g.away || '-'}</td>
                    <td>${g.score || '-'}</td>
                    <td>${g.status || '-'}</td>
                `;
                tbody.appendChild(tr);
            });
            tbl.appendChild(tbody);
            card.appendChild(tbl);
            panel.appendChild(card);
        });
    } catch (err) {
        console.log('스포츠 일정 로드 실패', err);
    }
}

/* =========================
   실행
========================= */
document.addEventListener("DOMContentLoaded", () => {
    canvas = document.getElementById("canvas");

    if (canvas) {
        ctx = canvas.getContext("2d");

        function resizeCanvas() {
            // Prefer parent element dimensions; fall back to bounding rect or defaults
            const parent = canvas.parentElement || document.body;
            const rectW = parent.clientWidth || canvas.getBoundingClientRect().width || 420;
            const rectH = parent.clientHeight || canvas.getBoundingClientRect().height || rectW;
            canvas.width = rectW;
            canvas.height = rectH;
            CANVAS_W = canvas.width;
            CANVAS_H = canvas.height;
            init();
        }

        resizeCanvas();
        window.addEventListener('resize', () => { resizeCanvas(); });

        animate();
        const fallback = document.getElementById('machineFallback');
        if (fallback) fallback.style.display = 'none';
    }

    loadKBO();
    setInterval(loadKBO, 10000);
    // 방문자/통계 로드
    loadStats();
    setInterval(loadStats, 30000);

    // 스포츠 일정 로드
    loadSportsSchedules();
    setInterval(loadSportsSchedules, 30000);

    // 로또 회차별 이력 로드 (최신)
    if (typeof loadLottoHistory === 'function') {
        loadLottoHistory();
    }
});


/* =========================
   로또 회차별 결과 표시
========================= */
async function loadLottoHistory() {
    try {
        const res = await fetch('/api/lotto/history');
        const j = await res.json();
        const container = document.getElementById('lottoHistory');
        if (!container) return;
        container.innerHTML = '';

        const draws = j.draws || {};
        if (Object.keys(draws).length === 0) {
            container.innerText = '회차 데이터가 없습니다.';
            return;
        }

        Object.keys(draws).sort((a,b)=>Number(b)-Number(a)).forEach(key => {
            const d = draws[key];
            const div = document.createElement('div');
            div.style.padding = '8px 6px';
            div.style.borderBottom = '1px solid rgba(255,255,255,0.04)';
            div.innerHTML = `<strong>${key}회 (${d.drwNoDate || ''})</strong> `;
            const nums = (d.numbers || []).map(n=>`<span class="ball ${getColorClass(n)}" style="display:inline-block;margin-left:6px;">${n}</span>`).join('');
            div.innerHTML += nums + (d.bonus ? `<span style="margin-left:8px; color:var(--muted);">보너스: ${d.bonus}</span>` : '');
            container.appendChild(div);
        });
    } catch (err) {
        console.log('로또 이력 로드 실패', err);
    }
}

async function fetchLottoRoundUI() {
    const v = document.getElementById('drwNoInput').value;
    if (!v) return loadLottoHistory();
    try {
        const res = await fetch('/api/lotto/history?round=' + encodeURIComponent(v));
        if (!res.ok) {
            alert('회차 데이터를 불러올 수 없습니다.');
            return;
        }
        const j = await res.json();
        const d = j.draw;
        const container = document.getElementById('lottoHistory');
        container.innerHTML = '';
        if (!d) {
            container.innerText = '해당 회차 데이터 없음';
            return;
        }
        const div = document.createElement('div');
        div.innerHTML = `<h4>${d.drwNo}회 (${d.drwNoDate || ''})</h4>`;
        const nums = (d.numbers || []).map(n=>`<span class="ball ${getColorClass(n)}" style="display:inline-block;margin-right:6px">${n}</span>`).join('');
        div.innerHTML += `<div>${nums} <span style="margin-left:8px; color:var(--muted);">보너스: ${d.bonus}</span></div>`;
        container.appendChild(div);
    } catch (err) {
        console.log('fetchLottoRoundUI error', err);
    }
}