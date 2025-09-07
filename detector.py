import requests

COMPANY_IPS = [
    "103.115.217.53",
    "103.115.217.54"
]

def check_ip():
    try:
        ip = requests.get("https://ifconfig.me", timeout=5).text.strip()
        print("現在のIP:", ip)  # デバッグ
        return ip in COMPANY_IPS
    except requests.exceptions.RequestException as e:
        print("IP取得失敗:", e)
        return False
