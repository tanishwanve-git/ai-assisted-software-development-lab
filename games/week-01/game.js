/* ============================
   Bug Dodger — game.js
   Core game logic
   ============================ */

'use strict';

// ─── Canvas Setup ───────────────────────────────────────────────────────────

const canvas  = document.getElementById('game-canvas');
const ctx     = canvas.getContext('2d');
const wrapper = document.getElementById('arena-wrapper');

/** Resize canvas to its CSS-rendered size (for crisp pixels on high-DPI). */
function resizeCanvas() {
  const dpr = window.devicePixelRatio || 1;
  const rect = wrapper.getBoundingClientRect();
  canvas.width  = rect.width  * dpr;
  canvas.height = rect.height * dpr;
  ctx.scale(dpr, dpr);
  // Store logical (CSS-pixel) dimensions for game logic
  canvas._w = rect.width;
  canvas._h = rect.height;
}

window.addEventListener('resize', () => {
  resizeCanvas();
  // Reposition player on resize so it doesn't go off-screen
  if (state.running) {
    player.x = Math.min(player.x, canvas._w - player.size);
  }
});

// ─── DOM References ──────────────────────────────────────────────────────────

const scoreDisplay  = document.getElementById('score-display');
const bestDisplay   = document.getElementById('best-display');
const levelDisplay  = document.getElementById('level-display');
const startScreen   = document.getElementById('start-screen');
const gameOverScreen = document.getElementById('game-over-screen');
const finalScore    = document.getElementById('final-score');
const finalBest     = document.getElementById('final-best');
const finalLevel    = document.getElementById('final-level');
const startBtn      = document.getElementById('start-btn');
const restartBtn    = document.getElementById('restart-btn');
const menuBtn       = document.getElementById('menu-btn');

// ─── Game Constants ──────────────────────────────────────────────────────────

const PLAYER_SIZE    = 28;       // px
const PLAYER_SPEED   = 6;        // px per frame
const PLAYER_Y_INSET = 48;       // distance from bottom
const BUG_SIZE       = 28;
const BUG_EMOJIS     = ['🐛', '🐜', '🦟', '🪲', '🕷️'];
const BASE_BUG_SPEED = 2.5;
const MAX_BUG_SPEED  = 9;
const BUG_SPAWN_BASE = 90;       // frames between spawns (decreases with level)
const LEVEL_EVERY    = 500;      // score points per level-up
const SCORE_PER_SEC  = 10;       // score added per second

// ─── Game State ──────────────────────────────────────────────────────────────

let state = {
  running:   false,
  paused:    false,
  score:     0,
  best:      parseInt(localStorage.getItem('bugdodger_best') || '0'),
  level:     1,
  frame:     0,
};

// ─── Player ──────────────────────────────────────────────────────────────────

const player = {
  x:    0,
  y:    0,
  size: PLAYER_SIZE,
  vx:   0,            // horizontal velocity
  trail: [],          // motion blur trail positions
};

function initPlayer() {
  player.x     = (canvas._w - player.size) / 2;
  player.y     = canvas._h - PLAYER_Y_INSET - player.size;
  player.vx    = 0;
  player.trail = [];
}

// ─── Bugs ────────────────────────────────────────────────────────────────────

let bugs = [];

function spawnBug() {
  const margin = BUG_SIZE + 8;
  const x = margin + Math.random() * (canvas._w - margin * 2);
  const speed = BASE_BUG_SPEED + (state.level - 1) * 0.6
                + Math.random() * 1.2;
  bugs.push({
    x,
    y:     -BUG_SIZE,
    size:  BUG_SIZE,
    speed: Math.min(speed, MAX_BUG_SPEED),
    emoji: BUG_EMOJIS[Math.floor(Math.random() * BUG_EMOJIS.length)],
    wobble: Math.random() * Math.PI * 2,  // phase offset for horizontal wobble
    wobbleAmp: 0.5 + Math.random() * 1.5, // wobble amplitude
  });
}

// ─── Keyboard Input ──────────────────────────────────────────────────────────

const keys = {};

window.addEventListener('keydown', (e) => {
  keys[e.key] = true;
  // Prevent arrow keys from scrolling the page
  if (['ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown'].includes(e.key)) {
    e.preventDefault();
  }
});

window.addEventListener('keyup', (e) => {
  keys[e.key] = false;
});

function isLeft()  { return keys['ArrowLeft']  || keys['a'] || keys['A']; }
function isRight() { return keys['ArrowRight'] || keys['d'] || keys['D']; }

// ─── Particle System ─────────────────────────────────────────────────────────

let particles = [];

function spawnExplosion(x, y) {
  const colors = ['#00e5ff', '#ff4d6d', '#ffd700', '#c77dff', '#ffffff'];
  for (let i = 0; i < 28; i++) {
    const angle = Math.random() * Math.PI * 2;
    const speed = 2 + Math.random() * 5;
    particles.push({
      x, y,
      vx:    Math.cos(angle) * speed,
      vy:    Math.sin(angle) * speed,
      life:  1,
      decay: 0.025 + Math.random() * 0.02,
      size:  3 + Math.random() * 4,
      color: colors[Math.floor(Math.random() * colors.length)],
    });
  }
}

function updateParticles() {
  particles = particles.filter(p => p.life > 0);
  for (const p of particles) {
    p.x   += p.vx;
    p.y   += p.vy;
    p.vy  += 0.12;   // gravity
    p.life -= p.decay;
  }
}

function drawParticles() {
  for (const p of particles) {
    ctx.save();
    ctx.globalAlpha = Math.max(0, p.life);
    ctx.fillStyle = p.color;
    ctx.shadowColor = p.color;
    ctx.shadowBlur = 8;
    ctx.beginPath();
    ctx.arc(p.x + p.size / 2, p.y + p.size / 2, p.size / 2, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();
  }
}

// ─── Scoring & Levelling ─────────────────────────────────────────────────────

let scoreTimer = 0;   // accumulates real time (ms)

function updateScore(dt) {
  scoreTimer += dt;
  if (scoreTimer >= 1000) {
    state.score  += SCORE_PER_SEC;
    scoreTimer   -= 1000;
    const newLevel = Math.floor(state.score / LEVEL_EVERY) + 1;
    if (newLevel !== state.level) {
      state.level = newLevel;
      levelDisplay.textContent = state.level;
    }
    scoreDisplay.textContent = state.score;
  }
}

// ─── Collision Detection (AABB) ──────────────────────────────────────────────

function rectsOverlap(ax, ay, aw, ah, bx, by, bw, bh) {
  const pad = 4; // slight forgiveness
  return ax + pad < bx + bw  &&
         ax + aw  > bx + pad &&
         ay + pad < by + bh  &&
         ay + ah  > by + pad;
}

// ─── Drawing Helpers ─────────────────────────────────────────────────────────

function drawBackground() {
  ctx.clearRect(0, 0, canvas._w, canvas._h);

  // Subtle radial vignette
  const grad = ctx.createRadialGradient(
    canvas._w / 2, canvas._h, 10,
    canvas._w / 2, canvas._h / 2, canvas._h * 0.9
  );
  grad.addColorStop(0, 'rgba(0,229,255,0.03)');
  grad.addColorStop(1, 'rgba(0,0,0,0.35)');
  ctx.fillStyle = grad;
  ctx.fillRect(0, 0, canvas._w, canvas._h);

  // Scanlines
  for (let y = 0; y < canvas._h; y += 4) {
    ctx.fillStyle = 'rgba(0,0,0,0.04)';
    ctx.fillRect(0, y, canvas._w, 1);
  }

  // Ground line
  const groundY = canvas._h - PLAYER_Y_INSET + 8;
  const lineGrad = ctx.createLinearGradient(0, 0, canvas._w, 0);
  lineGrad.addColorStop(0,   'transparent');
  lineGrad.addColorStop(0.2, 'rgba(0,229,255,0.4)');
  lineGrad.addColorStop(0.8, 'rgba(0,229,255,0.4)');
  lineGrad.addColorStop(1,   'transparent');
  ctx.strokeStyle = lineGrad;
  ctx.lineWidth   = 1;
  ctx.beginPath();
  ctx.moveTo(0, groundY);
  ctx.lineTo(canvas._w, groundY);
  ctx.stroke();
}

function drawPlayer() {
  // Draw motion trail
  for (let i = 0; i < player.trail.length; i++) {
    const t    = player.trail[i];
    const frac = (i + 1) / player.trail.length;
    ctx.save();
    ctx.globalAlpha = frac * 0.25;
    ctx.fillStyle   = '#00e5ff';
    ctx.shadowColor = '#00e5ff';
    ctx.shadowBlur  = 12;
    ctx.beginPath();
    roundRect(ctx, t.x, t.y, player.size, player.size, 6);
    ctx.fill();
    ctx.restore();
  }

  // Glow pulse
  const pulse = 0.7 + 0.3 * Math.sin(state.frame * 0.1);

  ctx.save();
  // Outer glow
  ctx.shadowColor = '#00e5ff';
  ctx.shadowBlur  = 20 * pulse;
  ctx.fillStyle   = 'rgba(0,229,255,0.15)';
  const glowPad = 6;
  ctx.beginPath();
  roundRect(ctx, player.x - glowPad, player.y - glowPad,
            player.size + glowPad * 2, player.size + glowPad * 2, 10);
  ctx.fill();

  // Main body gradient
  const bodyGrad = ctx.createLinearGradient(
    player.x, player.y,
    player.x + player.size, player.y + player.size
  );
  bodyGrad.addColorStop(0, '#00e5ff');
  bodyGrad.addColorStop(1, '#0077b6');
  ctx.fillStyle = bodyGrad;
  ctx.beginPath();
  roundRect(ctx, player.x, player.y, player.size, player.size, 6);
  ctx.fill();

  // Shine
  ctx.fillStyle = 'rgba(255,255,255,0.25)';
  ctx.beginPath();
  roundRect(ctx, player.x + 4, player.y + 4, player.size / 2 - 4, 4, 3);
  ctx.fill();

  ctx.restore();
}

function drawBugs() {
  const t = state.frame;
  ctx.font = `${BUG_SIZE}px serif`;
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  for (const bug of bugs) {
    ctx.save();
    // Spinning fall effect
    const cx = bug.x + bug.size / 2;
    const cy = bug.y + bug.size / 2;
    ctx.translate(cx, cy);
    ctx.rotate(Math.sin(t * 0.05 + bug.wobble) * 0.3);
    ctx.fillText(bug.emoji, 0, 0);
    ctx.restore();
  }
}

/** Polyfill for ctx.roundRect (fallback for older browsers) */
function roundRect(ctx, x, y, w, h, r) {
  if (ctx.roundRect) {
    ctx.roundRect(x, y, w, h, r);
  } else {
    ctx.moveTo(x + r, y);
    ctx.lineTo(x + w - r, y);
    ctx.quadraticCurveTo(x + w, y, x + w, y + r);
    ctx.lineTo(x + w, y + h - r);
    ctx.quadraticCurveTo(x + w, y + h, x + w - r, y + h);
    ctx.lineTo(x + r, y + h);
    ctx.quadraticCurveTo(x, y + h, x, y + h - r);
    ctx.lineTo(x, y + r);
    ctx.quadraticCurveTo(x, y, x + r, y);
    ctx.closePath();
  }
}

// ─── Game Loop ────────────────────────────────────────────────────────────────

let lastTime   = 0;
let rafId      = null;
let spawnTimer = 0;

function spawnInterval() {
  // Spawn faster as level increases
  return Math.max(25, BUG_SPAWN_BASE - (state.level - 1) * 8);
}

function gameLoop(timestamp) {
  if (!state.running) return;

  rafId = requestAnimationFrame(gameLoop);

  const dt = Math.min(timestamp - lastTime, 50); // cap at 50ms to avoid spiral of death
  lastTime = timestamp;

  state.frame++;

  // ── Update Score & Level ──
  updateScore(dt);

  // ── Update Player ──
  player.trail.push({ x: player.x, y: player.y });
  if (player.trail.length > 6) player.trail.shift();

  if (isLeft())  player.vx = -PLAYER_SPEED;
  else if (isRight()) player.vx = PLAYER_SPEED;
  else player.vx *= 0.7;  // friction

  player.x += player.vx;
  player.x  = Math.max(0, Math.min(canvas._w - player.size, player.x));

  // ── Spawn Bugs ──
  spawnTimer++;
  if (spawnTimer >= spawnInterval()) {
    spawnBug();
    // Occasionally double-spawn at higher levels
    if (state.level >= 4 && Math.random() < 0.3) spawnBug();
    spawnTimer = 0;
  }

  // ── Update Bugs ──
  bugs = bugs.filter(bug => bug.y < canvas._h + BUG_SIZE * 2);
  for (const bug of bugs) {
    bug.y += bug.speed;
    // Gentle horizontal wobble
    bug.x += Math.sin(state.frame * 0.05 + bug.wobble) * bug.wobbleAmp;
    // Keep in bounds
    bug.x  = Math.max(0, Math.min(canvas._w - bug.size, bug.x));

    // Collision
    if (rectsOverlap(player.x, player.y, player.size, player.size,
                     bug.x,    bug.y,    bug.size,   bug.size)) {
      spawnExplosion(player.x + player.size / 2, player.y + player.size / 2);
      endGame();
      return;
    }
  }

  // ── Update Particles ──
  updateParticles();

  // ── Draw ──
  drawBackground();
  drawParticles();
  drawBugs();
  drawPlayer();

  // Update HUD
  scoreDisplay.textContent = state.score;
  bestDisplay.textContent  = state.best;
  levelDisplay.textContent = state.level;
}

// ─── Game Lifecycle ──────────────────────────────────────────────────────────

function startGame() {
  resizeCanvas();

  // Reset state
  state.running   = true;
  state.score     = 0;
  state.level     = 1;
  state.frame     = 0;
  spawnTimer      = 0;
  scoreTimer      = 0;
  bugs            = [];
  particles       = [];

  scoreDisplay.textContent = '0';
  levelDisplay.textContent = '1';

  initPlayer();
  hideOverlays();

  lastTime = performance.now();
  rafId    = requestAnimationFrame(gameLoop);
}

function endGame() {
  state.running = false;
  cancelAnimationFrame(rafId);

  // Draw one last frame (with explosion particles)
  const drawLast = (ts) => {
    drawBackground();
    updateParticles();
    drawParticles();
    if (particles.length > 0) requestAnimationFrame(drawLast);
  };
  requestAnimationFrame(drawLast);

  // Update best score
  if (state.score > state.best) {
    state.best = state.score;
    localStorage.setItem('bugdodger_best', state.best);
  }

  // Show game-over screen after short delay (let explosion play)
  setTimeout(() => {
    finalScore.textContent = state.score;
    finalBest.textContent  = state.best;
    finalLevel.textContent = state.level;
    bestDisplay.textContent = state.best;
    showOverlay(gameOverScreen);
  }, 600);
}

function showOverlay(el) {
  el.classList.add('active');
}

function hideOverlays() {
  startScreen.classList.remove('active');
  gameOverScreen.classList.remove('active');
}

// ─── Button Listeners ────────────────────────────────────────────────────────

startBtn.addEventListener('click', startGame);
restartBtn.addEventListener('click', startGame);

menuBtn.addEventListener('click', () => {
  hideOverlays();
  showOverlay(startScreen);
});

// ─── Keyboard shortcuts on overlays ─────────────────────────────────────────

window.addEventListener('keydown', (e) => {
  if (e.key === 'Enter' || e.key === ' ') {
    if (startScreen.classList.contains('active'))    { e.preventDefault(); startGame(); }
    if (gameOverScreen.classList.contains('active')) { e.preventDefault(); startGame(); }
  }
});

// ─── Init ────────────────────────────────────────────────────────────────────

resizeCanvas();
bestDisplay.textContent = state.best;

// Draw a static preview background on load
drawBackground();
