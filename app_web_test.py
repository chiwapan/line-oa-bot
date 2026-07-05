#!/usr/bin/env python3
"""
The Oasis LINE OA Bot — Web Test Interface (DEMO Mode)
Built from 9,809 chat conversations analysis.
"""
import json
import os
import re
from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

# Load FAQ config
try:
    with open(os.path.join(os.path.dirname(__file__), 'faq_config.json')) as f:
        CONFIG = json.load(f)
except Exception as e:
    print(f"⚠️ Failed to load config: {e}")
    CONFIG = {"intents": {}, "fallback_response": "ไม่มีข้อมูลครับ", "contact": {}}

DEMO_MODE = not os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")
HISTORY = []


def classify_intent(text):
    """Match user text against configured intents by keyword."""
    text = text.lower()
    best_intent = None
    best_count = 0
    for intent, data in CONFIG.get("intents", {}).items():
        count = sum(1 for kw in data.get("keywords", []) if kw.lower() in text)
        if count > best_count:
            best_count = count
            best_intent = intent
    return best_intent if best_intent else "unknown"


def get_response(intent):
    """Return the configured response for an intent."""
    rules = CONFIG.get("intents", {})
    if intent in rules:
        return rules[intent].get("response", CONFIG.get("fallback_response", "ไม่มีข้อมูล"))
    return CONFIG.get("fallback_response", "ไม่เข้าใจครับ พิมพ์ใหม่หรือกดเมนูด้านล่าง")


HTML_PAGE = """<!DOCTYPE html>
<html lang="th"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>The Oasis Bot Test</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:#f0f2f5;padding:16px}
.box{max-width:500px;margin:0 auto;background:#fff;border-radius:12px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,.1)}
.hd{background:#06c755;color:#fff;padding:16px;text-align:center;font-size:18px}
.msgs{height:55vh;overflow-y:auto;padding:12px;display:flex;flex-direction:column;gap:8px}
.m{max-width:80%;padding:10px 14px;border-radius:12px;font-size:15px;line-height:1.5;white-space:pre-wrap}
.u{background:#06c755;color:#fff;align-self:flex-end}
.b{background:#e9ecef;align-self:flex-start}
.bar{display:flex;border-top:1px solid #ddd}
.bar input{flex:1;border:none;padding:14px;font-size:16px;outline:none}
.bar button{background:#06c755;color:#fff;border:none;padding:0 20px;font-size:18px;cursor:pointer}
.chips{display:flex;flex-wrap:wrap;gap:6px;padding:8px 12px}
.chips button{background:#e8f5e9;border:1px solid #06c755;color:#06c755;border-radius:20px;padding:6px 12px;font-size:13px;cursor:pointer}
.stats{background:#f8f9fa;padding:8px 12px;font-size:12px;color:#666;border-top:1px solid #eee;text-align:center}
</style></head><body>
<div class="box">
<div class="hd">🤖 The Oasis Bot Test (DEMO)</div>
<div class="chips">
<button onclick="t('ราคาเท่าไร')">💰 ราคา</button>
<button onclick="t('รักษาอะไรบ้าง')">🏥 บริการ</button>
<button onclick="t('ปวดหัว')">😰 อาการ</button>
<button onclick="t('นัดหมาย')">📅 นัดคิว</button>
<button onclick="t('อยู่ไหน')">📍 สถานที่</button>
<button onclick="t('หมอชื่ออะไร')">👨‍⚕️ ทีมแพทย์</button>
<button onclick="t('ยกเลิกนัด')">❌ ยกเลิก</button>
</div>
<div class="msgs" id="M"></div>
<div class="bar"><input id="I" placeholder="พิมพ์ข้อความ..." onkeydown="if(event.key==='Enter')s()"><button onclick="s()">ส่ง</button></div>
<div class="stats" id="S">0 matched intents</div>
</div>
<script>
let matched=0;
function t(m){document.getElementById('I').value=m;s()}
function s(){
let i=document.getElementById('I'),v=i.value.trim();
if(!v)return;
let M=document.getElementById('M');
M.innerHTML+='<div class="m u">'+v+'</div>';
i.value='';
M.scrollTop=M.scrollHeight;
fetch('/api/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:v})})
.then(r=>r.json()).then(d=>{
M.innerHTML+='<div class="m b">'+d.response+'</div>';
if(d.intent!=='unknown'){matched++;document.getElementById('S').textContent=matched+' matched intents';}
M.scrollTop=M.scrollHeight;
});
}
</script></body></html>
"""


@app.route("/")
def index():
    return HTML_PAGE


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json()
    msg = data.get("message", "")
    intent = classify_intent(msg)
    resp = get_response(intent)
    entry = {
        "user": msg,
        "intent": intent,
        "response": resp,
        "time": datetime.now().strftime("%H:%M:%S")
    }
    HISTORY.append(entry)
    return jsonify(entry)


@app.route("/api/history")
def history():
    return jsonify(HISTORY[-50:])


@app.route("/api/clear", methods=["POST"])
def clear():
    HISTORY.clear()
    return jsonify({"status": "ok"})


@app.route("/api/test", methods=["GET"])
def test():
    return jsonify({"status": "ok", "mode": "demo", "intents": list(CONFIG.get("intents", {}).keys())})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
