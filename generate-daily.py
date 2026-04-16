#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数学魔法师 - 每日自动练习生成脚本
根据学习计划自动生成当天的数学练习HTML
难度循序渐进，目标：上海实验小学自主招生
"""

import datetime
import random
import os
import subprocess
import sys

# 配置
WORKSPACE = "/Users/solomon/workspace/QoderWork/math-magic"
START_DATE = datetime.date(2026, 4, 14)
REPO_URL = "https://solomonhe-hgx.github.io/math-magic/"

# 主题轮换（周一到周五）
THEMES = {
    1: {"name": "超市购物", "emoji": "🛒", "bg": "linear-gradient(180deg, #ff6b6b 0%, #ee5a24 30%, #e55039 60%, #b71540 100%)"},
    2: {"name": "太空探险", "emoji": "🚀", "bg": "linear-gradient(180deg, #0d1b2a 0%, #1b2838 30%, #2d3a5e 60%, #4a5f8a 100%)"},
    3: {"name": "海底世界", "emoji": "🌊", "bg": "linear-gradient(180deg, #0a4d8c 0%, #0b6e9f 30%, #118ab2 60%, #073b4c 100%)"},
    4: {"name": "动物园", "emoji": "🦁", "bg": "linear-gradient(180deg, #87ceeb 0%, #90EE90 40%, #228B22 80%, #006400 100%)"},
    5: {"name": "魔法城堡", "emoji": "🏰", "bg": "linear-gradient(180deg, #6c5ce7 0%, #a29bfe 30%, #6c5ce7 60%, #2d1b69 100%)"},
}

WEEKEND_THEME = {"name": "周末复习", "emoji": "📝", "bg": "linear-gradient(180deg, #636e72 0%, #2d3436 30%, #636e72 60%, #2d3436 100%)"}

# 各周难度配置
PHASES = [
    # (开始周, 结束周, 难度名称, 题目生成器)
    (1, 2, "10以内加减法", "phase1"),
    (3, 4, "10-20不进位加法", "phase2"),
    (5, 6, "10-20不退位减法", "phase3"),
    (7, 8, "20以内进位加法", "phase4"),
    (9, 10, "20以内退位减法", "phase5"),
    (11, 12, "20以内加减法混合", "phase6"),
    (13, 14, "认识100以内的数", "phase7"),
    (15, 16, "整十数加减法", "phase8"),
    (17, 18, "两位数加减一位数", "phase9"),
    (19, 20, "两位数加减两位数", "phase10"),
    (21, 22, "100以内加减法综合", "phase11"),
    (23, 24, "认识人民币", "phase12"),
    (25, 26, "认识钟表", "phase13"),
]


def get_current_week(today=None):
    if today is None:
        today = datetime.date.today()
    elapsed = (today - START_DATE).days
    return max(1, elapsed // 7 + 1)


def get_phase_info(week):
    for start, end, name, generator in PHASES:
        if start <= week <= end:
            return {"name": name, "generator": generator}
    # 超出范围，使用最后一个阶段
    return {"name": "综合复习冲刺", "generator": "phase13"}


def random_q(min_val, max_val):
    """生成随机题目"""
    a = random.randint(min_val, max_val)
    b = random.randint(min_val, max_val)
    return a, b


def gen_no_carry_add():
    """不进位加法: 十几+个位，个位和<=9"""
    a = random.randint(11, 19)
    a_unit = a % 10
    max_b = 9 - a_unit
    if max_b < 1:
        max_b = 1
    b = random.randint(1, max_b)
    return a, b, a + b


def gen_no_borrow_sub():
    """不退位减法: 十几-个位，个位够减"""
    a = random.randint(12, 19)
    a_unit = a % 10
    if a_unit < 1:
        a_unit = 1
    b = random.randint(1, a_unit)
    return a, b, a - b


def gen_carry_add():
    """进位加法: 个位和>9，总和<=20"""
    a = random.randint(2, 9)
    a_unit = a % 10
    b = random.randint(10 - a_unit, 9)
    if a + b > 20:
        b = 20 - a
    if b < 1:
        b = 1
    return a, b, a + b


def gen_borrow_sub():
    """退位减法: 被减数个位<减数个位"""
    a = random.randint(12, 19)
    a_unit = a % 10
    b = random.randint(a_unit + 1, 9)
    if b >= a:
        b = a - 1
    if b < 1:
        b = 1
    return a, b, a - b


def gen_mixed_20():
    """20以内混合"""
    if random.random() < 0.5:
        a, b = random_q(2, 15), random_q(2, 15)
        if a[0] + b[0] > 20:
            b = (20 - a[0],)
        return a[0], b[0], a[0] + b[0], "+"
    else:
        a = random.randint(5, 19)
        b = random.randint(1, a - 1)
        return a, b, a - b, "-"


def generate_questions_for_phase(phase, count=10):
    """根据阶段生成题目"""
    questions = []
    generator = phase["generator"]

    for _ in range(count):
        if generator == "phase1":
            # 10以内加减法
            if random.random() < 0.5:
                a = random.randint(1, 9)
                b = random.randint(1, 10 - a)
                questions.append({"a": a, "b": b, "op": "+", "answer": a + b})
            else:
                a = random.randint(2, 10)
                b = random.randint(1, a - 1)
                questions.append({"a": a, "b": b, "op": "-", "answer": a - b})
        elif generator == "phase2":
            # 不进位加法为主
            a, b, ans = gen_no_carry_add()
            questions.append({"a": a, "b": b, "op": "+", "answer": ans})
        elif generator == "phase3":
            # 不退位减法为主
            a, b, ans = gen_no_borrow_sub()
            questions.append({"a": a, "b": b, "op": "-", "answer": ans})
        elif generator == "phase4":
            # 进位加法
            a, b, ans = gen_carry_add()
            questions.append({"a": a, "b": b, "op": "+", "answer": ans})
        elif generator == "phase5":
            # 退位减法
            a, b, ans = gen_borrow_sub()
            questions.append({"a": a, "b": b, "op": "-", "answer": ans})
        elif generator == "phase6":
            # 混合
            a, b, ans, op = gen_mixed_20()
            questions.append({"a": a, "b": b, "op": op, "answer": ans})
        elif generator in ("phase7", "phase8", "phase9", "phase10", "phase11"):
            # 100以内计算
            a = random.randint(10, 80)
            b = random.randint(10, 80)
            if random.random() < 0.5:
                if a + b > 100:
                    b = 100 - a
                questions.append({"a": a, "b": b, "op": "+", "answer": a + b})
            else:
                if b >= a:
                    b = a - 1
                if b < 1:
                    b = 1
                questions.append({"a": a, "b": b, "op": "-", "answer": a - b})
        elif generator in ("phase12", "phase13"):
            # 综合
            a = random.randint(10, 90)
            b = random.randint(5, 50)
            if random.random() < 0.5:
                if a + b > 100:
                    b = 100 - a
                questions.append({"a": a, "b": b, "op": "+", "answer": a + b})
            else:
                if b >= a:
                    b = a - 1
                if b < 1:
                    b = 1
                questions.append({"a": a, "b": b, "op": "-", "answer": a - b})

    return questions


def get_scene_text(a, b, op, theme_name):
    """根据主题生成场景文字"""
    scenes = {
        "超市购物": {
            "+": f"货架上有{a}个苹果，又补了{b}个，现在有几个？",
            "-": f"购物车里有{a}件商品，放了{b}件回去，还剩几件？",
        },
        "太空探险": {
            "+": f"飞船有{a}桶燃料，又加了{b}桶，一共有几桶？",
            "-": f"月球基地有{a}颗能量石，用了{b}颗，还剩几颗？",
        },
        "海底世界": {
            "+": f"海底有{a}条小鱼，又来了{b}条，一共几条？",
            "-": f"珊瑚丛有{a}只螃蟹，爬走了{b}只，还剩几只？",
        },
        "动物园": {
            "+": f"动物园有{a}只小鸟，又飞来{b}只，一共几只？",
            "-": f"猴山有{a}只猴子，走了{b}只，还剩几只？",
        },
        "魔法城堡": {
            "+": f"魔法书有{a}页，又学了{b}页，一共几页？",
            "-": f"魔法书有{a}个咒语，学会了{b}个，还有几个？",
        },
        "周末复习": {
            "+": f"有{a}个，又来了{b}个，一共几个？",
            "-": f"有{a}个，拿走了{b}个，还剩几个？",
        },
    }
    theme_scenes = scenes.get(theme_name, scenes["周末复习"])
    return theme_scenes.get(op, f"{a} {op} {b} = ?")


def generate_html(today, theme, week, phase_info, questions):
    """生成完整的HTML"""
    date_str = today.strftime("%Y-%m-%d")
    date_cn = today.strftime("%Y年%m月%d日")
    day_name = ["", "一", "二", "三", "四", "五", "六", "日"][today.isoweekday()]

    # 热身题
    w1_a = random.randint(5, 9)
    w1_b = random.randint(1, 10 - w1_a)
    w1_ans = w1_a + w1_b
    w2_a = random.randint(11, 18)
    w2_b = random.randint(1, 9 - (w2_a % 10))
    w2_ans = w2_a + w2_b

    # 互动挑战
    c_a = random.randint(10, 19)
    c_b = random.randint(1, 9 - (c_a % 10) if c_a % 10 < 9 else 1)
    c_ans = c_a + c_b
    c2_a = random.randint(12, 19)
    c2_b = random.randint(1, c2_a % 10)
    c2_ans = c2_a - c2_b
    c3_a = random.randint(10, 19)
    c3_b = random.randint(1, 9 - (c3_a % 10) if c3_a % 10 < 9 else 1)
    c3_ans = c3_a + c3_b
    c4_a = random.randint(12, 19)
    c4_b = random.randint(1, c4_a % 10)
    c4_ans = c4_a - c4_b

    # 找最大值
    results = {"A": c_ans, "B": c2_ans, "C": c3_ans, "D": c4_ans}
    max_val = max(results.values())
    max_keys = [k for k, v in results.items() if v == max_val]

    # 核心题目HTML
    core_html = ""
    for i, q in enumerate(questions):
        scene = get_scene_text(q["a"], q["b"], q["op"], theme["name"])
        core_html += f"""
    <div class="question-card" id="core{i+1}">
      <div class="question-text">{theme['emoji']} {scene}<input type="number" class="answer-input" data-answer="{q['answer']}" oninput="checkAnswer(this)" onblur="checkAnswer(this)" onkeydown="handleEnter(event, this)"></div>
      <div class="feedback"></div>
    </div>"""

    # 最大值选项高亮
    def challenge_class(key):
        return ' data-correct="true"' if key in max_keys else ""

    max_keys_str = "和".join(max_keys)
    max_desc = f"{max_keys_str}选项的{max_val}最大"

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{theme['emoji']} {theme['name']} - 数学魔法任务 {date_str}</title>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}

  body {{
    font-family: "Comic Sans MS", "PingFang SC", "Microsoft YaHei", sans-serif;
    background: {theme['bg']};
    min-height: 100vh;
    padding: 20px;
    color: #fff;
    overflow-x: hidden;
  }}

  .container {{ max-width: 960px; margin: 0 auto; }}

  .header {{
    text-align: center; margin-bottom: 24px;
    background: rgba(255,255,255,0.15); backdrop-filter: blur(8px);
    border-radius: 24px; padding: 20px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.2);
  }}
  .header h1 {{ font-size: 32px; margin-bottom: 8px; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }}

  .scoreboard {{
    display: flex; justify-content: center; align-items: center; gap: 16px;
    font-size: 22px; font-weight: bold;
  }}
  .scoreboard .score {{
    background: #ffd166; color: #073b4c;
    padding: 8px 24px; border-radius: 16px; min-width: 120px;
  }}
  .retry-btn {{
    background: #ef476f; color: #fff; border: none;
    padding: 10px 24px; border-radius: 16px; font-size: 18px;
    cursor: pointer; transition: transform 0.2s, background 0.2s;
    min-height: 44px; min-width: 44px;
  }}
  .retry-btn:hover {{ background: #d63a5e; transform: scale(1.05); }}
  .retry-btn:active {{ transform: scale(0.95); }}

  .section {{
    background: rgba(255,255,255,0.12); backdrop-filter: blur(6px);
    border-radius: 24px; padding: 24px; margin-bottom: 24px;
    box-shadow: 0 4px 16px rgba(0,0,0,0.15);
  }}
  .section-title {{
    font-size: 26px; margin-bottom: 16px; text-align: center;
    text-shadow: 1px 1px 3px rgba(0,0,0,0.3);
  }}

  .question-card {{
    background: rgba(255,255,255,0.18); border-radius: 16px;
    padding: 16px 20px; margin-bottom: 12px;
    display: flex; align-items: center; justify-content: space-between;
    flex-wrap: wrap; gap: 12px; transition: background 0.3s;
  }}
  .question-card.correct {{ background: rgba(81, 207, 102, 0.35); }}
  .question-card.wrong {{ background: rgba(255, 183, 77, 0.35); }}

  .question-text {{ font-size: 24px; font-weight: bold; flex: 1; min-width: 200px; }}

  .answer-input {{
    width: 80px; height: 50px; font-size: 26px; text-align: center;
    border: 3px solid #ffd166; border-radius: 14px; outline: none;
    background: #fff; color: #073b4c; font-weight: bold;
    transition: border-color 0.3s, background 0.3s;
    -moz-appearance: textfield;
  }}
  .answer-input::-webkit-outer-spin-button,
  .answer-input::-webkit-inner-spin-button {{ -webkit-appearance: none; margin: 0; }}
  .answer-input.correct {{ border-color: #51cf66; background: #d3f9d8; }}
  .answer-input.wrong {{ border-color: #ffa94d; background: #fff3e0; }}

  .feedback {{ font-size: 22px; min-width: 80px; min-height: 30px; }}

  .challenge-option {{
    display: inline-block; background: rgba(255,255,255,0.25);
    border: 3px solid #ffd166; border-radius: 14px;
    padding: 12px 20px; margin: 6px; font-size: 22px; font-weight: bold;
    cursor: pointer; transition: all 0.2s; min-height: 44px; min-width: 44px;
  }}
  .challenge-option:hover {{ background: rgba(255,255,255,0.4); transform: scale(1.05); }}
  .challenge-option.correct-choice {{ background: #51cf66; border-color: #51cf66; color: #fff; }}
  .challenge-option.wrong-choice {{ background: #ef476f; border-color: #ef476f; color: #fff; }}

  .achievement {{ text-align: center; padding: 30px; display: none; }}
  .achievement.show {{ display: block; }}
  .achievement h2 {{ font-size: 36px; margin-bottom: 16px; animation: bounce 0.6s ease infinite alternate; }}
  .achievement .badge {{ font-size: 64px; margin: 16px 0; }}
  .achievement p {{ font-size: 22px; margin-bottom: 8px; }}
  @keyframes bounce {{ from {{ transform: translateY(0); }} to {{ transform: translateY(-10px); }} }}

  .confetti-container {{
    position: fixed; top: 0; left: 0; right: 0; bottom: 0;
    pointer-events: none; z-index: 999; overflow: hidden;
  }}
  .confetti {{
    position: absolute; width: 10px; height: 10px; border-radius: 2px;
    animation: fall 2.5s ease-out forwards;
  }}
  @keyframes fall {{
    0% {{ transform: translateY(-20px) rotate(0deg); opacity: 1; }}
    100% {{ transform: translateY(100vh) rotate(720deg); opacity: 0; }}
  }}

  .bubble {{
    position: fixed; border-radius: 50%;
    background: rgba(255,255,255,0.1);
    animation: float-up 8s ease-in infinite;
    pointer-events: none;
  }}
  @keyframes float-up {{
    0% {{ transform: translateY(100vh) scale(0.5); opacity: 0.6; }}
    100% {{ transform: translateY(-100px) scale(1); opacity: 0; }}
  }}

  @media (max-width: 599px) {{
    body {{ padding: 12px; }}
    .header h1 {{ font-size: 24px; }}
    .scoreboard {{ font-size: 18px; gap: 10px; }}
    .scoreboard .score {{ padding: 6px 16px; min-width: 100px; }}
    .section {{ padding: 16px; border-radius: 18px; }}
    .section-title {{ font-size: 22px; }}
    .question-card {{ padding: 12px 14px; flex-direction: column; align-items: flex-start; }}
    .question-text {{ font-size: 20px; }}
    .answer-input {{ width: 70px; height: 46px; font-size: 22px; }}
    .feedback {{ font-size: 18px; }}
    .challenge-option {{ font-size: 18px; padding: 10px 16px; }}
    .achievement h2 {{ font-size: 28px; }}
    .achievement .badge {{ font-size: 48px; }}
  }}
  @media (min-width: 600px) and (max-width: 1023px) {{ .container {{ max-width: 700px; }} }}
  @media (min-width: 1024px) {{ .container {{ max-width: 960px; }} }}
</style>
</head>
<body>

<div id="bubbles"></div>
<div class="confetti-container" id="confetti-container"></div>

<div class="container">
  <div class="header">
    <h1>{theme['emoji']} {theme['name']} {theme['emoji']}</h1>
    <p style="font-size:16px; margin-bottom:12px; opacity:0.85;">数学魔法任务 · {date_cn} 星期{day_name} · 第{week}周 · {phase_info['name']}</p>
    <div class="scoreboard">
      <span>答对：</span>
      <span class="score" id="score-display">0 / 11</span>
      <button class="retry-btn" id="retry-btn" onclick="retryAll()">🔄 再试一次</button>
    </div>
  </div>

  <!-- 热身 -->
  <div class="section">
    <div class="section-title">🔥 热身小游戏：动动身体算一算（2分钟）</div>
    <p style="text-align:center; font-size:18px; margin-bottom:16px;">站起来！边做动作边算题！</p>
    <div style="text-align:center; font-size:18px; margin-bottom:16px; padding:16px; background:rgba(255,255,255,0.15); border-radius:16px;">
      <p style="font-size:22px; margin-bottom:12px;">👋 <strong>第一题：</strong>有 <strong style="color:#ffd166; font-size:26px;">{w1_a}</strong> 个，又加 <strong style="color:#ffd166; font-size:26px;">{w1_b}</strong> 个，一共几个？</p>
      <p style="font-size:16px; opacity:0.8; margin-bottom:12px;">（踮起脚尖，用手指比出答案，然后输入）</p>
      <input type="number" class="answer-input" data-answer="{w1_ans}" oninput="checkAnswer(this)" onblur="checkAnswer(this)" onkeydown="handleEnter(event, this)" style="margin:0 auto; display:block;">
    </div>
    <div style="text-align:center; font-size:18px; padding:16px; background:rgba(255,255,255,0.15); border-radius:16px;">
      <p style="font-size:22px; margin-bottom:12px;">👋 <strong>第二题：</strong>有 <strong style="color:#ffd166; font-size:26px;">{w2_a}</strong> 个，又加 <strong style="color:#ffd166; font-size:26px;">{w2_b}</strong> 个，一共几个？</p>
      <p style="font-size:16px; opacity:0.8; margin-bottom:12px;">（挥动双臂，然后输入答案）</p>
      <input type="number" class="answer-input" data-answer="{w2_ans}" oninput="checkAnswer(this)" onblur="checkAnswer(this)" onkeydown="handleEnter(event, this)" style="margin:0 auto; display:block;">
    </div>
  </div>

  <!-- 核心任务 -->
  <div class="section">
    <div class="section-title">⭐ 今日核心任务：{theme['name']}计算（8分钟）</div>
    <p style="text-align:center; font-size:18px; margin-bottom:16px;">{phase_info['name']} · 帮小朋友算出正确答案！</p>
    {core_html}
  </div>

  <!-- 互动挑战 -->
  <div class="section">
    <div class="section-title">🎮 互动挑战：哪个结果最大？（3-5分钟）</div>
    <p style="text-align:center; font-size:18px; margin-bottom:16px;">算出每个式子的结果，选出最大的！</p>

    <div style="text-align:center; margin-bottom:20px;">
      <div class="challenge-option" data-value="{c_ans}"{challenge_class("A")} onclick="selectChallenge(this, event)">A. {c_a} + {c_b} = {c_ans}</div>
      <div class="challenge-option" data-value="{c2_ans}"{challenge_class("B")} onclick="selectChallenge(this, event)">B. {c2_a} - {c2_b} = {c2_ans}</div>
      <div class="challenge-option" data-value="{c3_ans}"{challenge_class("C")} onclick="selectChallenge(this, event)">C. {c3_a} + {c3_b} = {c3_ans}</div>
      <div class="challenge-option" data-value="{c4_ans}"{challenge_class("D")} onclick="selectChallenge(this, event)">D. {c4_a} - {c4_b} = {c4_ans}</div>
    </div>

    <p style="text-align:center; font-size:20px; margin:16px 0;">🤔 <strong style="color:#ffd166;">哪个结果最大？选出所有最大的选项！</strong></p>

    <div style="text-align:center;">
      <div class="challenge-option" data-challenge-final="A" onclick="selectFinalAnswer(this, event)">A. {c_ans}</div>
      <div class="challenge-option" data-challenge-final="B" onclick="selectFinalAnswer(this, event)">B. {c2_ans}</div>
      <div class="challenge-option" data-challenge-final="C" onclick="selectFinalAnswer(this, event)">C. {c3_ans}</div>
      <div class="challenge-option" data-challenge-final="D" onclick="selectFinalAnswer(this, event)">D. {c4_ans}</div>
    </div>

    <div id="challenge-feedback" style="text-align:center; font-size:20px; min-height:36px; margin-top:16px;"></div>
  </div>

  <!-- 成就 -->
  <div class="section achievement" id="achievement">
    <h2>🎉 太棒了！</h2>
    <div class="badge">🏆{theme['emoji']}🌟</div>
    <p>你完成了所有{theme['name']}数学魔法任务！</p>
    <p id="achievement-detail"></p>
    <p style="font-size:18px; margin-top:12px; opacity:0.8;">明天继续来探险吧！🎈</p>
  </div>
</div>

<script>
const AudioCtx = window.AudioContext || window.webkitAudioContext;
let audioCtx = null;
function getAudioCtx() {{ if (!audioCtx) audioCtx = new AudioCtx(); return audioCtx; }}

function playCorrectSound() {{
  try {{
    const ctx = getAudioCtx();
    [523.25, 659.25, 783.99].forEach((f, i) => {{
      const o = ctx.createOscillator(), g = ctx.createGain();
      o.type = 'sine'; o.frequency.value = f;
      g.gain.setValueAtTime(0.2, ctx.currentTime + i * 0.1);
      g.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + i * 0.1 + 0.4);
      o.connect(g); g.connect(ctx.destination);
      o.start(ctx.currentTime + i * 0.1); o.stop(ctx.currentTime + i * 0.1 + 0.4);
    }});
  }} catch(e) {{}}
}}

function playWrongSound() {{
  try {{
    const ctx = getAudioCtx(), o = ctx.createOscillator(), g = ctx.createGain();
    o.type = 'triangle';
    o.frequency.setValueAtTime(300, ctx.currentTime);
    o.frequency.exponentialRampToValueAtTime(150, ctx.currentTime + 0.3);
    g.gain.setValueAtTime(0.2, ctx.currentTime);
    g.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.3);
    o.connect(g); g.connect(ctx.destination); o.start(); o.stop(ctx.currentTime + 0.3);
  }} catch(e) {{}}
}}

function launchConfetti() {{
  const c = document.getElementById('confetti-container');
  const colors = ['#ff6b6b','#ffd166','#51cf66','#339af0','#cc5de8','#ff922b','#20c997'];
  for (let i = 0; i < 80; i++) {{
    const d = document.createElement('div');
    d.className = 'confetti';
    d.style.left = Math.random() * 100 + '%';
    d.style.backgroundColor = colors[Math.floor(Math.random() * colors.length)];
    d.style.animationDelay = Math.random() * 1.5 + 's';
    d.style.animationDuration = (2 + Math.random() * 1.5) + 's';
    d.style.width = (6 + Math.random() * 8) + 'px';
    d.style.height = (6 + Math.random() * 8) + 'px';
    c.appendChild(d);
  }}
  setTimeout(() => {{ c.innerHTML = ''; }}, 4000);
}}

function createBubbles() {{
  const c = document.getElementById('bubbles');
  for (let i = 0; i < 12; i++) {{
    const b = document.createElement('div');
    b.className = 'bubble';
    const size = 20 + Math.random() * 40;
    b.style.width = size + 'px';
    b.style.height = size + 'px';
    b.style.left = Math.random() * 100 + '%';
    b.style.animationDelay = Math.random() * 8 + 's';
    b.style.animationDuration = (6 + Math.random() * 6) + 's';
    c.appendChild(b);
  }}
}}
createBubbles();

let answeredCorrectly = new Set();
let challengeCorrect = false;

function updateScore() {{
  const coreInputs = document.querySelectorAll('#core1 .answer-input, #core2 .answer-input, #core3 .answer-input, #core4 .answer-input, #core5 .answer-input, #core6 .answer-input, #core7 .answer-input, #core8 .answer-input, #core9 .answer-input, #core10 .answer-input');
  let coreCorrect = 0;
  coreInputs.forEach(i => {{ if (i.classList.contains('correct')) coreCorrect++; }});
  let total = coreCorrect + (challengeCorrect ? 1 : 0);
  document.getElementById('score-display').textContent = total + ' / 11';
  if (coreCorrect === 10 && challengeCorrect) showAchievement();
}}

function checkAnswer(input) {{
  const userAnswer = parseInt(input.value);
  const correctAnswer = parseInt(input.dataset.answer);
  const card = input.closest('.question-card');
  const fbSpan = card ? card.querySelector('.feedback') : null;
  if (isNaN(userAnswer) || input.value === '') {{
    input.classList.remove('correct', 'wrong');
    if (card) card.classList.remove('correct', 'wrong');
    if (fbSpan) fbSpan.innerHTML = '';
    updateScore(); return;
  }}
  if (userAnswer === correctAnswer) {{
    input.classList.remove('wrong'); input.classList.add('correct');
    if (card) {{ card.classList.remove('wrong'); card.classList.add('correct'); }}
    if (fbSpan) fbSpan.innerHTML = '<span style="color:#51cf66;">✅ 太棒了！</span>';
    playCorrectSound();
  }} else {{
    input.classList.remove('correct'); input.classList.add('wrong');
    if (card) {{ card.classList.remove('correct'); card.classList.add('wrong'); }}
    if (fbSpan) fbSpan.innerHTML = '<span style="color:#ffa94d;">❌ 答案是 ' + correctAnswer + '</span>';
    playWrongSound();
  }}
  updateScore();
}}

function handleEnter(event, input) {{
  if (event.key === 'Enter') {{
    event.preventDefault(); checkAnswer(input);
    const allInputs = Array.from(document.querySelectorAll('.answer-input'));
    const idx = allInputs.indexOf(input);
    if (idx < allInputs.length - 1) allInputs[idx + 1].focus();
  }}
}}

function selectChallenge(el, event) {{
  event.stopPropagation();
  const options = document.querySelectorAll('.challenge-option[data-value]');
  options.forEach(o => o.classList.remove('selected', 'correct-choice', 'wrong-choice'));
  if (el.dataset.correct === 'true') {{
    el.classList.add('correct-choice');
    document.getElementById('challenge-feedback').innerHTML = '<span style="color:#51cf66;">✅ 答对了！</span>';
    playCorrectSound();
  }} else {{
    el.classList.add('wrong-choice');
    options.forEach(o => {{ if (o.dataset.correct === 'true') o.classList.add('correct-choice'); }});
    document.getElementById('challenge-feedback').innerHTML = '<span style="color:#ffa94d;">❌ 看看正确答案吧！</span>';
    playWrongSound();
  }}
}}

function selectFinalAnswer(el, event) {{
  event.stopPropagation();
  const options = document.querySelectorAll('[data-challenge-final]');
  const selected = el.dataset.challengeFinal;
  options.forEach(o => o.classList.remove('selected', 'correct-choice', 'wrong-choice'));
  const vals = {{'A': {c_ans}, 'B': {c2_ans}, 'C': {c3_ans}, 'D': {c4_ans}}};
  const maxVal = {max_val};
  const correctOnes = Object.keys(vals).filter(k => vals[k] === maxVal);
  if (correctOnes.includes(selected)) {{
    el.classList.add('correct-choice');
    options.forEach(o => {{ if (correctOnes.includes(o.dataset.challengeFinal)) o.classList.add('correct-choice'); }});
    document.getElementById('challenge-feedback').innerHTML = '<span style="color:#51cf66;">✅ 太聪明了！{max_desc}！</span>';
    challengeCorrect = true; playCorrectSound();
  }} else {{
    el.classList.add('wrong-choice');
    options.forEach(o => {{ if (correctOnes.includes(o.dataset.challengeFinal)) o.classList.add('correct-choice'); }});
    document.getElementById('challenge-feedback').innerHTML = '<span style="color:#ffa94d;">❌ 再想想哦！{max_desc}！</span>';
    challengeCorrect = false; playWrongSound();
  }}
  updateScore();
}}

function showAchievement() {{
  const ach = document.getElementById('achievement');
  if (ach.classList.contains('show')) return;
  ach.classList.add('show');
  document.getElementById('achievement-detail').textContent = '你答对了全部11道题，真是数学小达人！';
  launchConfetti();
  try {{
    const ctx = getAudioCtx();
    [523.25, 587.33, 659.25, 698.46, 783.99, 880, 987.77, 1046.5].forEach((f, i) => {{
      const o = ctx.createOscillator(), g = ctx.createGain();
      o.type = 'sine'; o.frequency.value = f;
      g.gain.setValueAtTime(0.15, ctx.currentTime + i * 0.12);
      g.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + i * 0.12 + 0.3);
      o.connect(g); g.connect(ctx.destination);
      o.start(ctx.currentTime + i * 0.12); o.stop(ctx.currentTime + i * 0.12 + 0.3);
    }});
  }} catch(e) {{}}
}}

function retryAll() {{
  document.querySelectorAll('.answer-input').forEach(i => {{ i.value = ''; i.classList.remove('correct', 'wrong'); }});
  document.querySelectorAll('.feedback').forEach(f => {{ f.innerHTML = ''; }});
  document.querySelectorAll('.question-card').forEach(c => {{ c.classList.remove('correct', 'wrong'); }});
  document.querySelectorAll('.section:nth-of-type(2) div[style*="text-align"]').forEach(d => {{ d.classList.remove('correct', 'wrong'); }});
  document.querySelectorAll('.challenge-option').forEach(o => {{ o.classList.remove('selected', 'correct-choice', 'wrong-choice'); }});
  document.getElementById('challenge-feedback').innerHTML = '';
  challengeCorrect = false; answeredCorrectly.clear(); updateScore();
  document.getElementById('achievement').classList.remove('show');
  const first = document.querySelector('.answer-input');
  if (first) first.focus();
}}

updateScore();
</script>
</body>
</html>"""
    return html


def main():
    today = datetime.date.today()
    date_str = today.strftime("%Y-%m-%d")
    file_name = f"{date_str}-math-magic.html"
    file_path = os.path.join(WORKSPACE, file_name)

    # 如果已存在则跳过
    if os.path.exists(file_path):
        print(f"今日练习已存在: {file_name}")
        return

    # 计算周数
    week = get_current_week(today)
    phase_info = get_phase_info(week)

    # 获取主题
    dow = today.isoweekday()
    theme = THEMES.get(dow, WEEKEND_THEME)

    # 生成题目
    random.seed(today.toordinal())  # 每天固定种子，保证同一天题目一致
    questions = generate_questions_for_phase(phase_info, count=10)

    # 生成HTML
    html = generate_html(today, theme, week, phase_info, questions)

    # 写入文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"✅ 已生成: {file_name}")
    print(f"   主题: {theme['emoji']} {theme['name']}")
    print(f"   周数: 第{week}周")
    print(f"   难度: {phase_info['name']}")

    # 提交到GitHub
    os.chdir(WORKSPACE)
    subprocess.run(["git", "add", "-f", file_name], check=True)
    subprocess.run(["git", "commit", "-m", f"每日数学练习自动生成: {date_str} {theme['emoji']} {theme['name']} 第{week}周 {phase_info['name']}"], check=True)
    subprocess.run(["git", "push", "origin", "main"], check=True)
    print("✅ 已推送到GitHub")


if __name__ == "__main__":
    main()
