#!/usr/bin/env python3
"""
Math Magic - Daily Core Math Practice Generator
Generates 10-question HTML with themed scenes, validation, and deduplication.
"""

import os
import sys
import json
import hashlib
import random
from datetime import datetime, timedelta
from pathlib import Path

# ===== Configuration =====
BASE_DIR = Path(__file__).resolve().parent.parent
HISTORY_FILE = BASE_DIR / "question-history.json"
OUTPUT_DIR = BASE_DIR

# Day of week theme mapping
DAY_THEMES = {
    0: ("超市购物", "🛒", "#4ECDC4"),
    1: ("太空探险", "🚀", "#6366F1"),
    2: ("海底世界", "🌊", "#3B82F6"),
    3: ("动物园", "🦁", "#F59E0B"),
    4: ("魔法城堡", "🏰", "#FF6B6B"),
    5: ("魔法城堡", "🏰", "#FF6B6B"),
    6: ("魔法城堡", "🏰", "#FF6B6B"),
}

# ===== Question History =====
def load_history():
    if HISTORY_FILE.exists():
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"used_questions": {}, "last_date": None}

def save_history(history):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

def get_question_hash(question_text):
    return hashlib.md5(question_text.encode("utf-8")).hexdigest()

def is_question_used(question_text, category=None):
    history = load_history()
    qhash = get_question_hash(question_text)
    if category and category in history["used_questions"]:
        return qhash in history["used_questions"][category]
    for cat_questions in history["used_questions"].values():
        if qhash in cat_questions:
            return True
    return False

def mark_question_used(question_text, category=None):
    history = load_history()
    qhash = get_question_hash(question_text)
    cat_key = category or "math_magic"
    if cat_key not in history["used_questions"]:
        history["used_questions"][cat_key] = {}
    history["used_questions"][cat_key][qhash] = {
        "text": question_text[:50],
        "date": datetime.now().strftime("%Y-%m-%d")
    }
    save_history(history)

def get_week_number(start_date_str, current_date_str):
    start = datetime.strptime(start_date_str, "%Y-%m-%d")
    current = datetime.strptime(current_date_str, "%Y-%m-%d")
    delta = (current - start).days
    return max(1, (delta // 7) + 1)

# ===== Math Magic Question Generators =====
def generate_scene_question(theme_name, theme_emoji, week, q_num):
    """Generate a themed math question."""
    
    # Scene templates by theme
    theme_scenes = {
        "超市购物": [
            {"emoji": "🍎", "name": "苹果", "unit": "元"},
            {"emoji": "🍞", "name": "面包", "unit": "元"},
            {"emoji": "🥛", "name": "牛奶", "unit": "元"},
            {"emoji": "🍪", "name": "饼干", "unit": "元"},
        ],
        "太空探险": [
            {"emoji": "🚀", "name": "火箭", "unit": "个"},
            {"emoji": "⭐", "name": "星星", "unit": "颗"},
            {"emoji": "🌙", "name": "月亮", "unit": "个"},
            {"emoji": "🪐", "name": "行星", "unit": "颗"},
        ],
        "海底世界": [
            {"emoji": "🐟", "name": "小鱼", "unit": "条"},
            {"emoji": "🐙", "name": "章鱼", "unit": "只"},
            {"emoji": "🦀", "name": "螃蟹", "unit": "只"},
            {"emoji": "🐚", "name": "贝壳", "unit": "个"},
        ],
        "动物园": [
            {"emoji": "🐵", "name": "猴子", "unit": "只"},
            {"emoji": "🐘", "name": "大象", "unit": "头"},
            {"emoji": "🦒", "name": "长颈鹿", "unit": "只"},
            {"emoji": "🐧", "name": "企鹅", "unit": "只"},
        ],
        "魔法城堡": [
            {"emoji": "🧙", "name": "魔法师", "unit": "个"},
            {"emoji": "🔮", "name": "水晶球", "unit": "个"},
            {"emoji": "📖", "name": "魔法书", "unit": "本"},
            {"emoji": "🗝️", "name": "钥匙", "unit": "把"},
        ],
    }
    
    scenes = theme_scenes.get(theme_name, theme_scenes["魔法城堡"])
    scene = random.choice(scenes)
    
    # Generate question based on week
    if week <= 2:
        # 10以内加减法
        a = random.randint(1, 7)
        b = random.randint(1, min(9 - a, 7))
        answer = a + b
        q_scene = f"{scene['emoji']} 小明有 {a} 个{scene['name']}，妈妈又买了 {b} 个<br>现在一共有几个{scene['name']}？"
    elif week <= 4:
        # 10-20不进位加法
        a = random.randint(10, 15)
        b = random.randint(1, min(9, 19 - a))
        answer = a + b
        q_scene = f"{scene['emoji']} 篮子里有 {a} 个{scene['name']}，又放进来了 {b} 个<br>现在一共有几个{scene['name']}？"
    elif week <= 6:
        # 10-20不退位减法
        a = random.randint(13, 19)
        b = random.randint(1, min(9, a - 10))
        answer = a - b
        q_scene = f"{scene['emoji']} 树上有 {a} 个{scene['name']}，被拿走了 {b} 个<br>还剩下几个{scene['name']}？"
    elif week <= 8:
        # 20以内进位加法
        a = random.randint(8, 15)
        b = random.randint(1, 9)
        while a + b <= 19 and a % 10 + b % 10 < 10:
            a = random.randint(8, 15)
            b = random.randint(1, 9)
        answer = a + b
        if answer > 20:
            a, b = 8, 5
            answer = 13
        q_scene = f"{scene['emoji']} 箱子里有 {a} 个{scene['name']}，又搬来了 {b} 个<br>现在一共有几个{scene['name']}？"
    else:
        # 20以内退位减法
        a = random.randint(12, 19)
        b = random.randint(3, 9)
        while a % 10 >= b % 10:
            a = random.randint(12, 19)
            b = random.randint(3, 9)
        answer = a - b
        q_scene = f"{scene['emoji']} 盘子里有 {a} 个{scene['name']}，吃掉了 {b} 个<br>还剩下几个{scene['name']}？"
    
    return {
        "id": f"q{q_num}",
        "type": "input",
        "scene": q_scene,
        "answer": str(answer),
        "explanation": {"ok": f"答对了！{answer}个，太棒了！🎉", "fix": f"正确答案是{answer}。"}
    }

def generate_all_questions(theme_name, theme_emoji, week):
    """Generate 10 questions (Q10 has 2 locks = 12 answer slots)."""
    questions = []
    
    # Q1-Q9: Regular questions
    for i in range(1, 10):
        q = generate_scene_question(theme_name, theme_emoji, week, i)
        
        # Check uniqueness
        max_attempts = 10
        while is_question_used(q["scene"], "math_scene") and max_attempts > 0:
            q = generate_scene_question(theme_name, theme_emoji, week, i)
            max_attempts -= 1
        
        mark_question_used(q["scene"], "math_scene")
        questions.append(q)
    
    # Q10: Two locks (two answers)
    a = random.randint(3, 9)
    b = random.randint(1, 5)
    c = random.randint(1, min(5, a + b))
    answer1 = a + b
    answer2 = answer1 - c
    
    lock_scene = f"第一关：{a} + {b} = ?<br>第二关：上一步的结果 - {c} = ?"
    questions.append({
        "id": "q10",
        "type": "multi-input",
        "scene": lock_scene,
        "answers": [str(answer1), str(answer2)],
        "explanation": {"ok": f"两关都通过了！{answer1} → {answer2} 🎉", "fix": f"第一关：{a}+{b}={answer1}，第二关：{answer1}-{c}={answer2}。"}
    })
    
    return questions

# ===== HTML Generation =====
def generate_html(date_str, questions):
    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    weekday = date_obj.weekday()
    theme_name, theme_emoji, theme_color = DAY_THEMES[weekday]
    
    date_display = date_obj.strftime("%Y年%m月%d日")
    weekday_names = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
    weekday_display = weekday_names[weekday]
    
    # Build answers JSON
    answers = {}
    explanations = {}
    for q in questions:
        if q["type"] == "multi-input":
            answers[q["id"] + "_1"] = q["answers"][0]
            answers[q["id"] + "_2"] = q["answers"][1]
            explanations[q["id"] + "_1"] = q["explanation"]
            explanations[q["id"] + "_2"] = q["explanation"]
        else:
            answers[q["id"]] = q["answer"]
            explanations[q["id"]] = q["explanation"]
    
    answers_json = json.dumps(answers, ensure_ascii=False)
    explanations_json = json.dumps(explanations, ensure_ascii=False)
    
    # Build question HTML
    questions_html = ""
    for i, q in enumerate(questions):
        q_num = i + 1
        if q["type"] == "multi-input":
            questions_html += f'''
    <!-- Q{q_num} -->
    <div class="quest-card lock-card" id="q{q_num}-card">
      <div class="quest-header">
        <span class="quest-num">{q_num}</span>
        <span style="font-weight:700;">双锁关卡</span>
      </div>
      <div class="quest-scene">{q["scene"]}</div>
      <div class="quest-row">
        <span class="quest-math">第一关：</span>
        <input type="number" class="answer-input" id="q{q_num}_1" data-answer="{q["answers"][0]}" min="0" max="99" inputmode="numeric" autocomplete="off">
      </div>
      <div class="quest-row">
        <span class="quest-math">第二关：</span>
        <input type="number" class="answer-input" id="q{q_num}_2" data-answer="{q["answers"][1]}" min="0" max="99" inputmode="numeric" autocomplete="off">
      </div>
      <div class="feedback" id="q{q_num}_1-fb"></div>
      <div class="feedback" id="q{q_num}_2-fb"></div>
    </div>
'''
        else:
            questions_html += f'''
    <!-- Q{q_num} -->
    <div class="quest-card" id="q{q_num}-card">
      <div class="quest-header">
        <span class="quest-num">{q_num}</span>
      </div>
      <div class="quest-scene">{q["scene"]}</div>
      <div class="quest-row">
        <span class="quest-math">答案是：</span>
        <input type="number" class="answer-input" id="q{q["id"]}" data-answer="{q["answer"]}" min="0" max="99" inputmode="numeric" autocomplete="off" oninput="checkSingle(this)" onblur="checkSingle(this)">
      </div>
      <div class="feedback" id="q{q["id"]}-fb"></div>
    </div>
'''
    
    # Coach notes based on week
    coach_notes = get_coach_notes(questions)
    
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>✨ Math Magic · 数学魔法师</title>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}

  :root {{
    --bg: #FFF8F0; --card: #FFFFFF; --primary: #FF6B6B;
    --accent: #4ECDC4; --gold: #FFD93D; --purple: #A78BFA;
    --blue: #60A5FA; --green: #34D399; --orange: #FB923C;
    --text: #2D3436; --text-light: #636E72;
    --success: #00B894; --success-bg: #E8FFF5;
    --error: #E17055; --error-bg: #FFF3ED;
    --radius: 16px; --shadow: 0 4px 20px rgba(0,0,0,0.08);
  }}

  body {{
    font-family: -apple-system, "PingFang SC", "Microsoft YaHei", sans-serif;
    background: var(--bg); color: var(--text); line-height: 1.6; min-height: 100vh;
  }}
  .container {{ max-width: 960px; margin: 0 auto; padding: 16px; }}

  .scoreboard {{
    position: sticky; top: 12px; z-index: 100;
    background: rgba(255,255,255,0.97); backdrop-filter: blur(12px);
    border-radius: var(--radius); padding: 14px 22px; margin-bottom: 20px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.12);
    display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 10px;
  }}
  .scoreboard .score {{ font-size: 18px; font-weight: 800; color: var(--text); }}
  .scoreboard .score .correct {{ color: var(--success); }}
  .scoreboard .status {{ font-size: 13px; color: var(--text-light); }}
  .progress-mini {{
    flex: 1; min-width: 120px; height: 8px; background: #E8E8E8; border-radius: 4px; overflow: hidden; margin: 0 16px;
  }}
  .progress-mini-fill {{ height: 100%; background: linear-gradient(90deg, var(--green), var(--accent)); border-radius: 4px; transition: width 0.4s ease; width: 0%; }}

  .header {{
    background: linear-gradient(135deg, #FF6B6B 0%, #FF8E53 50%, #FFD93D 100%);
    border-radius: var(--radius); padding: 28px 24px; text-align: center; color: white;
    margin-bottom: 20px; box-shadow: 0 8px 32px rgba(255,107,107,0.3);
  }}
  .header h1 {{ font-size: 1.7em; font-weight: 800; text-shadow: 0 2px 8px rgba(0,0,0,0.15); }}
  .header .subtitle {{ font-size: 1em; opacity: 0.95; margin-top: 6px; }}
  .header .date-badge {{ display: inline-block; background: rgba(255,255,255,0.25); backdrop-filter: blur(4px); padding: 4px 14px; border-radius: 20px; font-size: 0.85em; margin-top: 10px; }}

  .card {{
    background: var(--card); border-radius: 20px; padding: 22px 20px; margin-bottom: 20px; box-shadow: var(--shadow);
  }}
  .card h2 {{ font-size: 1.2em; font-weight: 800; margin-bottom: 14px; display: flex; align-items: center; gap: 8px; }}

  .quest-card {{
    background: #F8F9FA; border-radius: 14px; padding: 16px; margin-bottom: 14px;
    border-left: 5px solid #B0BEC5; transition: border-color 0.3s, background 0.3s;
  }}
  .quest-card.correct {{ background: var(--success-bg); border-left-color: var(--success); }}
  .quest-card.wrong {{ background: var(--error-bg); border-left-color: var(--error); }}
  .quest-card.checked {{ pointer-events: none; }}
  .lock-card {{ border-left-color: var(--gold); background: #FFFDF5; }}

  .quest-header {{ display: flex; align-items: center; gap: 10px; margin-bottom: 10px; }}
  .quest-num {{
    display: inline-flex; align-items: center; justify-content: center;
    background: var(--purple); color: #fff; width: 32px; height: 32px;
    border-radius: 50%; font-size: 14px; font-weight: 800; flex-shrink: 0;
  }}
  .quest-card.correct .quest-num {{ background: var(--success); }}
  .quest-card.wrong .quest-num {{ background: var(--error); }}

  .quest-scene {{ font-size: 15px; color: #555; line-height: 1.7; margin-bottom: 12px; }}
  .quest-row {{ display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }}
  .quest-math {{ font-size: 18px; font-weight: 700; color: var(--text); letter-spacing: 1px; }}

  .answer-input {{
    width: 70px; height: 44px; font-size: 20px; font-weight: 700; text-align: center;
    border: 3px solid #E0E0E0; border-radius: 12px; outline: none;
    transition: border-color 0.3s, background 0.3s; background: #FAFAFA;
    -webkit-appearance: none; appearance: none;
  }}
  .answer-input:focus {{ border-color: var(--accent); background: white; box-shadow: 0 0 0 3px rgba(78,205,196,0.15); }}
  .answer-input.correct-input {{ border-color: var(--success); background: #E8FFF5; color: #0A6B55; }}
  .answer-input.wrong-input {{ border-color: var(--error); background: #FFF3ED; color: #C0392B; }}

  .feedback {{ display: none; margin-top: 10px; font-size: 14px; font-weight: 600; line-height: 1.6; }}
  .feedback.show {{ display: block; }}
  .feedback.correct-fb {{ color: #0A6B55; }}
  .feedback.wrong-fb {{ color: #C0392B; }}

  .achievement-card {{
    background: linear-gradient(135deg, #fff8e1, #ffecb3);
    border: 3px solid #ffc107; text-align: center; padding: 26px 18px; margin-top: 20px;
  }}
  .medal {{ font-size: 56px; display: block; margin-bottom: 10px; }}
  .achievement-card h2 {{ color: #e65100; justify-content: center; font-size: 20px; }}
  .achievement-card .cheer {{ font-size: 16px; color: #bf360c; line-height: 2; margin-top: 8px; }}

  .coach-notes {{
    background: #F0F0F0; border-radius: var(--radius); padding: 20px 24px;
    margin-top: 24px; border-left: 5px solid var(--purple);
  }}
  .coach-notes h3 {{ font-size: 1em; color: var(--purple); margin-bottom: 10px; }}

  .divider {{ text-align: center; margin: 24px 0; font-size: 22px; letter-spacing: 10px; opacity: 0.5; }}

  .confetti-container {{ position: fixed; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; z-index: 9999; overflow: hidden; }}
  .confetti {{ position: absolute; top: -10px; opacity: 0; animation: confetti-fall 3s ease-out forwards; }}
  @keyframes confetti-fall {{ 0%{{opacity:1;transform:translateY(0) rotate(0deg)}} 100%{{opacity:0;transform:translateY(100vh) rotate(720deg)}} }}

  .retry-btn {{
    display: inline-flex; align-items: center; gap: 8px;
    background: linear-gradient(135deg, #6366f1, #8b5cf6); color: #fff; border: none;
    border-radius: 16px; padding: 12px 36px; font-size: 17px; font-weight: 700;
    cursor: pointer; box-shadow: 0 4px 15px rgba(99,102,241,0.3); transition: transform 0.2s;
  }}
  .retry-btn:hover {{ transform: scale(1.05); }}

  .submit-btn {{
    display: block; width: 100%; margin-top: 20px; padding: 16px;
    background: linear-gradient(135deg, #FF6B6B, #FF8E53); color: white; border: none;
    border-radius: 16px; font-size: 18px; font-weight: 700; cursor: pointer;
    box-shadow: 0 4px 15px rgba(255,107,107,0.3); transition: transform 0.2s;
  }}
  .submit-btn:hover {{ transform: scale(1.02); }}

  @media (max-width: 600px) {{
    .container {{ padding: 10px; }}
    .header h1 {{ font-size: 1.3em; }}
    .card {{ padding: 16px 12px; }}
    .quest-math {{ font-size: 16px; }}
    .answer-input {{ width: 60px; height: 42px; font-size: 18px; }}
  }}
</style>
</head>
<body>
<div class="container">

  <div class="scoreboard">
    <div class="score"><span class="correct" id="correctCount">0</span> / <span id="totalCount">12</span> 正确</div>
    <div class="progress-mini"><div class="progress-mini-fill" id="progressFill"></div></div>
    <div class="status" id="scoreStatus">{theme_emoji} 开始今天的魔法练习吧！</div>
  </div>

  <div class="header">
    <h1>✨ Math Magic · 数学魔法师</h1>
    <div class="subtitle">今日主题：{theme_emoji} <strong>{theme_name}</strong></div>
    <div class="date-badge">📅 {date_display} · {weekday_display}</div>
  </div>

  <div class="card">
    <h2>🧩 数学挑战</h2>
{questions_html}

    <button class="submit-btn" onclick="submitAll()">🎯 提交答案，解锁成就</button>
  </div>

  <div class="divider">🏆🏆🏆</div>

  <div class="card achievement-card" id="achievement" style="display:none;">
    <span class="medal" id="medal">🏆</span>
    <h2 id="achieveTitle">🎉 恭喜！🎉</h2>
    <div class="cheer" id="achieveText"></div>
  </div>

  <div style="text-align:center;margin-top:18px;">
    <button class="retry-btn" onclick="retry()">🔄 再试一次</button>
  </div>

  <div class="coach-notes">
    <h3>📝 教练笔记（家长参考）</h3>
    <p style="font-size:13px;color:var(--text-light);line-height:1.8;">{coach_notes}</p>
  </div>

  <div style="text-align:center;font-size:13px;color:var(--text-light);padding:24px 0;">✨ Math Magic · 数学魔法师 &nbsp;|&nbsp; 每天练习15分钟，数学思维节节高！🚀</div>
</div>

<div class="confetti-container" id="confettiContainer"></div>

<script>
const AudioCtx = window.AudioContext || window.webkitAudioContext;
let audioCtx;
function getAudioCtx() {{ if (!audioCtx) audioCtx = new AudioCtx(); return audioCtx; }}

function playCorrect() {{
  try {{
    const ctx = getAudioCtx();
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.connect(gain); gain.connect(ctx.destination);
    osc.type = 'sine';
    const t = ctx.currentTime;
    osc.frequency.setValueAtTime(523.25, t);
    osc.frequency.setValueAtTime(659.25, t + 0.1);
    osc.frequency.setValueAtTime(783.99, t + 0.2);
    gain.gain.setValueAtTime(0.3, t);
    gain.gain.exponentialRampToValueAtTime(0.001, t + 0.5);
    osc.start(t); osc.stop(t + 0.5);
  }} catch(e) {{}}
}}

function playWrong() {{
  try {{
    const ctx = getAudioCtx();
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.connect(gain); gain.connect(ctx.destination);
    osc.type = 'sawtooth';
    const t = ctx.currentTime;
    osc.frequency.setValueAtTime(300, t);
    osc.frequency.linearRampToValueAtTime(150, t + 0.4);
    gain.gain.setValueAtTime(0.15, t);
    gain.gain.exponentialRampToValueAtTime(0.001, t + 0.45);
    osc.start(t); osc.stop(t + 0.45);
  }} catch(e) {{}}
}}

function checkSingle(input) {{
  const val = input.value.trim();
  if (val === '') {{
    input.className = 'answer-input';
    const card = input.closest('.quest-card');
    if (card) {{
      card.className = card.classList.contains('lock-card') ? 'quest-card lock-card' : 'quest-card';
      const fb = card.querySelector('.feedback');
      if (fb) {{ fb.className = 'feedback'; fb.textContent = ''; }}
    }}
    return;
  }}
  const qId = input.id;
  const expected = answers[qId];
  const userAnswer = parseInt(val);
  if (isNaN(userAnswer)) return;

  const card = input.closest('.quest-card');
  const fb = card ? card.querySelector('.feedback') : null;

  if (String(userAnswer) === String(expected)) {{
    input.className = 'answer-input correct-input';
    if (fb) {{
      fb.className = 'feedback show correct-fb';
      const data = explanations[qId];
      fb.textContent = '✅ ' + (data ? data.ok : '答对了！🌟');
    }}
    playCorrect();
  }} else {{
    input.className = 'answer-input wrong-input';
    if (fb) {{
      fb.className = 'feedback show wrong-fb';
      const data = explanations[qId];
      fb.innerHTML = '❌ 不对哦<br>💡 正确答案：' + (data ? data.fix : expected);
    }}
    playWrong();
  }}
  updateScore();
}}

function updateScore() {{
  let correct = 0;
  document.querySelectorAll('.answer-input.correct-input').forEach(() => correct++);
  document.getElementById('correctCount').textContent = correct;
  document.getElementById('progressFill').style.width = (correct / 12 * 100) + '%';
}}

const TOTAL = 12;
const checked = new Set();
const answers = {answers_json};
const explanations = {explanations_json};

function submitAll() {{
  let correct = 0;
  document.querySelectorAll('.answer-input').forEach(input => {{
    const val = input.value.trim();
    if (val === '') return;
    const qId = input.id;
    checked.add(qId);
    if (String(parseInt(val)) === String(answers[qId])) {{
      correct++;
      input.className = 'answer-input correct-input';
    }} else {{
      input.className = 'answer-input wrong-input';
    }}
  }});
  
  document.getElementById('correctCount').textContent = correct;
  document.getElementById('progressFill').style.width = (correct / 12 * 100) + '%';
  
  if (correct === TOTAL) {{
    showAchievement(true);
  }} else {{
    showAchievement(false, correct);
  }}
}}

function showAchievement(perfect, score) {{
  const ach = document.getElementById('achievement');
  ach.style.display = 'block';
  if (perfect) {{
    document.getElementById('medal').textContent = '👑';
    document.getElementById('achieveTitle').textContent = '🎊 满分通关！数学大师！🎊';
    document.getElementById('achieveText').innerHTML = '12/12 全部正确！你已经是真正的数学魔法师了！✨';
    launchConfetti();
  }} else {{
    document.getElementById('medal').textContent = '🌟';
    document.getElementById('achieveTitle').textContent = `🌟 完成挑战！`;
    document.getElementById('achieveText').innerHTML = `答对了 ${{score}}/12 题，继续加油！每天进步一点点！💪`;
  }}
  ach.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
}}

function retry() {{
  checked.clear();
  document.querySelectorAll('.answer-input').forEach(input => {{
    input.value = '';
    input.className = 'answer-input';
  }});
  document.querySelectorAll('.feedback').forEach(fb => {{
    fb.className = 'feedback';
    fb.textContent = '';
  }});
  document.querySelectorAll('.quest-card').forEach(card => {{
    if (card.classList.contains('lock-card')) {{
      card.className = 'quest-card lock-card';
    }} else {{
      card.className = 'quest-card';
    }}
  }});
  document.getElementById('correctCount').textContent = '0';
  document.getElementById('progressFill').style.width = '0%';
  document.getElementById('achievement').style.display = 'none';
  window.scrollTo({{ top: 0, behavior: 'smooth' }});
}}

function launchConfetti() {{
  const container = document.getElementById('confettiContainer');
  container.innerHTML = '';
  const colors = ['#FF6B6B','#FFD93D','#4ECDC4','#A78BFA','#60A5FA','#34D399','#FB923C','#F472B6'];
  for (let i = 0; i < 80; i++) {{
    const c = document.createElement('div');
    c.className = 'confetti';
    c.style.left = Math.random() * 100 + '%';
    c.style.animationDelay = Math.random() * 2 + 's';
    c.style.animationDuration = (2 + Math.random() * 2) + 's';
    c.style.backgroundColor = colors[Math.floor(Math.random() * colors.length)];
    c.style.borderRadius = Math.random() > 0.5 ? '50%' : '2px';
    c.style.width = (6 + Math.random() * 8) + 'px';
    c.style.height = (6 + Math.random() * 8) + 'px';
    container.appendChild(c);
  }}
  setTimeout(() => container.innerHTML = '', 5000);
}}

document.querySelectorAll('.answer-input').forEach(input => {{
  input.addEventListener('keydown', function(e) {{
    if (e.key === 'Enter') {{ e.preventDefault(); checkSingle(this); }}
  }});
}});
</script>
</body>
</html>'''
    
    return html

def get_coach_notes(questions):
    """Generate coach notes based on current week's focus."""
    return "今日练习重点：帮助孩子理解题目情境，鼓励大声读题。Q10双锁关卡训练连续运算能力，引导孩子先算第一步，再算第二步。注意书写工整，养成检查的好习惯。"

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 generate.py YYYY-MM-DD [--output-dir DIR]")
        sys.exit(1)
    
    date_str = sys.argv[1]
    output_dir = OUTPUT_DIR
    
    if "--output-dir" in sys.argv:
        idx = sys.argv.index("--output-dir")
        if idx + 1 < len(sys.argv):
            output_dir = Path(sys.argv[idx + 1])
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    week = get_week_number("2026-04-14", date_str)
    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    weekday = date_obj.weekday()
    theme_name, theme_emoji, _ = DAY_THEMES[weekday]
    
    random.seed(date_str)
    
    questions = generate_all_questions(theme_name, theme_emoji, week)
    html = generate_html(date_str, questions)
    
    output_file = output_dir / f"{date_str}-math-magic.html"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html)
    
    print(f"Generated: {output_file}")
    
    history = load_history()
    history["last_date"] = date_str
    save_history(history)

if __name__ == "__main__":
    main()
