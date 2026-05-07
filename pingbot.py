import os
import time
import threading
import requests
from flask import Flask, render_template_string

app = Flask(__name__)

TARGET_LINK = os.environ.get("TARGET_LINK", "Link Ayarlanmamış")

# HTML Şablonu (Aynı bıraktım)
HTML_PAGE = """...""" # Yukarıdaki tasarımın aynısı

def pinger():
    """Arka planda her dakika hedef linke ping atar."""
    time.sleep(10)
    while True:
        if TARGET_LINK != "Link Ayarlanmamış":
            try:
                response = requests.get(TARGET_LINK, timeout=15)
                print(f"[{time.strftime('%H:%M:%S')}] Ping Başarılı: {TARGET_LINK} (Kod: {response.status_code})")
            except Exception as e:
                print(f"Hata: Ping gönderilemedi -> {e}")
        time.sleep(60)

# DİKKAT: Thread'i burada başlatıyoruz ki Gunicorn çalıştırdığında da devreye girsin
threading.Thread(target=pinger, daemon=True).start()

@app.route('/')
def index():
    return render_template_string(HTML_PAGE, url=TARGET_LINK)

if __name__ == "__main__":
    # Bu kısım sadece yerelde (kendi bilgisayarında) test ederken çalışır
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
