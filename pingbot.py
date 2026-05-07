import os
import time
import threading
import requests
from flask import Flask, render_template_string

app = Flask(__name__)

# Render panelindeki 'Environment' kısmından linki çekiyoruz
# Eğer değer girilmemişse 'Link Bulunamadı' mesajı döner
TARGET_LINK = os.environ.get("TARGET_LINK", "Link Ayarlanmamış")

# Basit ve şık bir arayüz
HTML_PAGE = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <title>Lobo Keeper v2</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #0f172a; color: #f8fafc; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .container { text-align: center; border: 2px solid #334155; padding: 40px; border-radius: 15px; background: #1e293b; box-shadow: 0 10px 25px rgba(0,0,0,0.5); }
        .status-on { color: #22c55e; font-weight: bold; font-size: 1.2em; }
        .url-box { background: #0f172a; padding: 10px; border-radius: 8px; color: #38bdf8; margin-top: 15px; word-break: break-all; }
        h1 { margin-bottom: 10px; color: #f1f5f9; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Lobo Keeper Aktif</h1>
        <p class="status-on">● Sistem Çalışıyor</p>
        <p>Dakika başı uyarı gönderilen hedef:</p>
        <div class="url-box">{{ url }}</div>
    </div>
</body>
</html>
"""

def pinger():
    """Arka planda her dakika hedef linke ping atar."""
    # Botun ilk açılışta kendine gelmesi için 10 saniye bekle
    time.sleep(10)
    
    while True:
        if TARGET_LINK != "Link Ayarlanmamış":
            try:
                # Timeout ekledik ki bot bir yere takılıp kalmasın
                response = requests.get(TARGET_LINK, timeout=15)
                print(f"[{time.strftime('%H:%M:%S')}] Ping Başarılı: {TARGET_LINK} (Kod: {response.status_code})")
            except Exception as e:
                print(f"Hata: Ping gönderilemedi -> {e}")
        else:
            print("Uyarı: TARGET_LINK değişkeni Render panelinde ayarlanmamış!")
        
        # 60 saniye (1 dakika) bekle
        time.sleep(60)

@app.route('/')
def index():
    return render_template_string(HTML_PAGE, url=TARGET_LINK)

if __name__ == "__main__":
    # Ping döngüsünü ayrı bir iş parçacığında başlat
    threading.Thread(target=pinger, daemon=True).start()
    
    # Port Render tarafından otomatik atanır
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
