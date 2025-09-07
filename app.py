import os
import time
from slack_bolt import App
from slack_sdk import WebClient
from storage import is_ignored_today, set_ignore_today
from detector import check_ip
from datetime import date
import threading
from dotenv import load_dotenv

load_dotenv() 

# 環境変数
BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
USER_TOKEN = os.environ["SLACK_USER_TOKEN"]

# App: Bot Token 用（DM送信用）
app = App(token=BOT_TOKEN)

# User Client: User Token 用（ステータス変更用）
user_client = WebClient(token=USER_TOKEN)

# ステータス変更関数
def set_status(text, emoji):
    profile = {"status_text": text, "status_emoji": emoji}
    user_client.users_profile_set(profile=profile)

# /shussha off → 今日だけ除外
@app.command("/shussha")
def handle_shussha(ack, say, command):
    ack()
    if "off" in command["text"]:
        set_ignore_today()
        say("✅ 今日の出社検知をOFFにしました")
    else:
        say("ℹ️ `/shussha off` で今日の検知を無効化できます")

# /出社リスト → 出社中ユーザー一覧をDMに表示
@app.command("/出社リスト")
def handle_list(ack, respond):
    ack()
    members = app.client.users_list()["members"]

    office_members = []
    for m in members:
        if not m.get("is_bot") and not m.get("deleted"):
            profile = m.get("profile", {})
            if profile.get("status_text") == "出社中":
                office_members.append(profile.get("real_name", m["name"]))

    if office_members:
        respond("🏢 出社中:\n" + "\n".join(office_members), ephemeral=True)
    else:
        respond("今日は誰も出社していません", ephemeral=True)

# 定期監視ループ
def monitor():
    notified_date = None
    while True:
        today = date.today()
        ip_in_office = check_ip()

        if not is_ignored_today():
            if ip_in_office and notified_date != today:
                # 出社判定 True
                set_status("出社中", ":office:")
                user_id = user_client.auth_test()["user_id"]
                app.client.chat_postMessage(
                    channel=user_id,
                    text=f"🏢 {today} 出社を検知しました！"
                )
                notified_date = today

            elif not ip_in_office and notified_date == today:
                # 出社取り消し
                set_status("", "")
                user_id = user_client.auth_test()["user_id"]
                app.client.chat_postMessage(
                    channel=user_id,
                    text=f"❌ {today} 出社キャンセルしました。"
                )
                notified_date = None

        time.sleep(10)  # 5分ごと

# デーモン化して Bolt App 起動
if __name__ == "__main__":
    from slack_bolt.adapter.socket_mode import SocketModeHandler
    handler = SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
    threading.Thread(target=monitor, daemon=True).start()
    handler.start()