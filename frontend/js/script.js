let canvas, ctx;
let balls = [];
let drawCount = 0;

const MAX_LINES = 5;

/* =========================
   배경 공 클래스
========================= */
class Ball {
    constructor(num) {
        this.num = num;
        this.radius = 16;
        this.x = Math.random() * (420 - this.radius * 2) + this.radius;
        this.y = Math.random() * (420 - this.radius * 2) + this.radius;
        this.vx = (Math.random() - 0.5) * 4;
        this.vy = (Math.random() - 0.5) * 4;
    }

    move() {
        this.x += this.vx;
        this.y += this.vy;

        if (this.x < this.radius || this.x > 420 - this.radius) this.vx *= -1;
        if (this.y < this.radius || this.y > 420 - this.radius) this.vy *= -1;
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
   실행
========================= */
document.addEventListener("DOMContentLoaded", () => {
    canvas = document.getElementById("canvas");

    if (canvas) {
        ctx = canvas.getContext("2d");
        canvas.width = 420;
        canvas.height = 420;

        init();
        animate();
    }

    loadKBO();
    setInterval(loadKBO, 10000);
});