import os
import time
import threading
import requests
from flask import Flask, render_template_string

app = Flask(__name__)

TARGET_LINK = os.environ.get("TARGET_LINK", "Link Ayarlanmamış")

# Ping durumunu tutan global değişkenler
ping_status = {
    "last_time": "Henüz ping atılmadı",
    "last_code": "-",
    "last_ok": None,
    "total": 0,
    "success": 0,
}

HTML_PAGE = """<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>PINGBOT // SYSTEM STATUS</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&display=swap');

  :root {
    --cyan: #00ffff;
    --cyan-dim: #00cccc;
    --cyan-glow: rgba(0,255,255,0.15);
    --red: #ff2244;
    --green: #00ff88;
    --bg: #000000;
    --panel: #020d0d;
    --border: #00ffff33;
    --muted: #006666;
    --mono: 'Share Tech Mono', monospace;
  }

  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

  body {
    background: var(--bg);
    color: var(--cyan);
    font-family: var(--mono);
    min-height: 100vh;
    display: grid;
    grid-template-rows: auto 1fr auto;
    grid-template-columns: 1fr;
    overflow: hidden;
    position: relative;
  }

  /* Scanline overlay */
  body::before {
    content: '';
    position: fixed;
    inset: 0;
    background: repeating-linear-gradient(
      0deg,
      transparent,
      transparent 2px,
      rgba(0,255,255,0.015) 2px,
      rgba(0,255,255,0.015) 4px
    );
    pointer-events: none;
    z-index: 999;
  }

  /* CRT flicker */
  @keyframes flicker {
    0%,100% { opacity: 1; }
    92% { opacity: 1; }
    93% { opacity: 0.92; }
    94% { opacity: 1; }
  }
  body { animation: flicker 8s infinite; }

  /* ── TOPBAR ── */
  .topbar {
    border-bottom: 1px solid var(--cyan);
    padding: 0.6rem 1.5rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: var(--panel);
    box-shadow: 0 0 20px var(--cyan-glow);
  }

  .topbar-title {
    font-size: 0.85rem;
    letter-spacing: 0.2em;
    color: var(--cyan);
    text-shadow: 0 0 8px var(--cyan);
  }

  .topbar-right {
    font-size: 0.75rem;
    color: var(--muted);
    letter-spacing: 0.1em;
  }

  #clock { color: var(--cyan-dim); }

  /* ── MAIN LAYOUT ── */
  main {
    display: grid;
    grid-template-columns: 1fr 340px;
    height: 100%;
    overflow: hidden;
  }

  /* ── LEFT: LOG PANEL ── */
  .log-panel {
    border-right: 1px solid var(--border);
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }

  .panel-header {
    font-size: 0.72rem;
    letter-spacing: 0.18em;
    color: var(--cyan);
    text-shadow: 0 0 6px var(--cyan);
    padding: 0.6rem 1.2rem;
    border-bottom: 1px solid var(--border);
    background: var(--panel);
  }

  .log-body {
    flex: 1;
    overflow-y: auto;
    padding: 1rem 1.2rem;
    font-size: 0.8rem;
    line-height: 1.8;
    color: var(--cyan-dim);
  }

  .log-body::-webkit-scrollbar { width: 4px; }
  .log-body::-webkit-scrollbar-track { background: transparent; }
  .log-body::-webkit-scrollbar-thumb { background: var(--muted); }

  .log-entry { display: flex; gap: 1rem; }
  .log-entry .ts { color: var(--muted); flex-shrink: 0; }
  .log-entry .msg { color: var(--cyan-dim); }
  .log-entry .msg.ok { color: var(--green); text-shadow: 0 0 6px var(--green); }
  .log-entry .msg.err { color: var(--red); text-shadow: 0 0 6px var(--red); }

  .cursor-line::after {
    content: '_';
    animation: blink-cur 1s step-end infinite;
  }
  @keyframes blink-cur { 50% { opacity: 0; } }

  /* ── RIGHT: STATUS PANEL ── */
  .status-panel {
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }

  .status-section {
    border-bottom: 1px solid var(--border);
    padding: 1rem 1.2rem;
  }

  .section-label {
    font-size: 0.68rem;
    letter-spacing: 0.2em;
    color: var(--cyan);
    text-shadow: 0 0 6px var(--cyan);
    margin-bottom: 0.8rem;
  }

  /* Status badge */
  .status-badge {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    font-size: 0.9rem;
    letter-spacing: 0.1em;
    margin-bottom: 0.5rem;
  }
  .dot {
    width: 10px; height: 10px;
    border-radius: 50%;
    flex-shrink: 0;
  }
  .dot.ok  { background: var(--green); box-shadow: 0 0 10px var(--green); animation: pulse-dot 1.4s ease-in-out infinite; }
  .dot.err { background: var(--red);   box-shadow: 0 0 10px var(--red); }
  .dot.idle { background: var(--muted); }

  @keyframes pulse-dot {
    0%,100% { box-shadow: 0 0 6px var(--green); }
    50% { box-shadow: 0 0 16px var(--green); }
  }

  .status-badge.ok  { color: var(--green); text-shadow: 0 0 8px var(--green); }
  .status-badge.err { color: var(--red);   text-shadow: 0 0 8px var(--red); }
  .status-badge.idle { color: var(--muted); }

  /* Data rows */
  .data-row {
    display: flex;
    flex-direction: column;
    gap: 0.15rem;
    margin-bottom: 0.8rem;
  }
  .data-row:last-child { margin-bottom: 0; }

  .data-key {
    font-size: 0.62rem;
    letter-spacing: 0.15em;
    color: var(--muted);
  }

  .data-val {
    font-size: 0.8rem;
    color: var(--cyan-dim);
    word-break: break-all;
  }
  .data-val.url { color: var(--cyan); }
  .data-val.code-ok  { color: var(--green); }
  .data-val.code-err { color: var(--red); }

  /* Stats */
  .stats-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0.6rem;
  }

  .stat-box {
    border: 1px solid var(--border);
    padding: 0.7rem;
    text-align: center;
  }

  .stat-num {
    font-size: 1.6rem;
    line-height: 1;
  }
  .stat-num.total   { color: var(--cyan); text-shadow: 0 0 10px var(--cyan); }
  .stat-num.success { color: var(--green); text-shadow: 0 0 10px var(--green); }

  .stat-lbl {
    font-size: 0.6rem;
    letter-spacing: 0.12em;
    color: var(--muted);
    margin-top: 0.3rem;
  }

  /* Refresh */
  .refresh-section {
    margin-top: auto;
    padding: 1rem 1.2rem;
    border-top: 1px solid var(--border);
    display: flex;
    align-items: center;
    justify-content: space-between;
  }

  .refresh-section span {
    font-size: 0.68rem;
    color: var(--muted);
    letter-spacing: 0.08em;
  }

  .refresh-btn {
    background: transparent;
    border: 1px solid var(--cyan);
    color: var(--cyan);
    font-family: var(--mono);
    font-size: 0.68rem;
    letter-spacing: 0.1em;
    padding: 0.35rem 0.8rem;
    cursor: pointer;
    transition: all 0.15s;
    text-shadow: 0 0 6px var(--cyan);
    box-shadow: 0 0 8px var(--cyan-glow);
  }

  .refresh-btn:hover {
    background: var(--cyan-glow);
    box-shadow: 0 0 16px var(--cyan);
  }

  /* ── BOTTOM BAR ── */
  .bottombar {
    border-top: 1px solid var(--cyan);
    padding: 0.4rem 1.5rem;
    background: var(--panel);
    display: flex;
    justify-content: space-between;
    font-size: 0.65rem;
    color: var(--muted);
    letter-spacing: 0.1em;
    box-shadow: 0 0 20px var(--cyan-glow);
  }
</style>
</head>
<body>

<!-- TOPBAR -->
<div class="topbar">
  <span class="topbar-title">PINGBOT // SYSTEM STATUS MONITOR</span>
  <span class="topbar-right"><span id="clock">--:--:--</span></span>
</div>

<!-- MAIN -->
<main>

  <!-- LEFT: LOG -->
  <div class="log-panel">
    <div class="panel-header">SYSTEM BROADCAST LOGS | PING.LOG</div>
    <div class="log-body" id="logbox">
      <div class="log-entry">
        <span class="ts">{{ last_time if last_time != 'Henüz ping atılmadı' else '--:--:--' }}</span>
        {% if last_ok == true %}
          <span class="msg ok">>> PING OK — {{ url }} [HTTP {{ last_code }}]</span>
        {% elif last_ok == false %}
          <span class="msg err">>> PING FAILED — {{ url }} [{{ last_code }}]</span>
        {% else %}
          <span class="msg">>> SYSTEM INIT — WAITING FOR FIRST PING...</span>
        {% endif %}
      </div>
      <div class="log-entry">
        <span class="ts"></span>
        <span class="msg cursor-line"></span>
      </div>
    </div>
  </div>

  <!-- RIGHT: STATUS -->
  <div class="status-panel">

    <div class="status-section">
      <div class="section-label">BOT CONTROL</div>
      {% if last_ok == true %}
        <div class="status-badge ok"><div class="dot ok"></div> ONLINE</div>
      {% elif last_ok == false %}
        <div class="status-badge err"><div class="dot err"></div> ERROR</div>
      {% else %}
        <div class="status-badge idle"><div class="dot idle"></div> STANDBY</div>
      {% endif %}
      <div style="font-size:0.68rem; color:var(--muted); margin-top:0.4rem; letter-spacing:0.08em;">pingbot.py</div>
    </div>

    <div class="status-section">
      <div class="section-label">TARGET INFO</div>
      <div class="data-row">
        <span class="data-key">TARGET_URL</span>
        <span class="data-val url">{{ url }}</span>
      </div>
      <div class="data-row">
        <span class="data-key">LAST_PING</span>
        <span class="data-val">{{ last_time }}</span>
      </div>
      <div class="data-row">
        <span class="data-key">HTTP_STATUS</span>
        {% if last_ok == true %}
          <span class="data-val code-ok">{{ last_code }}</span>
        {% elif last_ok == false %}
          <span class="data-val code-err">{{ last_code }}</span>
        {% else %}
          <span class="data-val">---</span>
        {% endif %}
      </div>
    </div>

    <div class="status-section">
      <div class="section-label">STATISTICS</div>
      <div class="stats-grid">
        <div class="stat-box">
          <div class="stat-num total">{{ total }}</div>
          <div class="stat-lbl">TOTAL PINGS</div>
        </div>
        <div class="stat-box">
          <div class="stat-num success">{{ success }}</div>
          <div class="stat-lbl">SUCCESS</div>
        </div>
      </div>
    </div>

    <div class="refresh-section">
      <span>AUTO-REFRESH: <span id="cd">30</span>s</span>
      <button class="refresh-btn" onclick="location.reload()">[ REFRESH ]</button>
    </div>

  </div>
</main>

<!-- BOTTOM BAR -->
<div class="bottombar">
  <span>PING INTERVAL: 60s // RENDER UPTIME BOT</span>
  <span>STATUS: ACTIVE</span>
</div>

<script>
  // Clock
  function tick() {
    const now = new Date();
    document.getElementById('clock').textContent =
      now.toTimeString().slice(0,8);
  }
  tick();
  setInterval(tick, 1000);

  // Countdown
  let secs = 30;
  const cd = document.getElementById('cd');
  setInterval(() => {
    secs--;
    cd.textContent = secs;
    if (secs <= 0) location.reload();
  }, 1000);
</script>
</body>
</html>
"""

def pinger():
    """Arka planda her 60 saniyede bir hedef URL'e ping atar."""
    time.sleep(10)
    while True:
        if TARGET_LINK != "Link Ayarlanmamış":
            try:
                response = requests.get(TARGET_LINK, timeout=15)
                ping_status["last_time"] = time.strftime('%d.%m.%Y %H:%M:%S')
                ping_status["last_code"] = response.status_code
                ping_status["last_ok"] = True
                ping_status["success"] += 1
                print(f"[{ping_status['last_time']}] ✅ Ping OK: {TARGET_LINK} ({response.status_code})")
            except Exception as e:
                ping_status["last_time"] = time.strftime('%d.%m.%Y %H:%M:%S')
                ping_status["last_code"] = "HATA"
                ping_status["last_ok"] = False
                print(f"[{ping_status['last_time']}] ❌ Ping Hatası: {e}")
            ping_status["total"] += 1
        time.sleep(60)

# Render'da Gunicorn ile de çalışsın diye thread burada başlıyor
threading.Thread(target=pinger, daemon=True).start()

@app.route('/')
def index():
    return render_template_string(
        HTML_PAGE,
        url=TARGET_LINK,
        last_time=ping_status["last_time"],
        last_code=ping_status["last_code"],
        last_ok=ping_status["last_ok"],
        total=ping_status["total"],
        success=ping_status["success"],
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
