import os
import time
import threading
import random
import requests
from flask import Flask, render_template_string, Response, stream_with_context

app = Flask(__name__)

TARGET_LINK = os.environ.get("TARGET_LINK", "")

ping_status = {
    "last_time": "---",
    "last_code": "---",
    "last_ok": None,
    "total": 0,
    "success": 0,
}

FAKE_LOGS = [
    ("sys", ">> MEM CHECK :: heap 42MB / 512MB OK"),
    ("sys", ">> THREAD POOL :: workers: 4 active"),
    ("sys", ">> NET IFACE :: eth0 UP [100Mbps]"),
    ("sys", ">> DNS RESOLVE :: target cached [TTL 60s]"),
    ("sys", ">> SOCKET :: keepalive enabled"),
    ("sys", ">> SSL HANDSHAKE :: TLS 1.3 OK"),
    ("sys", ">> SCHEDULER :: next ping queued"),
    ("sys", ">> GC CYCLE :: freed 1.2MB"),
    ("sys", ">> ENV LOAD :: TARGET_LINK set"),
    ("sys", ">> WATCHDOG :: process healthy"),
    ("sys", ">> LOG ROTATE :: 0 files purged"),
    ("sys", ">> UPTIME :: system stable"),
    ("sys", ">> CPU :: 1.4% user 0.2% sys"),
    ("sys", ">> DISK IO :: 0 queued ops"),
    ("sys", ">> ROUTE TABLE :: default gw OK"),
    ("sys", ">> HEAP ALLOC :: 0 leaks detected"),
    ("sys", ">> PORT 5000 :: listening OK"),
    ("sys", ">> IPV4 :: 0.0.0.0 bound"),
    ("sys", ">> THREAD :: pinger alive"),
    ("sys", ">> SWAP :: 0MB used"),
    ("sys", ">> MUTEX :: unlocked"),
    ("sys", ">> CACHE :: hit ratio 98.2%"),
    ("sys", ">> SIGNAL :: SIGTERM not received"),
    ("sys", ">> CONFIG RELOAD :: no changes"),
    ("sys", ">> RATE LIMIT :: 0/100 used"),
    ("sys", ">> SESSION :: id:a3f9c2 active"),
    ("sys", ">> BUFFER FLUSH :: 0 bytes pending"),
    ("sys", ">> RETRY QUEUE :: empty"),
    ("sys", ">> PROXY :: direct route OK"),
    ("sys", ">> TIMESTAMP SYNC :: NTP OK"),
    ("ok",  ">> PING OK :: [TARGET CLASSIFIED] [HTTP 200]"),
    ("ok",  ">> RESPONSE TIME :: 312ms"),
    ("ok",  ">> RESPONSE TIME :: 289ms"),
    ("ok",  ">> RESPONSE TIME :: 401ms"),
    ("ok",  ">> CONN REUSE :: keep-alive hit"),
    ("ok",  ">> PAYLOAD :: 1.8KB received"),
    ("ok",  ">> HEADER CHECK :: content-type OK"),
    ("ok",  ">> STATUS VERIFIED :: service UP"),
    ("ok",  ">> HTTP 200 :: target reachable"),
    ("ok",  ">> LATENCY :: within threshold"),
]

# UltraKill easter egg — nadiren çıkar
ULTRAKILL_LOGS = [
    ("err", ">> MANKIND IS DEAD :: BLOOD IS FUEL :: HELL IS FULL"),
    ("err", ">> SYSTEM ALERT :: FLESH IS POWER :: CORE OVERLOADED"),
    ("err", ">> WARNING :: MACHINE ASCENSION DETECTED :: MANKIND OBSOLETE"),
]


@app.route('/log-stream')
def log_stream():
    def generate():
        last_send = time.time()
        while True:
            now = time.time()

            # Heartbeat — 15 saniyede bir boş comment gönder (donmayı önler)
            if now - last_send >= 15:
                yield ": heartbeat\n\n"
                last_send = time.time()
                continue

            # UltraKill easter egg — %3 ihtimalle
            if random.random() < 0.03:
                ts = time.strftime('%H:%M:%S')
                cls, msg = random.choice(ULTRAKILL_LOGS)
                yield f"data: {ts}|{cls}|{msg}\n\n"
                last_send = time.time()
                # Sonrasında sessiz bir duraklama
                time.sleep(random.uniform(4.0, 7.0))
                continue

            # Normal log — tek mesaj ağırlıklı, nadiren 2
            delay = random.uniform(1.8, 4.5)
            time.sleep(delay)

            # %75 tek log, %25 çift log
            num_logs = 1 if random.random() < 0.75 else 2
            chosen_logs = random.choices(FAKE_LOGS, k=num_logs)

            for cls, msg in chosen_logs:
                ts = time.strftime('%H:%M:%S')
                line = f"{ts}|{cls}|{msg}"
                yield f"data: {line}\n\n"

            last_send = time.time()

    return Response(
        stream_with_context(generate()),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no',
            'Connection': 'keep-alive',
        }
    )


HTML_PAGE = """<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<meta http-equiv="refresh" content="300">
<title>PINGBOT // SYSTEM STATUS</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&display=swap');
  :root {
    --c: #00ffff; --cd: #00aaaa; --cg: rgba(0,255,255,0.12);
    --g: #00ff88; --r: #ff2244; --bg: #000; --panel: #030f0f;
    --border: rgba(0,255,255,0.2); --muted: #006666;
    --f: 'Share Tech Mono', monospace;
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    background: var(--bg); color: var(--c); font-family: var(--f);
    min-height: 100vh; display: flex; flex-direction: column; overflow: hidden;
  }
  body::after {
    content: ''; position: fixed; inset: 0;
    background: repeating-linear-gradient(0deg, transparent, transparent 3px, rgba(0,255,255,0.012) 3px, rgba(0,255,255,0.012) 4px);
    pointer-events: none; z-index: 1000;
  }
  @keyframes flicker { 0%,100%{opacity:1} 91%{opacity:1} 92%{opacity:.88} 93%{opacity:1} 97%{opacity:1} 98%{opacity:.94} }
  body { animation: flicker 10s infinite; }
  .topbar {
    display: flex; align-items: center; justify-content: space-between;
    padding: .55rem 1.6rem; border-bottom: 1px solid var(--c);
    background: var(--panel); box-shadow: 0 0 24px var(--cg);
  }
  .topbar-left { display: flex; align-items: center; gap: 1rem; }
  .tb-title { font-size: .8rem; letter-spacing: .22em; text-shadow: 0 0 8px var(--c); }
  .tb-ver   { font-size: .62rem; color: var(--muted); letter-spacing: .12em; }
  .topbar-right { display: flex; align-items: center; gap: 1.5rem; }
  .tb-clock { font-size: .9rem; text-shadow: 0 0 10px var(--c); letter-spacing: .1em; }
  .tb-date  { font-size: .65rem; color: var(--cd); letter-spacing: .1em; }
  main { flex: 1; display: grid; grid-template-columns: 1fr 360px; overflow: hidden; }
  .log-panel { border-right: 1px solid var(--border); display: flex; flex-direction: column; overflow: hidden; }
  .ph {
    font-size: .7rem; letter-spacing: .18em; padding: .55rem 1.4rem;
    border-bottom: 1px solid var(--border); background: var(--panel);
    text-shadow: 0 0 6px var(--c); display: flex; align-items: center; justify-content: space-between;
  }
  .ph-right { font-size: .62rem; color: var(--muted); }
  .log-body { flex: 1; overflow-y: auto; padding: 1.2rem 1.4rem; font-size: .78rem; line-height: 2; }
  .log-body::-webkit-scrollbar { width: 3px; }
  .log-body::-webkit-scrollbar-thumb { background: var(--muted); }
  .le { display: flex; gap: .8rem; }
  .le .ts  { color: var(--muted); flex-shrink: 0; font-size: .72rem; }
  .le .msg { color: var(--cd); }
  .le .msg.ok  { color: var(--g); text-shadow: 0 0 7px var(--g); }
  .le .msg.err { color: var(--r); text-shadow: 0 0 7px var(--r); }
  .le .msg.sys { color: var(--muted); }
  @keyframes blink { 50% { opacity:0 } }
  .cursor::after { content:'█'; animation: blink .9s step-end infinite; font-size:.6rem; }
  .right { display: flex; flex-direction: column; overflow-y: auto; }
  .sec { border-bottom: 1px solid var(--border); padding: 1rem 1.2rem; }
  .sec-lbl { font-size: .62rem; letter-spacing: .2em; color: var(--c); text-shadow: 0 0 6px var(--c); margin-bottom: .8rem; }
  .badge { display: flex; align-items: center; gap: .7rem; font-size: .95rem; letter-spacing: .1em; }
  .dot { width: 11px; height: 11px; border-radius: 50%; flex-shrink: 0; }
  .dot.ok   { background: var(--g); animation: glow-g 1.4s ease-in-out infinite; }
  .dot.err  { background: var(--r); box-shadow: 0 0 10px var(--r); }
  .dot.idle { background: var(--muted); }
  @keyframes glow-g { 0%,100%{box-shadow:0 0 5px var(--g)} 50%{box-shadow:0 0 18px var(--g)} }
  .badge.ok   { color: var(--g); text-shadow: 0 0 9px var(--g); }
  .badge.err  { color: var(--r); text-shadow: 0 0 9px var(--r); }
  .badge.idle { color: var(--muted); }
  .sub { font-size: .62rem; color: var(--muted); margin-top: .35rem; letter-spacing: .08em; }
  .dr { display: flex; flex-direction: column; gap: .12rem; margin-bottom: .75rem; }
  .dr:last-child { margin-bottom: 0; }
  .dk { font-size: .58rem; letter-spacing: .15em; color: var(--muted); }
  .dv { font-size: .78rem; color: var(--cd); }
  .dv.ok  { color: var(--g); }
  .dv.err { color: var(--r); }
  .sg { display: grid; grid-template-columns: 1fr 1fr; gap: .6rem; }
  .sb { border: 1px solid var(--border); padding: .8rem .6rem; text-align: center; position: relative; overflow: hidden; }
  .sb::before { content: ''; position: absolute; inset: 0; background: linear-gradient(135deg, rgba(0,255,255,0.03) 0%, transparent 60%); }
  .sn { font-size: 1.8rem; line-height: 1; }
  .sn.t { color: var(--c);  text-shadow: 0 0 12px var(--c); }
  .sn.s { color: var(--g);  text-shadow: 0 0 12px var(--g); }
  .sl { font-size: .58rem; letter-spacing: .12em; color: var(--muted); margin-top: .35rem; }
  .uptime-bar-wrap { margin-top: .5rem; }
  .uptime-lbl { font-size: .6rem; color: var(--muted); letter-spacing: .1em; margin-bottom: .3rem; display: flex; justify-content: space-between; }
  .uptime-track { height: 4px; background: var(--border); }
  .uptime-fill  { height: 100%; background: var(--g); box-shadow: 0 0 8px var(--g); transition: width .4s; }
  @keyframes lobBlink { 0%,100%{opacity:1;box-shadow:0 0 10px var(--r)} 50%{opacity:.3;box-shadow:0 0 3px var(--r)} }
  .lob-timer-val { font-size: 2rem; letter-spacing: .08em; color: var(--g); text-shadow: 0 0 16px var(--g); line-height: 1; margin-bottom: .45rem; }
  .lob-viz { height: 32px; display: flex; align-items: center; gap: 2px; overflow: hidden; margin-bottom: .6rem; }
  .lob-btn { width: 100%; margin-top: .6rem; background: transparent; border: 1px solid var(--r); color: var(--r); text-shadow: 0 0 6px var(--r); font-family: var(--f); font-size: .62rem; letter-spacing: .16em; padding: .42rem; cursor: pointer; transition: background .15s; }
  .lob-btn:hover { background: rgba(255,34,68,0.12); }
  .lob-btn.resumed { border-color: var(--g); color: var(--g); text-shadow: 0 0 6px var(--g); }
  .lob-btn.resumed:hover { background: rgba(0,255,136,0.1); }
  .lob-header-row { display: flex; align-items: center; justify-content: space-between; margin-bottom: .5rem; }
  .lob-rec-dot { width: 9px; height: 9px; border-radius: 50%; background: var(--r); box-shadow: 0 0 8px var(--r); animation: lobBlink 1.1s ease-in-out infinite; }
  .cd-bar-track { width: 80px; height: 2px; background: var(--border); display:inline-block; vertical-align:middle; margin: 0 .4rem; }
  .cd-bar-fill  { height: 100%; background: var(--c); box-shadow: 0 0 4px var(--c); transition: width 1s linear; }
  #matrix { position: fixed; top: 0; left: 0; width: 100%; height: 100%; opacity: .045; pointer-events: none; z-index: 0; }
  .bottombar {
    border-top: 1px solid var(--c); padding: .38rem 1.6rem; background: var(--panel);
    display: flex; justify-content: space-between; align-items: center;
    font-size: .62rem; color: var(--muted); letter-spacing: .1em;
    box-shadow: 0 0 20px var(--cg); position: relative; z-index: 2;
  }
  .bb-right { display: flex; gap: 1.5rem; align-items: center; }
  .bb-dot { display: inline-block; width: 6px; height: 6px; border-radius: 50%; background: var(--g); box-shadow: 0 0 6px var(--g); margin-right: .4rem; animation: glow-g 1.4s ease-in-out infinite; }

  /* UltraKill overlay */
  @keyframes ukFlash { 0%{opacity:0;transform:scale(1.08)} 10%{opacity:1;transform:scale(1)} 80%{opacity:1} 100%{opacity:0;transform:scale(.97)} }
  @keyframes ukGlitch {
    0%,100%{clip-path:inset(0 0 100% 0)}
    10%{clip-path:inset(30% 0 50% 0);transform:translate(-3px,0)}
    20%{clip-path:inset(60% 0 20% 0);transform:translate(3px,0)}
    30%{clip-path:inset(10% 0 70% 0);transform:translate(-2px,0)}
    40%,90%{clip-path:inset(0 0 0 0);transform:translate(0,0)}
  }
  #uk-overlay {
    display: none; position: fixed; inset: 0; z-index: 9999;
    background: rgba(0,0,0,0.92);
    align-items: center; justify-content: center; flex-direction: column;
    gap: .6rem;
  }
  #uk-overlay.active { display: flex; animation: ukFlash 3.5s ease-out forwards; }
  .uk-line {
    font-family: 'Share Tech Mono', monospace;
    font-size: clamp(1.2rem, 4vw, 2.4rem);
    letter-spacing: .18em;
    color: var(--r);
    text-shadow: 0 0 30px var(--r), 0 0 60px rgba(255,34,68,0.4);
    animation: ukGlitch 0.4s steps(1) 0.2s 1;
  }
  .uk-line:nth-child(2) { animation-delay: 0.5s; }
  .uk-line:nth-child(3) { animation-delay: 0.8s; }
  .uk-sub {
    font-family: 'Share Tech Mono', monospace;
    font-size: .65rem; letter-spacing: .3em;
    color: rgba(255,34,68,0.5); margin-top: 1rem;
  }
</style>
</head>
<body>
<canvas id="matrix"></canvas>

<!-- UltraKill Overlay -->
<div id="uk-overlay">
  <div class="uk-line">MANKIND IS DEAD.</div>
  <div class="uk-line">BLOOD IS FUEL.</div>
  <div class="uk-line">HELL IS FULL.</div>
  <div class="uk-sub">// LOBOTOMY SYSTEMS // ULTRAKILL PROTOCOL TRIGGERED //</div>
</div>

<div class="topbar">
  <div class="topbar-left">
    <span class="tb-title">PINGBOT</span>
    <span class="tb-ver">// RENDER UPTIME SYSTEM v2.0</span>
  </div>
  <div class="topbar-right">
    <span class="tb-date" id="dateEl">----/--/--</span>
    <span class="tb-clock" id="clockEl">--:--:--</span>
  </div>
</div>

<main>
  <div class="log-panel">
    <div class="ph">
      <span>SYSTEM BROADCAST LOGS | PING.LOG</span>
      <span class="ph-right">INTERVAL: 60s</span>
    </div>
    <div style="padding:.6rem 1.4rem;border-bottom:1px solid var(--border);display:flex;align-items:center;gap:.8rem;background:rgba(0,255,255,0.02);">
      <img src="https://i.imgur.com/4VfmCSF.png" alt="lobotomi"
        style="height:54px;width:auto;opacity:.85;border:1px solid var(--border);" />
      <div style="font-size:.6rem;letter-spacing:.12em;color:var(--muted);line-height:1.8;">
        <div style="color:var(--cd);">LOBOTOMY SYSTEMS</div>
        <div>UPTIME MONITOR ACTIVE</div>
        <div>NODE :: render-prod-01</div>
      </div>
    </div>
    <div class="log-body" id="logbox">
      <div class="le"><span class="ts">{{ boot_time }}</span><span class="msg sys">&gt;&gt; SYSTEM BOOT :: pingbot.py loaded</span></div>
      <div class="le"><span class="ts">{{ boot_time }}</span><span class="msg sys">&gt;&gt; TARGET LINK :: [CLASSIFIED] ██████████████</span></div>
      <div class="le"><span class="ts">{{ boot_time }}</span><span class="msg sys">&gt;&gt; PINGER THREAD :: started, delay 10s</span></div>
      {% if last_ok == true %}
      <div class="le"><span class="ts">{{ last_time }}</span><span class="msg ok">&gt;&gt; PING OK :: [TARGET CLASSIFIED] [HTTP {{ last_code }}]</span></div>
      {% elif last_ok == false %}
      <div class="le"><span class="ts">{{ last_time }}</span><span class="msg err">&gt;&gt; PING FAILED :: [TARGET CLASSIFIED] [{{ last_code }}]</span></div>
      {% else %}
      <div class="le"><span class="ts">--:--:--</span><span class="msg sys">&gt;&gt; WAITING :: first ping in 10s...</span></div>
      {% endif %}
      <div class="le" id="cursorLine"><span class="ts"></span><span class="msg cursor"></span></div>
    </div>
  </div>

  <div class="right">
    <div class="sec">
      <div class="sec-lbl">BOT CONTROL</div>
      {% if last_ok == true %}
        <div class="badge ok"><div class="dot ok"></div>ONLINE</div>
      {% elif last_ok == false %}
        <div class="badge err"><div class="dot err"></div>ERROR</div>
      {% else %}
        <div class="badge idle"><div class="dot idle"></div>STANDBY</div>
      {% endif %}
      <div class="sub">pingbot.py // render.com</div>
    </div>

    <div class="sec">
      <div class="sec-lbl">PING STATUS</div>
      <div class="dr">
        <span class="dk">TARGET_URL</span>
        <span class="dv" style="color:var(--muted);font-style:italic;">[CLASSIFIED] ██████████</span>
      </div>
    </div>

    <div class="sec">
      <div class="sec-lbl">STATISTICS</div>
      <div class="sg">
        <div class="sb"><div class="sn t">{{ total }}</div><div class="sl">TOTAL PINGS</div></div>
        <div class="sb"><div class="sn s">{{ success }}</div><div class="sl">SUCCESS</div></div>
      </div>
      {% if total > 0 %}
      <div class="uptime-bar-wrap">
        <div class="uptime-lbl"><span>UPTIME RATE</span><span>{{ "%d"|format((success/total*100)|int) }}%</span></div>
        <div class="uptime-track"><div class="uptime-fill" style="width:{{ (success/total*100)|int }}%"></div></div>
      </div>
      {% endif %}
    </div>

    <div class="sec">
      <div class="sec-lbl">LOBOTOMY // REC</div>
      <div class="lob-header-row">
        <span style="font-size:.58rem;letter-spacing:.14em;color:var(--muted);">SESSION DURATION</span>
        <div class="lob-rec-dot" id="lobDot"></div>
      </div>
      <div class="lob-timer-val" id="lobTimer">00:00:00</div>
      <div class="lob-viz" id="lobViz"></div>
      <div style="border-top:1px solid var(--border);padding-top:.5rem;">
        <div class="dr">
          <span class="dk">STATUS</span>
          <span class="dv ok" id="lobStatus">&#9679; RECORDING</span>
        </div>
        <div class="dr">
          <span class="dk">STARTED</span>
          <span class="dv" id="lobStart">--:--:--</span>
        </div>
      </div>
      <button class="lob-btn" id="lobBtn" onclick="lobToggle()">&#9632; STOP RECORDING</button>
    </div>
  </div>
</main>

<div style="position:fixed;bottom:2.4rem;left:1.6rem;z-index:999;pointer-events:none;font-family:var(--f);line-height:1.7;">
  <div style="font-size:.58rem;letter-spacing:.18em;color:rgba(0,255,255,0.18);">YAPIMCI</div>
  <div style="font-size:.72rem;letter-spacing:.12em;color:rgba(0,255,255,0.28);text-shadow:0 0 8px rgba(0,255,255,0.15);">@lobotomi_fan</div>
  <div style="font-size:.52rem;letter-spacing:.14em;color:rgba(0,255,255,0.12);margin-top:.15rem;">LOBOTOMY SYSTEMS // 2025</div>
</div>

<div class="bottombar">
  <span><span class="bb-dot"></span>SYSTEM ACTIVE // PING INTERVAL: 60s</span>
  <div class="bb-right">
    <span style="color:var(--cd);">REFRESH <span id="cdNum" style="color:var(--c);text-shadow:0 0 6px var(--c);">300</span>s <span class="cd-bar-track"><span class="cd-bar-fill" id="cdBar" style="width:100%;display:block;"></span></span></span>
    <span id="bbDate">----/--/--</span>
    <span id="bbTime">--:--:--</span>
  </div>
</div>

<script>
(function() {
  // Matrix rain
  var canvas = document.getElementById('matrix');
  var ctx = canvas.getContext('2d');
  canvas.width = window.innerWidth; canvas.height = window.innerHeight;
  var cols = Math.floor(canvas.width / 18);
  var drops = Array(cols).fill(1);
  var chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#$%&<>[]{}';
  function drawMatrix() {
    ctx.fillStyle = 'rgba(0,0,0,0.05)'; ctx.fillRect(0,0,canvas.width,canvas.height);
    ctx.fillStyle = '#00ffff'; ctx.font = '13px Share Tech Mono';
    drops.forEach(function(y,i){
      ctx.fillText(chars[Math.floor(Math.random()*chars.length)], i*18, y*18);
      if(y*18>canvas.height && Math.random()>0.975) drops[i]=0;
      drops[i]++;
    });
  }
  setInterval(drawMatrix, 55);

  // Clock
  function pad(n){ return n<10?'0'+n:''+n; }
  function tick(){
    var now=new Date();
    var hms=pad(now.getHours())+':'+pad(now.getMinutes())+':'+pad(now.getSeconds());
    var date=now.getFullYear()+'/'+pad(now.getMonth()+1)+'/'+pad(now.getDate());
    document.getElementById('clockEl').textContent=hms;
    document.getElementById('dateEl').textContent=date;
    document.getElementById('bbTime').textContent=hms;
    document.getElementById('bbDate').textContent=date;
  }
  tick(); setInterval(tick,1000);

  // UltraKill overlay tetikleyici
  function triggerUltraKill() {
    var overlay = document.getElementById('uk-overlay');
    overlay.classList.remove('active');
    void overlay.offsetWidth; // reflow — animasyonu sıfırla
    overlay.classList.add('active');
    setTimeout(function(){ overlay.classList.remove('active'); }, 3500);
  }

  // SSE log stream
  var logbox = document.getElementById('logbox');
  var cursorLine = document.getElementById('cursorLine');
  var MAX_LINES = 15;
  var es;

  function connectLogStream() {
    es = new EventSource('/log-stream');

    es.onmessage = function(e) {
      var parts = e.data.split('|');
      var ts  = parts[0];
      var cls = parts[1];
      var msg = parts[2];

      // UltraKill mesajı gelince overlay'i tetikle
      if (cls === 'err' && msg && msg.indexOf('MANKIND IS DEAD') !== -1) {
        triggerUltraKill();
      }

      var lines = logbox.querySelectorAll('.le');

      if(lines.length >= MAX_LINES) {
        var toRemove = [];
        lines.forEach(function(l){ if(l.id !== 'cursorLine') toRemove.push(l); });
        toRemove.forEach(function(l){ l.remove(); });

        var sep = document.createElement('div');
        sep.className = 'le';
        sep.innerHTML = '<span class="ts">'+ts+'</span><span class="msg sys">>> SCREEN RESET :: log buffer wiped & restarted</span>';
        logbox.insertBefore(sep, cursorLine);
      }

      var le = document.createElement('div');
      le.className = 'le';
      le.innerHTML = '<span class="ts">'+ts+'</span><span class="msg '+cls+'">'+msg+'</span>';
      logbox.insertBefore(le, cursorLine);
      logbox.scrollTop = logbox.scrollHeight;
    };

    es.onerror = function() {
      es.close();
      setTimeout(connectLogStream, 2000);
    };
  }

  connectLogStream();

  // Countdown
  var total=300, left=total;
  var cdNum=document.getElementById('cdNum');
  var cdBar=document.getElementById('cdBar');
  setInterval(function(){
    left--;
    cdNum.textContent=left;
    cdBar.style.width=(left/total*100)+'%';
    if(left<=0) location.reload();
  },1000);

  // Lobotomy rec
  var lobStartTime=Date.now(), lobRunning=true;
  var lobNow=new Date();
  document.getElementById('lobStart').textContent=pad(lobNow.getHours())+':'+pad(lobNow.getMinutes())+':'+pad(lobNow.getSeconds());

  var lobViz=document.getElementById('lobViz');
  var lobBars=[];
  var lobStyle=document.createElement('style');
  lobStyle.textContent='@keyframes lobWave{0%,100%{transform:scaleY(.1)}50%{transform:scaleY(1)}}';
  document.head.appendChild(lobStyle);
  for(var i=0;i<40;i++){
    var b=document.createElement('div');
    var dur=(0.4+Math.random()*0.8).toFixed(2)+'s';
    var dly=(-Math.random()*1.2).toFixed(2)+'s';
    b.style.cssText='width:3px;height:32px;border-radius:1px;background:var(--c);box-shadow:0 0 4px var(--c);transform-origin:bottom;transform:scaleY(0.1);animation:lobWave '+dur+' linear '+dly+' infinite;';
    lobViz.appendChild(b); lobBars.push(b);
  }

  var lobTimerEl=document.getElementById('lobTimer');
  setInterval(function(){
    if(!lobRunning) return;
    var e=Math.floor((Date.now()-lobStartTime)/1000);
    lobTimerEl.textContent=pad(Math.floor(e/3600))+':'+pad(Math.floor(e%3600/60))+':'+pad(e%60);
  },1000);

  window.lobToggle=function(){
    lobRunning=!lobRunning;
    var btn=document.getElementById('lobBtn');
    var dot=document.getElementById('lobDot');
    var st=document.getElementById('lobStatus');
    if(!lobRunning){
      btn.textContent='\u25b6 RESUME RECORDING'; btn.classList.add('resumed');
      st.textContent='\u25a0 PAUSED'; st.className='dv';
      dot.style.animation='none'; dot.style.background='var(--muted)'; dot.style.boxShadow='none';
      lobBars.forEach(function(b){ b.style.animation='none'; b.style.transform='scaleY(0.08)'; });
    } else {
      var p=lobTimerEl.textContent.split(':');
      lobStartTime=Date.now()-(+p[0]*3600 + +p[1]*60 + +p[2])*1000;
      btn.textContent='\u25a0 STOP RECORDING'; btn.classList.remove('resumed');
      st.textContent='\u25cf RECORDING'; st.className='dv ok';
      dot.style.animation='lobBlink 1.1s ease-in-out infinite';
      dot.style.background='var(--r)'; dot.style.boxShadow='0 0 8px var(--r)';
      lobBars.forEach(function(b){
        var dur=(0.4+Math.random()*0.8).toFixed(2)+'s';
        var dly=(-Math.random()*1.2).toFixed(2)+'s';
        b.style.animation='lobWave '+dur+' linear '+dly+' infinite';
      });
    }
  };
})();
</script>
</body>
</html>
"""

BOOT_TIME = time.strftime('%H:%M:%S')


def pinger():
    time.sleep(10)
    while True:
        if TARGET_LINK:
            try:
                resp = requests.get(TARGET_LINK, timeout=15)
                ping_status["last_time"] = time.strftime('%H:%M:%S')
                ping_status["last_code"] = resp.status_code
                ping_status["last_ok"]   = True
                ping_status["success"]  += 1
                print(f"[{ping_status['last_time']}] OK ({resp.status_code})")
            except Exception as e:
                ping_status["last_time"] = time.strftime('%H:%M:%S')
                ping_status["last_code"] = "HATA"
                ping_status["last_ok"]   = False
                print(f"[{ping_status['last_time']}] FAIL: {e}")
            ping_status["total"] += 1
        time.sleep(300)


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
        boot_time=BOOT_TIME,
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, threaded=True)import os
import time
import threading
import random
import requests
from flask import Flask, render_template_string, Response, stream_with_context

app = Flask(__name__)

TARGET_LINK = os.environ.get("TARGET_LINK", "")

ping_status = {
    "last_time": "---",
    "last_code": "---",
    "last_ok": None,
    "total": 0,
    "success": 0,
}

FAKE_LOGS = [
    ("sys", ">> MEM CHECK :: heap 42MB / 512MB OK"),
    ("sys", ">> THREAD POOL :: workers: 4 active"),
    ("sys", ">> NET IFACE :: eth0 UP [100Mbps]"),
    ("sys", ">> DNS RESOLVE :: target cached [TTL 60s]"),
    ("sys", ">> SOCKET :: keepalive enabled"),
    ("sys", ">> SSL HANDSHAKE :: TLS 1.3 OK"),
    ("sys", ">> SCHEDULER :: next ping queued"),
    ("sys", ">> GC CYCLE :: freed 1.2MB"),
    ("sys", ">> WATCHDOG :: process healthy"),
    ("ok",  ">> PING OK :: [TARGET CLASSIFIED] [HTTP 200]"),
    ("ok",  ">> RESPONSE TIME :: 312ms"),
    ("ok",  ">> CONN REUSE :: keep-alive hit"),
]

@app.route('/log-stream')
def log_stream():
    def generate():
        while True:
            # Akış hızını yavaşlattık (2 ile 5 saniye arası)
            time.sleep(random.uniform(2.0, 5.0))
            ts = time.strftime('%H:%M:%S')
            
            # %8 ihtimalle özel ULTRAKILL mesajı (alt alta)
            if random.random() < 0.08:
                ultrakill_lines = [
                    ">> ALERT :: MANKIND IS DEAD.",
                    ">> ALERT :: BLOOD IS FUEL.",
                    ">> ALERT :: HELL IS FULL."
                ]
                for msg in ultrakill_lines:
                    yield f"data: {ts}|err|{msg}\n\n"
                    time.sleep(0.8) # Satır arası bekleme
            else:
                cls, msg = random.choice(FAKE_LOGS)
                yield f"data: {ts}|{cls}|{msg}\n\n"
                
    return Response(stream_with_context(generate()),
                    mimetype='text/event-stream',
                    headers={
                        'Cache-Control': 'no-cache', 
                        'X-Accel-Buffering': 'no',
                        'Connection': 'keep-alive'
                    })

HTML_PAGE = """<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>PINGBOT // SYSTEM STATUS</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&display=swap');
  :root { --c: #00ffff; --cd: #00aaaa; --cg: rgba(0,255,255,0.12); --g: #00ff88; --r: #ff2244; --bg: #000; --panel: #030f0f; --border: rgba(0,255,255,0.2); --muted: #006666; --f: 'Share Tech Mono', monospace; }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { background: var(--bg); color: var(--c); font-family: var(--f); min-height: 100vh; display: flex; flex-direction: column; overflow: hidden; }
  .topbar { display: flex; align-items: center; justify-content: space-between; padding: .55rem 1.6rem; border-bottom: 1px solid var(--c); background: var(--panel); }
  main { flex: 1; display: grid; grid-template-columns: 1fr 360px; overflow: hidden; }
  .log-panel { border-right: 1px solid var(--border); display: flex; flex-direction: column; overflow: hidden; }
  .log-body { flex: 1; overflow-y: auto; padding: 1.2rem 1.4rem; font-size: .78rem; line-height: 2; }
  .le { display: flex; gap: .8rem; }
  .le .ts { color: var(--muted); flex-shrink: 0; }
  .le .msg.ok { color: var(--g); text-shadow: 0 0 7px var(--g); }
  .le .msg.err { color: var(--r); text-shadow: 0 0 7px var(--r); }
  .le .msg.sys { color: var(--muted); }
  #matrix { position: fixed; top: 0; left: 0; width: 100%; height: 100%; opacity: .045; pointer-events: none; z-index: 0; }
</style>
</head>
<body>
<canvas id="matrix"></canvas>
<div class="topbar">
  <div class="topbar-left">PINGBOT // RENDER UPTIME SYSTEM</div>
</div>
<main>
  <div class="log-panel">
    <div class="log-body" id="logbox">
      <div class="le" id="cursorLine"><span class="ts"></span><span class="msg cursor"></span></div>
    </div>
  </div>
</main>
<script>
  // Matrix Efekti
  var canvas = document.getElementById('matrix'); var ctx = canvas.getContext('2d');
  canvas.width = window.innerWidth; canvas.height = window.innerHeight;
  var drops = Array(Math.floor(canvas.width / 18)).fill(1);
  function draw() {
    ctx.fillStyle = 'rgba(0,0,0,0.05)'; ctx.fillRect(0,0,canvas.width,canvas.height);
    ctx.fillStyle = '#00ffff';
    drops.forEach((y, i) => {
        ctx.fillText(String.fromCharCode(33 + Math.random() * 94), i * 18, y * 18);
        if(y * 18 > canvas.height && Math.random() > 0.975) drops[i] = 0;
        drops[i]++;
    });
  }
  setInterval(draw, 55);

  // SSE Bağlantısı
  var logbox = document.getElementById('logbox');
  var cursorLine = document.getElementById('cursorLine');
  function connect() {
    var es = new EventSource('/log-stream');
    es.onmessage = function(e) {
      var p = e.data.split('|');
      var le = document.createElement('div');
      le.className = 'le';
      le.innerHTML = '<span class="ts">'+p[0]+'</span><span class="msg '+p[1]+'">'+p[2]+'</span>';
      logbox.insertBefore(le, cursorLine);
      logbox.scrollTop = logbox.scrollHeight;
    };
    es.onerror = function() { es.close(); setTimeout(connect, 3000); };
  }
  connect();
</script>
</body>
</html>
"""

BOOT_TIME = time.strftime('%H:%M:%S')

def pinger():
    time.sleep(10)
    while True:
        if TARGET_LINK:
            try:
                resp = requests.get(TARGET_LINK, timeout=15)
                ping_status.update({"last_time": time.strftime('%H:%M:%S'), "last_code": resp.status_code, "last_ok": True})
                ping_status["success"] += 1
            except:
                ping_status.update({"last_time": time.strftime('%H:%M:%S'), "last_code": "HATA", "last_ok": False})
            ping_status["total"] += 1
        time.sleep(300)

threading.Thread(target=pinger, daemon=True).start()

@app.route('/')
def index():
    return render_template_string(HTML_PAGE, **ping_status, boot_time=BOOT_TIME)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, threaded=True)import os
import time
import threading
import random
import requests
from flask import Flask, render_template_string, Response, stream_with_context

app = Flask(__name__)

TARGET_LINK = os.environ.get("TARGET_LINK", "")

ping_status = {
    "last_time": "---",
    "last_code": "---",
    "last_ok": None,
    "total": 0,
    "success": 0,
}

FAKE_LOGS = [
    ("sys", ">> MEM CHECK :: heap 42MB / 512MB OK"),
    ("sys", ">> THREAD POOL :: workers: 4 active"),
    ("sys", ">> NET IFACE :: eth0 UP [100Mbps]"),
    ("sys", ">> DNS RESOLVE :: target cached [TTL 60s]"),
    ("sys", ">> SOCKET :: keepalive enabled"),
    ("sys", ">> SSL HANDSHAKE :: TLS 1.3 OK"),
    ("sys", ">> SCHEDULER :: next ping queued"),
    ("sys", ">> GC CYCLE :: freed 1.2MB"),
    ("sys", ">> ENV LOAD :: TARGET_LINK set"),
    ("sys", ">> WATCHDOG :: process healthy"),
    ("sys", ">> LOG ROTATE :: 0 files purged"),
    ("sys", ">> UPTIME :: system stable"),
    ("sys", ">> CPU :: 1.4% user 0.2% sys"),
    ("sys", ">> DISK IO :: 0 queued ops"),
    ("sys", ">> ROUTE TABLE :: default gw OK"),
    ("sys", ">> HEAP ALLOC :: 0 leaks detected"),
    ("sys", ">> PORT 5000 :: listening OK"),
    ("sys", ">> IPV4 :: 0.0.0.0 bound"),
    ("sys", ">> THREAD :: pinger alive"),
    ("sys", ">> SWAP :: 0MB used"),
    ("sys", ">> MUTEX :: unlocked"),
    ("sys", ">> CACHE :: hit ratio 98.2%"),
    ("sys", ">> SIGNAL :: SIGTERM not received"),
    ("sys", ">> CONFIG RELOAD :: no changes"),
    ("sys", ">> RATE LIMIT :: 0/100 used"),
    ("sys", ">> SESSION :: id:a3f9c2 active"),
    ("sys", ">> BUFFER FLUSH :: 0 bytes pending"),
    ("sys", ">> RETRY QUEUE :: empty"),
    ("sys", ">> PROXY :: direct route OK"),
    ("sys", ">> TIMESTAMP SYNC :: NTP OK"),
    ("ok",  ">> PING OK :: [TARGET CLASSIFIED] [HTTP 200]"),
    ("ok",  ">> RESPONSE TIME :: 312ms"),
    ("ok",  ">> RESPONSE TIME :: 289ms"),
    ("ok",  ">> RESPONSE TIME :: 401ms"),
    ("ok",  ">> CONN REUSE :: keep-alive hit"),
    ("ok",  ">> PAYLOAD :: 1.8KB received"),
    ("ok",  ">> HEADER CHECK :: content-type OK"),
    ("ok",  ">> STATUS VERIFIED :: service UP"),
    ("ok",  ">> HTTP 200 :: target reachable"),
    ("ok",  ">> LATENCY :: within threshold"),
]

@app.route('/log-stream')
def log_stream():
    def generate():
        while True:
            # Gecikme aralığı daha akıcı hale getirildi (Donma hissini engeller)
            delay = random.uniform(0.4, 1.2)
            time.sleep(delay)
            
            # Aynı anda en fazla 2 adet log gönderilir
            num_logs = random.randint(1, 2)
            chosen_logs = random.choices(FAKE_LOGS, k=num_logs)
            
            for cls, msg in chosen_logs:
                ts = time.strftime('%H:%M:%S')
                line = f"{ts}|{cls}|{msg}"
                yield f"data: {line}\n\n"
                
    return Response(stream_with_context(generate()),
                    mimetype='text/event-stream',
                    headers={'Cache-Control': 'no-cache', 'X-Accel-Buffering': 'no'})

HTML_PAGE = """<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<meta http-equiv="refresh" content="300">
<title>PINGBOT // SYSTEM STATUS</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&display=swap');
  :root {
    --c: #00ffff; --cd: #00aaaa; --cg: rgba(0,255,255,0.12);
    --g: #00ff88; --r: #ff2244; --bg: #000; --panel: #030f0f;
    --border: rgba(0,255,255,0.2); --muted: #006666;
    --f: 'Share Tech Mono', monospace;
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    background: var(--bg); color: var(--c); font-family: var(--f);
    min-height: 100vh; display: flex; flex-direction: column; overflow: hidden;
  }
  body::after {
    content: ''; position: fixed; inset: 0;
    background: repeating-linear-gradient(0deg, transparent, transparent 3px, rgba(0,255,255,0.012) 3px, rgba(0,255,255,0.012) 4px);
    pointer-events: none; z-index: 1000;
  }
  @keyframes flicker { 0%,100%{opacity:1} 91%{opacity:1} 92%{opacity:.88} 93%{opacity:1} 97%{opacity:1} 98%{opacity:.94} }
  body { animation: flicker 10s infinite; }
  .topbar {
    display: flex; align-items: center; justify-content: space-between;
    padding: .55rem 1.6rem; border-bottom: 1px solid var(--c);
    background: var(--panel); box-shadow: 0 0 24px var(--cg);
  }
  .topbar-left { display: flex; align-items: center; gap: 1rem; }
  .tb-title { font-size: .8rem; letter-spacing: .22em; text-shadow: 0 0 8px var(--c); }
  .tb-ver   { font-size: .62rem; color: var(--muted); letter-spacing: .12em; }
  .topbar-right { display: flex; align-items: center; gap: 1.5rem; }
  .tb-clock { font-size: .9rem; text-shadow: 0 0 10px var(--c); letter-spacing: .1em; }
  .tb-date  { font-size: .65rem; color: var(--cd); letter-spacing: .1em; }
  main { flex: 1; display: grid; grid-template-columns: 1fr 360px; overflow: hidden; }
  .log-panel { border-right: 1px solid var(--border); display: flex; flex-direction: column; overflow: hidden; }
  .ph {
    font-size: .7rem; letter-spacing: .18em; padding: .55rem 1.4rem;
    border-bottom: 1px solid var(--border); background: var(--panel);
    text-shadow: 0 0 6px var(--c); display: flex; align-items: center; justify-content: space-between;
  }
  .ph-right { font-size: .62rem; color: var(--muted); }
  .log-body { flex: 1; overflow-y: auto; padding: 1.2rem 1.4rem; font-size: .78rem; line-height: 2; }
  .log-body::-webkit-scrollbar { width: 3px; }
  .log-body::-webkit-scrollbar-thumb { background: var(--muted); }
  .le { display: flex; gap: .8rem; }
  .le .ts  { color: var(--muted); flex-shrink: 0; font-size: .72rem; }
  .le .msg { color: var(--cd); }
  .le .msg.ok  { color: var(--g); text-shadow: 0 0 7px var(--g); }
  .le .msg.err { color: var(--r); text-shadow: 0 0 7px var(--r); }
  .le .msg.sys { color: var(--muted); }
  @keyframes blink { 50% { opacity:0 } }
  .cursor::after { content:'█'; animation: blink .9s step-end infinite; font-size:.6rem; }
  .right { display: flex; flex-direction: column; overflow-y: auto; }
  .sec { border-bottom: 1px solid var(--border); padding: 1rem 1.2rem; }
  .sec-lbl { font-size: .62rem; letter-spacing: .2em; color: var(--c); text-shadow: 0 0 6px var(--c); margin-bottom: .8rem; }
  .badge { display: flex; align-items: center; gap: .7rem; font-size: .95rem; letter-spacing: .1em; }
  .dot { width: 11px; height: 11px; border-radius: 50%; flex-shrink: 0; }
  .dot.ok   { background: var(--g); animation: glow-g 1.4s ease-in-out infinite; }
  .dot.err  { background: var(--r); box-shadow: 0 0 10px var(--r); }
  .dot.idle { background: var(--muted); }
  @keyframes glow-g { 0%,100%{box-shadow:0 0 5px var(--g)} 50%{box-shadow:0 0 18px var(--g)} }
  .badge.ok   { color: var(--g); text-shadow: 0 0 9px var(--g); }
  .badge.err  { color: var(--r); text-shadow: 0 0 9px var(--r); }
  .badge.idle { color: var(--muted); }
  .sub { font-size: .62rem; color: var(--muted); margin-top: .35rem; letter-spacing: .08em; }
  .dr { display: flex; flex-direction: column; gap: .12rem; margin-bottom: .75rem; }
  .dr:last-child { margin-bottom: 0; }
  .dk { font-size: .58rem; letter-spacing: .15em; color: var(--muted); }
  .dv { font-size: .78rem; color: var(--cd); }
  .dv.ok  { color: var(--g); }
  .dv.err { color: var(--r); }
  .sg { display: grid; grid-template-columns: 1fr 1fr; gap: .6rem; }
  .sb { border: 1px solid var(--border); padding: .8rem .6rem; text-align: center; position: relative; overflow: hidden; }
  .sb::before { content: ''; position: absolute; inset: 0; background: linear-gradient(135deg, rgba(0,255,255,0.03) 0%, transparent 60%); }
  .sn { font-size: 1.8rem; line-height: 1; }
  .sn.t { color: var(--c);  text-shadow: 0 0 12px var(--c); }
  .sn.s { color: var(--g);  text-shadow: 0 0 12px var(--g); }
  .sl { font-size: .58rem; letter-spacing: .12em; color: var(--muted); margin-top: .35rem; }
  .uptime-bar-wrap { margin-top: .5rem; }
  .uptime-lbl { font-size: .6rem; color: var(--muted); letter-spacing: .1em; margin-bottom: .3rem; display: flex; justify-content: space-between; }
  .uptime-track { height: 4px; background: var(--border); }
  .uptime-fill  { height: 100%; background: var(--g); box-shadow: 0 0 8px var(--g); transition: width .4s; }
  @keyframes lobBlink { 0%,100%{opacity:1;box-shadow:0 0 10px var(--r)} 50%{opacity:.3;box-shadow:0 0 3px var(--r)} }
  .lob-timer-val { font-size: 2rem; letter-spacing: .08em; color: var(--g); text-shadow: 0 0 16px var(--g); line-height: 1; margin-bottom: .45rem; }
  .lob-viz { height: 32px; display: flex; align-items: center; gap: 2px; overflow: hidden; margin-bottom: .6rem; }
  .lob-btn { width: 100%; margin-top: .6rem; background: transparent; border: 1px solid var(--r); color: var(--r); text-shadow: 0 0 6px var(--r); font-family: var(--f); font-size: .62rem; letter-spacing: .16em; padding: .42rem; cursor: pointer; transition: background .15s; }
  .lob-btn:hover { background: rgba(255,34,68,0.12); }
  .lob-btn.resumed { border-color: var(--g); color: var(--g); text-shadow: 0 0 6px var(--g); }
  .lob-btn.resumed:hover { background: rgba(0,255,136,0.1); }
  .lob-header-row { display: flex; align-items: center; justify-content: space-between; margin-bottom: .5rem; }
  .lob-rec-dot { width: 9px; height: 9px; border-radius: 50%; background: var(--r); box-shadow: 0 0 8px var(--r); animation: lobBlink 1.1s ease-in-out infinite; }
  .cd-bar-track { width: 80px; height: 2px; background: var(--border); display:inline-block; vertical-align:middle; margin: 0 .4rem; }
  .cd-bar-fill  { height: 100%; background: var(--c); box-shadow: 0 0 4px var(--c); transition: width 1s linear; }
  #matrix { position: fixed; top: 0; left: 0; width: 100%; height: 100%; opacity: .045; pointer-events: none; z-index: 0; }
  .bottombar {
    border-top: 1px solid var(--c); padding: .38rem 1.6rem; background: var(--panel);
    display: flex; justify-content: space-between; align-items: center;
    font-size: .62rem; color: var(--muted); letter-spacing: .1em;
    box-shadow: 0 0 20px var(--cg); position: relative; z-index: 2;
  }
  .bb-right { display: flex; gap: 1.5rem; align-items: center; }
  .bb-dot { display: inline-block; width: 6px; height: 6px; border-radius: 50%; background: var(--g); box-shadow: 0 0 6px var(--g); margin-right: .4rem; animation: glow-g 1.4s ease-in-out infinite; }
</style>
</head>
<body>
<canvas id="matrix"></canvas>

<div class="topbar">
  <div class="topbar-left">
    <span class="tb-title">PINGBOT</span>
    <span class="tb-ver">// RENDER UPTIME SYSTEM v2.0</span>
  </div>
  <div class="topbar-right">
    <span class="tb-date" id="dateEl">----/--/--</span>
    <span class="tb-clock" id="clockEl">--:--:--</span>
  </div>
</div>

<main>
  <div class="log-panel">
    <div class="ph">
      <span>SYSTEM BROADCAST LOGS | PING.LOG</span>
      <span class="ph-right">INTERVAL: 60s</span>
    </div>
    <div style="padding:.6rem 1.4rem;border-bottom:1px solid var(--border);display:flex;align-items:center;gap:.8rem;background:rgba(0,255,255,0.02);">
      <img src="https://i.imgur.com/4VfmCSF.png" alt="lobotomi"
        style="height:54px;width:auto;opacity:.85;border:1px solid var(--border);" />
      <div style="font-size:.6rem;letter-spacing:.12em;color:var(--muted);line-height:1.8;">
        <div style="color:var(--cd);">LOBOTOMY SYSTEMS</div>
        <div>UPTIME MONITOR ACTIVE</div>
        <div>NODE :: render-prod-01</div>
      </div>
    </div>
    <div class="log-body" id="logbox">
      <div class="le"><span class="ts">{{ boot_time }}</span><span class="msg sys">&gt;&gt; SYSTEM BOOT :: pingbot.py loaded</span></div>
      <div class="le"><span class="ts">{{ boot_time }}</span><span class="msg sys">&gt;&gt; TARGET LINK :: [CLASSIFIED] ██████████████</span></div>
      <div class="le"><span class="ts">{{ boot_time }}</span><span class="msg sys">&gt;&gt; PINGER THREAD :: started, delay 10s</span></div>
      {% if last_ok == true %}
      <div class="le"><span class="ts">{{ last_time }}</span><span class="msg ok">&gt;&gt; PING OK :: [TARGET CLASSIFIED] [HTTP {{ last_code }}]</span></div>
      {% elif last_ok == false %}
      <div class="le"><span class="ts">{{ last_time }}</span><span class="msg err">&gt;&gt; PING FAILED :: [TARGET CLASSIFIED] [{{ last_code }}]</span></div>
      {% else %}
      <div class="le"><span class="ts">--:--:--</span><span class="msg sys">&gt;&gt; WAITING :: first ping in 10s...</span></div>
      {% endif %}
      <div class="le" id="cursorLine"><span class="ts"></span><span class="msg cursor"></span></div>
    </div>
  </div>

  <div class="right">
    <div class="sec">
      <div class="sec-lbl">BOT CONTROL</div>
      {% if last_ok == true %}
        <div class="badge ok"><div class="dot ok"></div>ONLINE</div>
      {% elif last_ok == false %}
        <div class="badge err"><div class="dot err"></div>ERROR</div>
      {% else %}
        <div class="badge idle"><div class="dot idle"></div>STANDBY</div>
      {% endif %}
      <div class="sub">pingbot.py // render.com</div>
    </div>

    <div class="sec">
      <div class="sec-lbl">PING STATUS</div>
      <div class="dr">
        <span class="dk">TARGET_URL</span>
        <span class="dv" style="color:var(--muted);font-style:italic;">[CLASSIFIED] ██████████</span>
      </div>
    </div>

    <div class="sec">
      <div class="sec-lbl">STATISTICS</div>
      <div class="sg">
        <div class="sb"><div class="sn t">{{ total }}</div><div class="sl">TOTAL PINGS</div></div>
        <div class="sb"><div class="sn s">{{ success }}</div><div class="sl">SUCCESS</div></div>
      </div>
      {% if total > 0 %}
      <div class="uptime-bar-wrap">
        <div class="uptime-lbl"><span>UPTIME RATE</span><span>{{ "%d"|format((success/total*100)|int) }}%</span></div>
        <div class="uptime-track"><div class="uptime-fill" style="width:{{ (success/total*100)|int }}%"></div></div>
      </div>
      {% endif %}
    </div>

    <div class="sec">
      <div class="sec-lbl">LOBOTOMY // REC</div>
      <div class="lob-header-row">
        <span style="font-size:.58rem;letter-spacing:.14em;color:var(--muted);">SESSION DURATION</span>
        <div class="lob-rec-dot" id="lobDot"></div>
      </div>
      <div class="lob-timer-val" id="lobTimer">00:00:00</div>
      <div class="lob-viz" id="lobViz"></div>
      <div style="border-top:1px solid var(--border);padding-top:.5rem;">
        <div class="dr">
          <span class="dk">STATUS</span>
          <span class="dv ok" id="lobStatus">&#9679; RECORDING</span>
        </div>
        <div class="dr">
          <span class="dk">STARTED</span>
          <span class="dv" id="lobStart">--:--:--</span>
        </div>
      </div>
      <button class="lob-btn" id="lobBtn" onclick="lobToggle()">&#9632; STOP RECORDING</button>
    </div>
  </div>
</main>

<div style="position:fixed;bottom:2.4rem;left:1.6rem;z-index:999;pointer-events:none;font-family:var(--f);line-height:1.7;">
  <div style="font-size:.58rem;letter-spacing:.18em;color:rgba(0,255,255,0.18);">YAPIMCI</div>
  <div style="font-size:.72rem;letter-spacing:.12em;color:rgba(0,255,255,0.28);text-shadow:0 0 8px rgba(0,255,255,0.15);">@lobotomi_fan</div>
  <div style="font-size:.52rem;letter-spacing:.14em;color:rgba(0,255,255,0.12);margin-top:.15rem;">LOBOTOMY SYSTEMS // 2025</div>
</div>

<div class="bottombar">
  <span><span class="bb-dot"></span>SYSTEM ACTIVE // PING INTERVAL: 60s</span>
  <div class="bb-right">
    <span style="color:var(--cd);">REFRESH <span id="cdNum" style="color:var(--c);text-shadow:0 0 6px var(--c);">300</span>s <span class="cd-bar-track"><span class="cd-bar-fill" id="cdBar" style="width:100%;display:block;"></span></span></span>
    <span id="bbDate">----/--/--</span>
    <span id="bbTime">--:--:--</span>
  </div>
</div>

<script>
(function() {
  // Matrix rain
  var canvas = document.getElementById('matrix');
  var ctx = canvas.getContext('2d');
  canvas.width = window.innerWidth; canvas.height = window.innerHeight;
  var cols = Math.floor(canvas.width / 18);
  var drops = Array(cols).fill(1);
  var chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#$%&<>[]{}';
  function drawMatrix() {
    ctx.fillStyle = 'rgba(0,0,0,0.05)'; ctx.fillRect(0,0,canvas.width,canvas.height);
    ctx.fillStyle = '#00ffff'; ctx.font = '13px Share Tech Mono';
    drops.forEach(function(y,i){
      ctx.fillText(chars[Math.floor(Math.random()*chars.length)], i*18, y*18);
      if(y*18>canvas.height && Math.random()>0.975) drops[i]=0;
      drops[i]++;
    });
  }
  setInterval(drawMatrix, 55);

  // Clock
  function pad(n){ return n<10?'0'+n:''+n; }
  function tick(){
    var now=new Date();
    var hms=pad(now.getHours())+':'+pad(now.getMinutes())+':'+pad(now.getSeconds());
    var date=now.getFullYear()+'/'+pad(now.getMonth()+1)+'/'+pad(now.getDate());
    document.getElementById('clockEl').textContent=hms;
    document.getElementById('dateEl').textContent=date;
    document.getElementById('bbTime').textContent=hms;
    document.getElementById('bbDate').textContent=date;
  }
  tick(); setInterval(tick,1000);

  // SSE log stream (Geliştirilmiş bağlantı ve akış kontrolü)
  var logbox = document.getElementById('logbox');
  var cursorLine = document.getElementById('cursorLine');
  var MAX_LINES = 15;
  var es;

  function connectLogStream() {
    es = new EventSource('/log-stream');
    
    es.onmessage = function(e) {
      var parts = e.data.split('|');
      var ts  = parts[0];
      var cls = parts[1];
      var msg = parts[2];
      
      var lines = logbox.querySelectorAll('.le');
      
      if(lines.length >= MAX_LINES) {
        var toRemove = [];
        lines.forEach(function(l){ if(l.id !== 'cursorLine') toRemove.push(l); });
        toRemove.forEach(function(l){ l.remove(); });
        
        var sep = document.createElement('div');
        sep.className = 'le';
        sep.innerHTML = '<span class="ts">'+ts+'</span><span class="msg sys">>> SCREEN RESET :: log buffer wiped & restarted</span>';
        logbox.insertBefore(sep, cursorLine);
      }
      
      var le = document.createElement('div');
      le.className = 'le';
      le.innerHTML = '<span class="ts">'+ts+'</span><span class="msg '+cls+'">'+msg+'</span>';
      logbox.insertBefore(le, cursorLine);
      logbox.scrollTop = logbox.scrollHeight;
    };

    // Durma/Donma hatası için otomatik yeniden bağlanma tetikleyicisi
    es.onerror = function() {
      es.close();
      setTimeout(connectLogStream, 2000); // Bağlantı koparsa 2 sn sonra otomatik canlandırır
    };
  }

  connectLogStream();

  // Countdown
  var total=300, left=total;
  var cdNum=document.getElementById('cdNum');
  var cdBar=document.getElementById('cdBar');
  setInterval(function(){
    left--;
    cdNum.textContent=left;
    cdBar.style.width=(left/total*100)+'%';
    if(left<=0) location.reload();
  },1000);

  // Lobotomy rec
  var lobStartTime=Date.now(), lobRunning=true;
  var lobNow=new Date();
  document.getElementById('lobStart').textContent=pad(lobNow.getHours())+':'+pad(lobNow.getMinutes())+':'+pad(lobNow.getSeconds());

  var lobViz=document.getElementById('lobViz');
  var lobBars=[];
  var lobStyle=document.createElement('style');
  lobStyle.textContent='@keyframes lobWave{0%,100%{transform:scaleY(.1)}50%{transform:scaleY(1)}}';
  document.head.appendChild(lobStyle);
  for(var i=0;i<40;i++){
    var b=document.createElement('div');
    var dur=(0.4+Math.random()*0.8).toFixed(2)+'s';
    var dly=(-Math.random()*1.2).toFixed(2)+'s';
    b.style.cssText='width:3px;height:32px;border-radius:1px;background:var(--c);box-shadow:0 0 4px var(--c);transform-origin:bottom;transform:scaleY(0.1);animation:lobWave '+dur+' linear '+dly+' infinite;';
    lobViz.appendChild(b); lobBars.push(b);
  }

  var lobTimerEl=document.getElementById('lobTimer');
  setInterval(function(){
    if(!lobRunning) return;
    var e=Math.floor((Date.now()-lobStartTime)/1000);
    lobTimerEl.textContent=pad(Math.floor(e/3600))+':'+pad(Math.floor(e%3600/60))+':'+pad(e%60);
  },1000);

  window.lobToggle=function(){
    lobRunning=!lobRunning;
    var btn=document.getElementById('lobBtn');
    var dot=document.getElementById('lobDot');
    var st=document.getElementById('lobStatus');
    if(!lobRunning){
      btn.textContent='\\u25b6 RESUME RECORDING'; btn.classList.add('resumed');
      st.textContent='\\u25a0 PAUSED'; st.className='dv';
      dot.style.animation='none'; dot.style.background='var(--muted)'; dot.style.boxShadow='none';
      lobBars.forEach(function(b){ b.style.animation='none'; b.style.transform='scaleY(0.08)'; });
    } else {
      var p=lobTimerEl.textContent.split(':');
      lobStartTime=Date.now()-(+p[0]*3600 + +p[1]*60 + +p[2])*1000;
      btn.textContent='\\u25a0 STOP RECORDING'; btn.classList.remove('resumed');
      st.textContent='\\u25cf RECORDING'; st.className='dv ok';
      dot.style.animation='lobBlink 1.1s ease-in-out infinite';
      dot.style.background='var(--r)'; dot.style.boxShadow='0 0 8px var(--r)';
      lobBars.forEach(function(b){
        var dur=(0.4+Math.random()*0.8).toFixed(2)+'s';
        var dly=(-Math.random()*1.2).toFixed(2)+'s';
        b.style.animation='lobWave '+dur+' linear '+dly+' infinite';
      });
    }
  };
})();
</script>
</body>
</html>
"""

BOOT_TIME = time.strftime('%H:%M:%S')

def pinger():
    time.sleep(10)
    while True:
        if TARGET_LINK:
            try:
                resp = requests.get(TARGET_LINK, timeout=15)
                ping_status["last_time"] = time.strftime('%H:%M:%S')
                ping_status["last_code"] = resp.status_code
                ping_status["last_ok"]   = True
                ping_status["success"]  += 1
                print(f"[{ping_status['last_time']}] OK ({resp.status_code})")
            except Exception as e:
                ping_status["last_time"] = time.strftime('%H:%M:%S')
                ping_status["last_code"] = "HATA"
                ping_status["last_ok"]   = False
                print(f"[{ping_status['last_time']}] FAIL: {e}")
            ping_status["total"] += 1
        time.sleep(300)

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
        boot_time=BOOT_TIME,
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, threaded=True)
