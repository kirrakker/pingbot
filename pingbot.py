import os
import time
import threading
import requests
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

TARGET_LINK = os.environ.get("TARGET_LINK", "")
INTERVAL_FILE = "/tmp/pingbot_interval.txt"

# ── Interval okuma/yazma (tüm worker'lar aynı dosyayı görür) ──
def read_interval():
    try:
        with open(INTERVAL_FILE, "r") as f:
            return max(10, min(300, int(f.read().strip())))
    except:
        return 60

def write_interval(val):
    with open(INTERVAL_FILE, "w") as f:
        f.write(str(val))

# İlk başta dosyayı oluştur
if not os.path.exists(INTERVAL_FILE):
    write_interval(60)

# Global state
ping_status = {
    "last_time": "Henüz ping atılmadı",
    "last_code": "-",
    "last_ok": None,
    "total": 0,
    "success": 0,
}

pinger_event = threading.Event()

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
    overflow: hidden;
    animation: flicker 8s infinite;
  }

  body::before {
    content: '';
    position: fixed; inset: 0;
    background: repeating-linear-gradient(
      0deg, transparent, transparent 2px,
      rgba(0,255,255,0.015) 2px, rgba(0,255,255,0.015) 4px
    );
    pointer-events: none; z-index: 999;
  }

  @keyframes flicker {
    0%,94%,100% { opacity: 1; }
    92%          { opacity: 0.92; }
  }

  /* TOPBAR */
  .topbar {
    border-bottom: 1px solid var(--cyan);
    padding: 0.6rem 1.5rem;
    display: flex; align-items: center; justify-content: space-between;
    background: var(--panel);
    box-shadow: 0 0 20px var(--cyan-glow);
  }
  .topbar-title { font-size: 0.85rem; letter-spacing: 0.2em; text-shadow: 0 0 8px var(--cyan); }
  #clock { color: var(--cyan-dim); font-size: 0.75rem; }

  /* MAIN */
  main {
    display: grid;
    grid-template-columns: 1fr 340px;
    overflow: hidden;
  }

  /* LOG */
  .log-panel { border-right: 1px solid var(--border); display: flex; flex-direction: column; overflow: hidden; }
  .panel-header {
    font-size: 0.72rem; letter-spacing: 0.18em;
    text-shadow: 0 0 6px var(--cyan);
    padding: 0.6rem 1.2rem;
    border-bottom: 1px solid var(--border); background: var(--panel);
  }
  .log-body {
    flex: 1; overflow-y: auto;
    padding: 1rem 1.2rem; font-size: 0.8rem; line-height: 1.9;
  }
  .log-body::-webkit-scrollbar { width: 4px; }
  .log-body::-webkit-scrollbar-thumb { background: var(--muted); }
  .log-entry { display: flex; gap: 1rem; }
  .ts  { color: var(--muted); flex-shrink: 0; }
  .msg { color: var(--cyan-dim); }
  .msg.ok  { color: var(--green); text-shadow: 0 0 6px var(--green); }
  .msg.err { color: var(--red);   text-shadow: 0 0 6px var(--red); }
  .cursor::after { content: '_'; animation: blink 1s step-end infinite; }
  @keyframes blink { 50% { opacity: 0; } }

  /* STATUS PANEL */
  .status-panel { display: flex; flex-direction: column; overflow-y: auto; }
  .status-section { border-bottom: 1px solid var(--border); padding: 1rem 1.2rem; }
  .section-label {
    font-size: 0.68rem; letter-spacing: 0.2em;
    text-shadow: 0 0 6px var(--cyan); margin-bottom: 0.8rem;
  }

  .status-badge { display: flex; align-items: center; gap: 0.6rem; font-size: 0.9rem; letter-spacing: 0.1em; margin-bottom: 0.4rem; }
  .dot { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }
  .dot.ok   { background: var(--green); animation: pdot 1.4s ease-in-out infinite; }
  .dot.err  { background: var(--red); }
  .dot.idle { background: var(--muted); }
  @keyframes pdot { 0%,100%{box-shadow:0 0 6px var(--green)} 50%{box-shadow:0 0 16px var(--green)} }
  .status-badge.ok   { color: var(--green); text-shadow: 0 0 8px var(--green); }
  .status-badge.err  { color: var(--red);   text-shadow: 0 0 8px var(--red); }
  .status-badge.idle { color: var(--muted); }

  .data-row { display: flex; flex-direction: column; gap: 0.15rem; margin-bottom: 0.8rem; }
  .data-row:last-child { margin-bottom: 0; }
  .data-key { font-size: 0.62rem; letter-spacing: 0.15em; color: var(--muted); }
  .data-val { font-size: 0.8rem; color: var(--cyan-dim); }
  .data-val.ok  { color: var(--green); }
  .data-val.err { color: var(--red); }

  .stats-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 0.6rem; }
  .stat-box { border: 1px solid var(--border); padding: 0.7rem; text-align: center; }
  .stat-num { font-size: 1.6rem; line-height: 1; }
  .stat-num.t { color: var(--cyan);  text-shadow: 0 0 10px var(--cyan); }
  .stat-num.s { color: var(--green); text-shadow: 0 0 10px var(--green); }
  .stat-lbl { font-size: 0.6rem; letter-spacing: 0.12em; color: var(--muted); margin-top: 0.3rem; }

  /* INTERVAL */
  .interval-section { border-bottom: 1px solid var(--border); padding: 1rem 1.2rem; }
  .interval-val {
    font-size: 1.6rem; color: var(--cyan); text-shadow: 0 0 10px var(--cyan);
    margin-bottom: 0.6rem;
  }
  .interval-val small { font-size: 0.7rem; color: var(--muted); }

  input[type=range] {
    -webkit-appearance: none; width: 100%; height: 3px;
    background: var(--border); outline: none; cursor: pointer; display: block; margin-bottom: 0.7rem;
  }
  input[type=range]::-webkit-slider-thumb {
    -webkit-appearance: none; width: 16px; height: 16px;
    border-radius: 50%; background: var(--cyan); box-shadow: 0 0 8px var(--cyan); cursor: pointer;
  }

  .presets { display: flex; gap: 0.4rem; margin-bottom: 0.7rem; }
  .pre {
    flex: 1; background: transparent; border: 1px solid var(--border);
    color: var(--muted); font-family: var(--mono); font-size: 0.65rem;
    padding: 0.3rem 0; cursor: pointer; transition: all 0.15s; text-align: center;
  }
  .pre:hover { border-color: var(--cyan); color: var(--cyan); }
  .pre.active { border-color: var(--cyan); color: var(--cyan); text-shadow: 0 0 6px var(--cyan); box-shadow: 0 0 6px var(--cyan-glow); }

  .apply {
    width: 100%; background: transparent; border: 1px solid var(--cyan);
    color: var(--cyan); font-family: var(--mono); font-size: 0.72rem;
    letter-spacing: 0.12em; padding: 0.5rem; cursor: pointer; transition: all 0.15s;
    text-shadow: 0 0 6px var(--cyan); display: block; margin-bottom: 0.5rem;
  }
  .apply:hover { background: var(--cyan-glow); }
  .apply:disabled { opacity: 0.4; cursor: not-allowed; }

  .toast { font-size: 0.68rem; letter-spacing: 0.08em; min-height: 1.1rem; transition: opacity 0.3s; }
  .toast.ok-msg  { color: var(--green); }
  .toast.err-msg { color: var(--red); }
  .toast.hide { opacity: 0; }

  /* REFRESH */
  .refresh-bar {
    padding: 0.8rem 1.2rem; border-top: 1px solid var(--border);
    display: flex; align-items: center; justify-content: space-between; margin-top: auto;
  }
  .refresh-bar span { font-size: 0.68rem; color: var(--muted); }
  .rbtn {
    background: transparent; border: 1px solid var(--cyan);
    color: var(--cyan); font-family: var(--mono); font-size: 0.68rem;
    padding: 0.35rem 0.8rem; cursor: pointer; transition: all 0.15s;
    text-shadow: 0 0 6px var(--cyan);
  }
  .rbtn:hover { background: var(--cyan-glow); }

  /* BOTTOM */
  .bottombar {
    border-top: 1px solid var(--cyan); padding: 0.4rem 1.5rem;
    background: var(--panel);
    display: flex; justify-content: space-between;
    font-size: 0.65rem; color: var(--muted); letter-spacing: 0.1em;
  }
</style>
</head>
<body>

<div class="topbar">
  <span class="topbar-title">PINGBOT // SYSTEM STATUS MONITOR</span>
  <span id="clock">--:--:--</span>
</div>

<main>
  <!-- LOG -->
  <div class="log-panel">
    <div class="panel-header">SYSTEM BROADCAST LOGS | PING.LOG</div>
    <div class="log-body">
      {% if last_ok == true %}
        <div class="log-entry"><span class="ts">{{ last_time }}</span><span class="msg ok">>> PING OK — [TARGET CLASSIFIED] [HTTP {{ last_code }}]</span></div>
      {% elif last_ok == false %}
        <div class="log-entry"><span class="ts">{{ last_time }}</span><span class="msg err">>> PING FAILED — [TARGET CLASSIFIED] [{{ last_code }}]</span></div>
      {% else %}
        <div class="log-entry"><span class="ts">--:--:--</span><span class="msg">>> SYSTEM INIT — WAITING FOR FIRST PING...</span></div>
      {% endif %}
      <div class="log-entry"><span class="ts"></span><span class="msg cursor"></span></div>
    </div>
  </div>

  <!-- STATUS -->
  <div class="status-panel">

    <div class="status-section">
      <div class="section-label">BOT CONTROL</div>
      {% if last_ok == true %}
        <div class="status-badge ok"><div class="dot ok"></div>ONLINE</div>
      {% elif last_ok == false %}
        <div class="status-badge err"><div class="dot err"></div>ERROR</div>
      {% else %}
        <div class="status-badge idle"><div class="dot idle"></div>STANDBY</div>
      {% endif %}
      <div style="font-size:0.65rem;color:var(--muted);margin-top:0.4rem;">pingbot.py</div>
    </div>

    <div class="status-section">
      <div class="section-label">PING STATUS</div>
      <div class="data-row">
        <span class="data-key">TARGET_URL</span>
        <span class="data-val" style="color:var(--muted);font-style:italic;">[CLASSIFIED]</span>
      </div>
      <div class="data-row">
        <span class="data-key">LAST_PING</span>
        <span class="data-val">{{ last_time }}</span>
      </div>
      <div class="data-row">
        <span class="data-key">HTTP_STATUS</span>
        {% if last_ok == true %}
          <span class="data-val ok">{{ last_code }}</span>
        {% elif last_ok == false %}
          <span class="data-val err">{{ last_code }}</span>
        {% else %}
          <span class="data-val">---</span>
        {% endif %}
      </div>
    </div>

    <div class="status-section">
      <div class="section-label">STATISTICS</div>
      <div class="stats-grid">
        <div class="stat-box"><div class="stat-num t">{{ total }}</div><div class="stat-lbl">TOTAL PINGS</div></div>
        <div class="stat-box"><div class="stat-num s">{{ success }}</div><div class="stat-lbl">SUCCESS</div></div>
      </div>
    </div>

    <!-- INTERVAL -->
    <div class="interval-section">
      <div class="section-label">PING INTERVAL</div>
      <div class="interval-val" id="dispVal">{{ interval }} <small>saniye</small></div>
      <input type="range" id="slider" min="10" max="300" step="5" value="{{ interval }}">
      <div class="presets">
        <button class="pre" data-val="30">30s</button>
        <button class="pre" data-val="60">1dk</button>
        <button class="pre" data-val="120">2dk</button>
        <button class="pre" data-val="300">5dk</button>
      </div>
      <button class="apply" id="applyBtn">[ APPLY ]</button>
      <div class="toast hide" id="toast"></div>
    </div>

    <div class="refresh-bar">
      <span>AUTO-REFRESH: <span id="cd">30</span>s</span>
      <button class="rbtn" id="refreshBtn">[ REFRESH ]</button>
    </div>

  </div>
</main>

<div class="bottombar">
  <span>PING INTERVAL: <span id="botInterval">{{ interval }}</span>s // RENDER UPTIME BOT</span>
  <span>STATUS: ACTIVE</span>
</div>

<script>
(function() {
  // ── Saat ──
  function tick() {
    document.getElementById('clock').textContent = new Date().toTimeString().slice(0, 8);
  }
  tick();
  setInterval(tick, 1000);

  // ── Sayaç ──
  var countdown = 30;
  var cdEl = document.getElementById('cd');
  setInterval(function() {
    countdown--;
    cdEl.textContent = countdown;
    if (countdown <= 0) location.reload();
  }, 1000);

  // ── Refresh butonu ──
  document.getElementById('refreshBtn').addEventListener('click', function() {
    location.reload();
  });

  // ── Slider ──
  var slider   = document.getElementById('slider');
  var dispVal  = document.getElementById('dispVal');
  var presets  = document.querySelectorAll('.pre');
  var applyBtn = document.getElementById('applyBtn');
  var toast    = document.getElementById('toast');

  function updateDisplay(val) {
    dispVal.innerHTML = val + ' <small>saniye</small>';
    presets.forEach(function(b) {
      b.classList.toggle('active', parseInt(b.dataset.val) === parseInt(val));
    });
  }

  slider.addEventListener('input', function() {
    updateDisplay(this.value);
  });

  // ── Preset butonları ──
  presets.forEach(function(btn) {
    btn.addEventListener('click', function() {
      var v = this.dataset.val;
      slider.value = v;
      updateDisplay(v);
    });
  });

  // İlk render'da aktif preset'i işaretle
  updateDisplay(slider.value);

  // ── Apply ──
  applyBtn.addEventListener('click', function() {
    var val = parseInt(slider.value);
    applyBtn.disabled = true;
    applyBtn.textContent = '[ APPLYING... ]';
    toast.className = 'toast hide';

    fetch('/set_interval', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ interval: val })
    })
    .then(function(r) { return r.json(); })
    .then(function(data) {
      toast.textContent = '>> INTERVAL SET: ' + data.interval + 's';
      toast.className = 'toast ok-msg';
      document.getElementById('botInterval').textContent = data.interval;
      applyBtn.textContent = '[ APPLY ]';
      applyBtn.disabled = false;
      setTimeout(function() { toast.className = 'toast hide'; }, 3000);
    })
    .catch(function() {
      toast.textContent = '>> ERROR: COULD NOT UPDATE';
      toast.className = 'toast err-msg';
      applyBtn.textContent = '[ APPLY ]';
      applyBtn.disabled = false;
    });
  });
})();
</script>
</body>
</html>
"""

def pinger():
    time.sleep(10)
    while True:
        interval = read_interval()
        if TARGET_LINK:
            try:
                resp = requests.get(TARGET_LINK, timeout=15)
                ping_status["last_time"] = time.strftime('%d.%m.%Y %H:%M:%S')
                ping_status["last_code"] = resp.status_code
                ping_status["last_ok"]   = True
                ping_status["success"]  += 1
                print(f"[{ping_status['last_time']}] OK ({resp.status_code})")
            except Exception as e:
                ping_status["last_time"] = time.strftime('%d.%m.%Y %H:%M:%S')
                ping_status["last_code"] = "HATA"
                ping_status["last_ok"]   = False
                print(f"[{ping_status['last_time']}] FAIL: {e}")
            ping_status["total"] += 1

        pinger_event.wait(timeout=interval)
        pinger_event.clear()

threading.Thread(target=pinger, daemon=True).start()

@app.route('/')
def index():
    return render_template_string(
        HTML_PAGE,
        last_time=ping_status["last_time"],
        last_code=ping_status["last_code"],
        last_ok=ping_status["last_ok"],
        total=ping_status["total"],
        success=ping_status["success"],
        interval=read_interval(),
    )

@app.route('/set_interval', methods=['POST'])
def set_interval():
    data = request.get_json(force=True)
    val  = max(10, min(300, int(data.get('interval', 60))))
    write_interval(val)
    pinger_event.set()
    print(f"[{time.strftime('%H:%M:%S')}] Interval -> {val}s")
    return jsonify({"interval": val})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
