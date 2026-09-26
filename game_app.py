from fastapi import FastAPI
from fastapi.responses import Response

app = FastAPI()

PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Space Bar Jump</title>
<style>
  body {
    margin: 0;
    background: #1e1e2e;
    color: #eee;
    font-family: system-ui, sans-serif;
    display: flex;
    flex-direction: column;
    align-items: center;
    padding-top: 40px;
  }
  h1 { margin-bottom: 4px; }
  p { margin-top: 0; color: #aaa; }
  canvas {
    background: #2a2a3d;
    border: 2px solid #555;
    border-radius: 8px;
  }
  #score {
    font-size: 20px;
    margin-top: 10px;
  }
  #overlay {
    margin-top: 10px;
    font-size: 16px;
    color: #f88;
    min-height: 24px;
  }
</style>
</head>
<body>
  <h1>Space Bar Jump</h1>
  <p>Click the game area once, then press <b>Space</b> to jump over the obstacles. Space also restarts after a crash.</p>
  <canvas id="game" width="600" height="200" tabindex="0"></canvas>
  <div id="score">Score: 0</div>
  <div id="overlay"></div>

<script>
const canvas = document.getElementById("game");
const ctx = canvas.getContext("2d");
const scoreEl = document.getElementById("score");
const overlayEl = document.getElementById("overlay");

const groundY = 160;

let player, obstacles, score, speed, gameOver, lastObstacleTime, frame;

function resetGame() {
  player = { x: 50, y: groundY, w: 32, h: 32, vy: 0, jumping: false };
  obstacles = [];
  score = 0;
  speed = 4;
  gameOver = false;
  lastObstacleTime = 0;
  frame = 0;
  overlayEl.textContent = "";
  scoreEl.textContent = "Score: 0";
}

function spawnObstacle() {
  obstacles.push({ x: canvas.width, y: groundY, w: 15, h: 30 });
}

function jump() {
  if (!player.jumping && !gameOver) {
    player.vy = -9;
    player.jumping = true;
  }
}

// The game runs inside an embedded view, which doesn't have keyboard focus
// until something inside it is clicked — so grab focus immediately and any
// time the canvas is clicked, and listen on window to catch the keydown.
canvas.focus();
canvas.addEventListener("click", () => canvas.focus());
window.addEventListener("keydown", (e) => {
  if (e.code === "Space") {
    e.preventDefault();
    if (gameOver) {
      resetGame();
    } else {
      jump();
    }
  }
});

function update() {
  if (gameOver) return;

  frame++;

  // gravity
  player.vy += 0.5;
  player.y += player.vy;
  if (player.y > groundY) {
    player.y = groundY;
    player.vy = 0;
    player.jumping = false;
  }

  // spawn obstacles periodically
  if (frame - lastObstacleTime > 60 + Math.random() * 40) {
    spawnObstacle();
    lastObstacleTime = frame;
  }

  // move obstacles
  for (const o of obstacles) {
    o.x -= speed;
  }
  obstacles = obstacles.filter(o => o.x + o.w > 0);

  // collision detection
  for (const o of obstacles) {
    const playerTop = player.y - player.h;
    const playerBottom = player.y;
    const obstacleTop = o.y - o.h;
    const obstacleBottom = o.y;
    const overlapX = player.x < o.x + o.w && player.x + player.w > o.x;
    const overlapY = playerBottom > obstacleTop && playerTop < obstacleBottom;
    if (overlapX && overlapY) {
      gameOver = true;
      overlayEl.textContent = "Crashed! Final score: " + score + " — press Space to try again.";
    }
  }

  if (!gameOver) {
    score++;
    scoreEl.textContent = "Score: " + score;
    speed = 4 + Math.floor(score / 300) * 0.5;
  }
}

function draw() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  // ground line
  ctx.strokeStyle = "#666";
  ctx.beginPath();
  ctx.moveTo(0, groundY + 1);
  ctx.lineTo(canvas.width, groundY + 1);
  ctx.stroke();

  // player: big bright circle with a face, impossible to miss
  const px = player.x;
  const pTop = player.y - player.h;
  const cx = px + player.w / 2;
  const cy = pTop + player.h / 2;
  const r = player.h / 2;

  ctx.beginPath();
  ctx.arc(cx, cy, r, 0, Math.PI * 2);
  ctx.fillStyle = "#ffd400";
  ctx.fill();
  ctx.lineWidth = 3;
  ctx.strokeStyle = "#000";
  ctx.stroke();

  // eyes
  ctx.fillStyle = "#000";
  ctx.beginPath();
  ctx.arc(cx - 5, cy - 4, 2, 0, Math.PI * 2);
  ctx.arc(cx + 5, cy - 4, 2, 0, Math.PI * 2);
  ctx.fill();

  // smile
  ctx.beginPath();
  ctx.arc(cx, cy + 2, 6, 0, Math.PI);
  ctx.stroke();

  // obstacles
  ctx.fillStyle = "#f88";
  for (const o of obstacles) {
    ctx.fillRect(o.x, o.y - o.h, o.w, o.h);
  }
}

function loop() {
  update();
  draw();
  requestAnimationFrame(loop);
}

resetGame();
loop();
</script>
</body>
</html>
"""

@app.get("/")
def index():
    return Response(
        content=PAGE,
        media_type="text/html",
        headers={"Cache-Control": "no-store, no-cache, must-revalidate"},
    )
