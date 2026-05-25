<!-- LOBOTOMY REC bölümünü right paneline ekle -->
<div class="sec" id="lob-sec">
  <div class="sec-lbl">LOBOTOMY // REC</div>

  <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:.7rem;">
    <span style="font-size:.62rem;letter-spacing:.14em;color:var(--muted);">SESSION DURATION</span>
    <div id="lobDot" style="width:9px;height:9px;border-radius:50%;background:var(--r);box-shadow:0 0 8px var(--r);animation:lobBlink 1.1s ease-in-out infinite;"></div>
  </div>

  <div id="lobTimer" style="font-size:2rem;letter-spacing:.08em;color:var(--r);text-shadow:0 0 16px var(--r);line-height:1;margin-bottom:.45rem;">00:00:00</div>

  <div id="lobViz" style="height:32px;display:flex;align-items:center;gap:2px;overflow:hidden;margin-bottom:.6rem;"></div>

  <div style="border-top:1px solid var(--border);padding-top:.5rem;">
    <div class="dr">
      <span class="dk">STATUS</span>
      <span class="dv ok" id="lobStatus">● RECORDING</span>
    </div>
    <div class="dr">
      <span class="dk">STARTED</span>
      <span class="dv" id="lobStart">--:--:--</span>
    </div>
    <div class="dr">
      <span class="dk">FRAMES</span>
      <span class="dv" id="lobFrames">0</span>
    </div>
  </div>

  <button id="lobBtn" onclick="lobToggle()"
    style="width:100%;margin-top:.6rem;background:transparent;border:1px solid var(--r);
    color:var(--r);text-shadow:0 0 6px var(--r);font-family:var(--f);font-size:.62rem;
    letter-spacing:.16em;padding:.4rem;cursor:pointer;">
    ■ STOP RECORDING
  </button>
</div>
