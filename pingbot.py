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

# UltraKill — 3 sade satir, sirasiya gonder
ULTRAKILL_LINES = [
    ("err", ">> MANKIND IS DEAD."),
    ("err", ">> BLOOD IS FUEL."),
    ("err", ">> HELL IS FULL."),
]


@app.route('/log-stream')
def log_stream():
    def generate():
        last_heartbeat = time.time()
        while True:
            now = time.time()

            # Heartbeat — donmayi onler
            if now - last_heartbeat >= 15:
                yield ": heartbeat\n\n"
                last_heartbeat = time.time()
                time.sleep(0.1)
                continue

            # UltraKill easter egg — %1 ihtimalle
            if random.random() < 0.01:
                for cls, msg in ULTRAKILL_LINES:
                    ts = time.strftime('%H:%M:%S')
                    yield f"data: {ts}|{cls}|{msg}\n\n"
                    time.sleep(0.6)
                last_heartbeat = time.time()
                continue

            # Normal log
            delay = random.uniform(1.8, 4.5)
            time.sleep(delay)

            num_logs = 1 if random.random() < 0.75 else 2
            chosen_logs = random.choices(FAKE_LOGS, k=num_logs)

            for cls, msg in chosen_logs:
                ts = time.strftime('%H:%M:%S')
                yield f"data: {ts}|{cls}|{msg}\n\n"

            last_heartbeat = time.time()

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
<meta http-equiv="refresh" content="43200">
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
    height: 100vh; display: flex; flex-direction: column; overflow: hidden;
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
    flex-shrink: 0;
  }
  .topbar-left { display: flex; align-items: center; gap: 1rem; }
  .tb-title { font-size: .8rem; letter-spacing: .22em; text-shadow: 0 0 8px var(--c); }
  .tb-ver   { font-size: .62rem; color: var(--muted); letter-spacing: .12em; }
  .topbar-right { display: flex; align-items: center; gap: 1.5rem; }
  .tb-clock { font-size: .9rem; text-shadow: 0 0 10px var(--c); letter-spacing: .1em; }
  .tb-date  { font-size: .65rem; color: var(--cd); letter-spacing: .1em; }
  main { flex: 1; display: grid; grid-template-columns: 1fr 360px; overflow: hidden; min-height: 0; }
  .log-panel { border-right: 1px solid var(--border); display: flex; flex-direction: column; overflow: hidden; min-height: 0; }
  .ph {
    font-size: .7rem; letter-spacing: .18em; padding: .55rem 1.4rem;
    border-bottom: 1px solid var(--border); background: var(--panel);
    text-shadow: 0 0 6px var(--c); display: flex; align-items: center; justify-content: space-between;
    flex-shrink: 0;
  }
  .ph-right { font-size: .62rem; color: var(--muted); }
  .log-body { flex: 1; overflow-y: auto; padding: .6rem 1.4rem; font-size: .78rem; line-height: 2; }
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
    flex-shrink: 0;
  }
  .bb-right { display: flex; gap: 1.5rem; align-items: center; }
  .bb-dot { display: inline-block; width: 6px; height: 6px; border-radius: 50%; background: var(--g); box-shadow: 0 0 6px var(--g); margin-right: .4rem; animation: glow-g 1.4s ease-in-out infinite; }

  /* ── YENİ BÖLÜMLER ── */
  .now-playing-sec {
    border: 1px solid var(--border);
    margin: auto 1rem 0.9rem 1rem;
    padding: 1rem 1.1rem 1.1rem;
    background: rgba(0,255,255,0.02);
  }
  .np-sec-lbl {
    font-size: .78rem; letter-spacing: .22em;
    color: var(--g); text-shadow: 0 0 8px var(--g);
    margin-bottom: .9rem;
    animation: npLblBlink 2.8s ease-in-out infinite;
  }
  @keyframes npLblBlink {
    0%,100% { opacity:1; text-shadow: 0 0 8px var(--g), 0 0 20px rgba(0,255,136,0.4); }
    50%      { opacity:.65; text-shadow: 0 0 4px var(--g); }
  }
  .np-inner {
    display: flex; align-items: flex-start; gap: .85rem;
  }
  .np-img-wrap {
    flex-shrink: 0;
    width: 72px; height: 72px;
    border: 1px solid var(--border);
    overflow: hidden;
  }
  .np-img-wrap img {
    width: 100%; height: 100%; object-fit: cover;
    display: block; opacity: .88;
  }
  .np-text-area {
    flex: 1; min-width: 0;
  }
  .np-content-text {
    font-size: .72rem; color: #ffffff; line-height: 1.75;
    letter-spacing: .04em; white-space: pre-wrap; word-break: break-word;
    text-shadow: 0 0 6px rgba(255,255,255,0.5);
  }
  .np-content-text.loading { color: var(--muted); font-style: italic; text-shadow: none; }
  .np-content-text.error   { color: var(--r); text-shadow: none; }

  .fav-person-sec {
    border-bottom: 1px solid var(--border);
    padding: 1rem 1.2rem;
  }
  .fav-person-row {
    display: flex; align-items: baseline; gap: .5rem; flex-wrap: wrap;
    margin-top: .15rem;
  }
  .fav-person-label {
    font-size: .65rem; color: var(--muted); letter-spacing: .1em; flex-shrink: 0;
  }
  .fav-person-name {
    font-size: .88rem; color: #ff69b4;
    text-shadow: 0 0 10px #ff69b4, 0 0 22px rgba(255,105,180,0.4);
    letter-spacing: .12em;
    animation: namePulse 2.6s ease-in-out infinite;
  }
  @keyframes namePulse {
    0%,100% { text-shadow: 0 0 8px #ff69b4, 0 0 18px rgba(255,105,180,0.35); opacity:1; }
    50%      { text-shadow: 0 0 16px #ff69b4, 0 0 34px rgba(255,105,180,0.65); opacity:.8; }
  }
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

    <!-- ── ŞU SIRALAR LOBOTOMİ ── -->
    <div class="now-playing-sec">
      <div class="np-sec-lbl">SU SIRALAR <span style="color:var(--c);text-shadow:0 0 12px var(--c),0 0 28px rgba(0,255,255,0.6);">LOBOTOMİ</span></div>
      <div class="np-inner">
        <!-- Resim: src'yi istediğin imgur linki ile değiştir -->
        <div class="np-img-wrap">
          <img id="npImg" src="https://i.imgur.com/4VfmCSF.png" alt="şu sıralar" />
        </div>
        <div class="np-text-area">
          <div class="np-content-text loading" id="npText">// FETCHING DATA...</div>
        </div>
      </div>
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
      <div class="sub">pingbot.py // https://discord.gg/PsDjBy7BjF</div>
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

    <!-- ── EN SEVDİĞİM KİŞİ ── -->
    <div class="fav-person-sec sec">
      <div class="sec-lbl">SU SIRALAR EN SEVDİĞİM KİŞİ</div>
      <div class="fav-person-row">
        <span class="fav-person-label">ŞU AN ::</span>
        <span class="fav-person-name" id="favPersonEl"></span>
      </div>
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
    <span style="color:var(--cd);">REFRESH <span id="cdNum" style="color:var(--c);text-shadow:0 0 6px var(--c);">43200</span>s <span class="cd-bar-track"><span class="cd-bar-fill" id="cdBar" style="width:100%;display:block;"></span></span></span>
    <span id="bbDate">----/--/--</span>
    <span id="bbTime">--:--:--</span>
  </div>
</div>

<script>
// ╔══════════════════════════════════════════╗
// ║  KOLAY DEĞİŞTİRİLEBİLİR SABİTLER        ║
// ╚══════════════════════════════════════════╝

// En sevdiğin kişi — buradan değiştir:
const FAV_PERSON = "Cowboy Spike";

// "Şu Sıralar" metninin çekileceği GitHub raw .txt URL'si:
const NOW_PLAYING_TXT_URL = "https://raw.githubusercontent.com/kirrakker/pingbot/refs/heads/main/mesaj.txt";

// "Şu Sıralar" görseli için imgur linki — npImg src'sini de değiştirebilirsin,
// ya da bu sabiti JS tarafından atamak istersen aşağıdaki satırı aç:
// document.getElementById('npImg').src = "https://i.imgur.com/XXXXX.png";

// ════════════════════════════════════════════

(function() {
  // ── EN SEVDİĞİM KİŞİ ──
  document.getElementById('favPersonEl').textContent = FAV_PERSON;

  // ── ŞU SIRALAR LOBOTOMİ :: GitHub'dan metin çek ──
  var npText = document.getElementById('npText');
  fetch(NOW_PLAYING_TXT_URL)
    .then(function(res) {
      if (!res.ok) throw new Error('HTTP ' + res.status);
      return res.text();
    })
    .then(function(txt) {
      npText.classList.remove('loading', 'error');
      npText.textContent = txt.trim();
    })
    .catch(function(err) {
      npText.classList.remove('loading');
      npText.classList.add('error');
      npText.textContent = '>> FETCH ERR :: ' + err.message;
    });

  // ── MATRIX ──
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

  var logbox = document.getElementById('logbox');
  var cursorLine = document.getElementById('cursorLine');
  var MAX_LINES = 13;
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
    es.onerror = function() {
      es.close();
      setTimeout(connectLogStream, 2000);
    };
  }
  connectLogStream();

  var total=43200, left=total;
  var cdNum=document.getElementById('cdNum');
  var cdBar=document.getElementById('cdBar');
  setInterval(function(){
    left--;
    cdNum.textContent=left;
    cdBar.style.width=(left/total*100)+'%';
    if(left<=0) location.reload();
  },1000);

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
    app.run(host='0.0.0.0', port=port, threaded=True)
