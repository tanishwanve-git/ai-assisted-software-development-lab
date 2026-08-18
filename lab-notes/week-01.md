# Week 01 — Bug Dodger

## Goal
Build a simple browser game using vanilla HTML, CSS, and JavaScript.

---

# Week 01 AI Log

## Tool Used
Antigravity AI (Claude Sonnet) — used as a pair programming assistant inside the editor.

---

## Prompt Given

1. *"Create a simple browser game called Bug Dodger using only HTML, CSS, and JavaScript."*
   — with a full list of rules: player square, falling bugs, arrow key movement, collision = game over, score over time, restart button.

2. *"The bugs are not clearly visible so change the visibility."*

3. *"Change the bug icon to a red shiny dot so that it is visible."*

4. *"Review this game code. Find at least five possible bugs, missing edge cases, or design problems. Do not rewrite yet."*

5. *"Fix the top three issues while keeping the code simple enough for a beginner to understand."*

---

## What AI Produced

- **`index.html`** — Full game shell with a HUD (Score, Best, Level), a start screen overlay, a game-over screen overlay with final stats, and a footer.
- **`style.css`** — A dark cyberpunk theme using CSS custom properties, Google Fonts (Orbitron), glassmorphism overlays, animated background grid, glowing buttons, and hover effects.
- **`game.js`** — Complete game engine including:
  - A `requestAnimationFrame` game loop with delta time (`dt`)
  - A player square with a motion trail and pulsing glow
  - Bug spawning with increasing difficulty per level
  - AABB (bounding box) collision detection
  - A particle explosion system on death
  - Score and level tracking via real elapsed time
  - Best score persistence using `localStorage`
- **`README.md`** and **`lab-notes/week-01.md`** — Project documentation
- **Bug visibility fix** — First added a white `shadowBlur` glow to the emoji. Then fully replaced the emoji with a hand-drawn red shiny 3D dot using canvas `radialGradient` and a specular highlight.
- **Three bug fixes** after a code review:
  - **Fix 1 (Frame-rate):** Converted all speeds from per-frame to per-second using `s = dt / 1000`, so the game runs identically on 60Hz and 144Hz monitors.
  - **Fix 2 (Mobile):** Added two on-screen `◀` `▶` touch buttons to the arena, wired up with `touchstart`/`touchend` events.
  - **Fix 3 (Blank canvas):** Added a single `drawBackground()` call inside the `resize` event listener so the canvas never goes blank when resizing on a non-running screen.

---

## What I Changed Manually

- Nothing in the source code was changed manually line-by-line.
- All Git operations were done manually in the terminal (clone, add, commit, push).
- Had to troubleshoot Git authentication — switched from HTTPS password login (which GitHub no longer supports) to SSH key authentication.
- Had to fix a tangled repo situation: accidentally deleted `.git`, re-initialised, renamed the folder, and corrected the remote URL manually before the first successful push.
- Used `git pull origin main --rebase` to resolve repeated "fetch first" push rejections caused by GitHub auto-generating commits remotely.

---

## How I Verified It

- Ran the game locally using `python3 -m http.server 8080` and opened `http://localhost:8080` in the browser.
- Played through the game to check: movement, bug spawning, collision, score incrementing, game-over screen, and restart.
- Did a high-level visual review of the files rather than a line-by-line read.
- Did not write any automated tests.

---

## What I Still Do Not Understand

- **Delta time (`dt`) and `s = dt / 1000`** — I understand *that* it fixes frame-rate dependency, but I'm not fully clear on *why* multiplying by seconds makes the speed consistent across different monitors.
- **`requestAnimationFrame`** — I know it drives the game loop, but I'm not sure how it decides when to fire or how it differs from `setInterval`.
- **`ctx.createRadialGradient()`** — The six parameters (two circles with x, y, radius) are confusing. I'm not clear on which circle is the "inner" highlight and which is the "outer" edge.
- **Git rebase vs merge** — I used `--rebase` when pulling, but I don't fully understand how it differs from a normal `git pull` and when I should choose one over the other.
- **`localStorage` crashing in private mode** — This was flagged as a known bug but not fixed yet. I don't know how to safely wrap it in a `try/catch` block.
