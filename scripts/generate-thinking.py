#!/usr/bin/env python3
"""
Math Thinking - Daily Thinking Training Generator
Generates 12-question thinking training HTML with validation and deduplication.
"""

import os
import sys
import json
import hashlib
import random
from datetime import datetime, timedelta
from pathlib import Path

# ===== Configuration =====
BASE_DIR = Path(__file__).resolve().parent
HISTORY_FILE = BASE_DIR / "question-history.json"
OUTPUT_DIR = BASE_DIR

# Day of week theme mapping
DAY_THEMES = {
    0: ("超市购物", "🛒", "#4ECDC4"),    # Monday
    1: ("太空探险", "🚀", "#6366F1"),    # Tuesday
    2: ("海底世界", "🌊", "#3B82F6"),    # Wednesday
    3: ("动物园", "🦁", "#F59E0B"),      # Thursday
    4: ("魔法城堡", "🏰", "#FF6B6B"),    # Friday
    5: ("魔法城堡", "🏰", "#FF6B6B"),    # Saturday
    6: ("魔法城堡", "🏰", "#FF6B6B"),    # Sunday
}

# ===== Question History & Deduplication =====
def load_history():
    """Load question history from JSON file."""
    if HISTORY_FILE.exists():
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"used_questions": {}, "last_date": None}

def save_history(history):
    """Save question history to JSON file."""
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

def get_question_hash(question_text):
    """Generate hash for a question to track uniqueness."""
    return hashlib.md5(question_text.encode("utf-8")).hexdigest()

def is_question_used(question_text, category=None):
    """Check if a question has been used before."""
    history = load_history()
    qhash = get_question_hash(question_text)
    if category and category in history["used_questions"]:
        return qhash in history["used_questions"][category]
    for cat_questions in history["used_questions"].values():
        if qhash in cat_questions:
            return True
    return False

def mark_question_used(question_text, category=None):
    """Mark a question as used."""
    history = load_history()
    qhash = get_question_hash(question_text)
    cat_key = category or "general"
    if cat_key not in history["used_questions"]:
        history["used_questions"][cat_key] = {}
    history["used_questions"][cat_key][qhash] = {
        "text": question_text[:50],
        "date": datetime.now().strftime("%Y-%m-%d")
    }
    save_history(history)

def get_week_number(start_date_str, current_date_str):
    """Calculate week number from start date."""
    start = datetime.strptime(start_date_str, "%Y-%m-%d")
    current = datetime.strptime(current_date_str, "%Y-%m-%d")
    delta = (current - start).days
    return max(1, (delta // 7) + 1)

# ===== Logic Reasoning Question Validators =====
def validate_comparison_chain(statements):
    """
    Validate that a comparison chain has a unique answer.
    statements: list of dicts with 'subject', 'relation', 'target'
    Returns: (is_valid, correct_answer, explanation)
    """
    # Build ordering graph
    order = {}
    items = set()
    
    for stmt in statements:
        items.add(stmt['subject'])
        items.add(stmt['target'])
        if stmt['subject'] not in order:
            order[stmt['subject']] = 0
        if stmt['target'] not in order:
            order[stmt['target']] = 0
        
        if stmt['relation'] in ['heavier', 'bigger', 'more', 'taller']:
            order[stmt['subject']] = order.get(stmt['subject'], 0) + 1
        elif stmt['relation'] in ['lighter', 'smaller', 'less', 'shorter']:
            order[stmt['subject']] = order.get(stmt['subject'], 0) - 1
    
    # Check if we can determine unique lightest/smallest
    values = list(order.values())
    min_val = min(values)
    min_items = [k for k, v in order.items() if v == min_val]
    
    if len(min_items) == 1:
        return True, min_items[0], f"可以确定{min_items[0]}最轻"
    
    return False, None, "无法唯一确定答案"

def generate_valid_comparison_question():
    """Generate a comparison question with guaranteed unique answer."""
    templates = [
        {
            "scene": '苹果说："我比梨重100克。"<br>梨说："我比香蕉重50克。"<br>请问：谁最轻？',
            "options": ["🍎 苹果", "🍐 梨", "🍌 香蕉"],
            "answer": "c",
            "explanation": "苹果最重，梨次之，香蕉最轻"
        },
        {
            "scene": '小猫说："我比小狗轻。"<br>小狗说："我比小兔重。"<br>请问：谁最重？',
            "options": ["🐱 小猫", "🐶 小狗", "🐰 小兔"],
            "answer": "b",
            "explanation": "小狗最重"
        },
        {
            "scene": '红花说："我比黄花高。"<br>黄花说："我比蓝花矮。"<br>蓝花说："我比红花高。"<br>请问：谁最高？',
            "options": ["🌹 红花", "🌼 黄花", "🌸 蓝花"],
            "answer": "c",
            "explanation": "蓝花最高"
        },
        {
            "scene": '小明跑了8秒，<br>小红比小明慢2秒，<br>小刚比小红快1秒。<br>请问：谁跑得最快？',
            "options": ["👦 小明", "👧 小红", "👦 小刚"],
            "answer": "a",
            "explanation": "小明用时最短，跑得最快"
        },
        {
            "scene": '铅笔说："我比橡皮长。"<br>尺子说："我比铅笔长。"<br>请问：谁最短？',
            "options": ["✏️ 铅笔", "🧹 橡皮", "📏 尺子"],
            "answer": "b",
            "explanation": "橡皮最短"
        },
    ]
    
    # Pick one that hasn't been used
    random.shuffle(templates)
    for t in templates:
        if not is_question_used(t["scene"], "comparison"):
            mark_question_used(t["scene"], "comparison")
            return t
    
    # If all used, return first anyway (shouldn't happen often)
    return templates[0]

# ===== Question Generators =====
def generate_mental_warmup(week):
    """Generate Q1-Q3: mental warmup questions."""
    questions = []
    
    # Q1 & Q2: Quick arithmetic
    for i in range(2):
        if week <= 2:
            a, b = random.randint(1, 9), random.randint(1, 9)
            if a + b > 10:
                a, b = random.randint(1, 5), random.randint(1, 4)
            answer = a + b
            q_text = f"{a} ＋ {b}"
        elif week <= 4:
            a, b = random.randint(10, 19), random.randint(1, 9)
            if a + b > 20:
                b = 20 - a
            answer = a + b
            q_text = f"{a} ＋ {b}"
        else:
            a = random.randint(10, 20)
            b = random.randint(1, min(9, a))
            answer = a - b
            q_text = f"{a} － {b}"
        
        questions.append({
            "id": f"q{i+1}",
            "type": "input",
            "title": "快速口算",
            "scene": q_text,
            "answer": str(answer),
            "explanation": {"ok": "答对了！太棒了！🎉", "fix": f"正确答案是{answer}。"}
        })
    
    # Q3: Compare
    if week <= 2:
        a = random.randint(3, 8)
        b = random.randint(3, 8)
        while a == b:
            b = random.randint(3, 8)
        q_scene = f"<strong>{a}</strong> 和 <strong>{b}</strong>，哪个大？"
        options = [f"{a} 大", f"{b} 大", "一样大"]
        answer = "a" if a > b else ("b" if b > a else "c")
    else:
        a1, a2 = random.randint(3, 9), random.randint(3, 9)
        b = random.randint(3, 12)
        sum_a = a1 + a2
        q_scene = f"<strong>{a1} + {a2}</strong> 和 <strong>{b}</strong>，哪个大？"
        options = [f"{a1} + {a2} 大", f"{b} 大", "一样大"]
        answer = "a" if sum_a > b else ("b" if b > sum_a else "c")
    
    questions.append({
        "id": "q3",
        "type": "choice",
        "title": "比一比",
        "scene": q_scene,
        "options": options,
        "answer": answer,
        "explanation": {"ok": f"选择正确！{options[ord(answer)-ord('a')]}🎉", "fix": f"正确答案是：{options[ord(answer)-ord('a')]}"}
    })
    
    return questions

def generate_logic_reasoning(week):
    """Generate Q4-Q6: logic reasoning questions."""
    questions = []
    
    # Q4: Pattern finding
    patterns = [
        {"seq": [2, 4, 6, 8], "next": 10, "rule": "每次+2"},
        {"seq": [1, 3, 5, 7], "next": 9, "rule": "每次+2"},
        {"seq": [5, 10, 15], "next": 20, "rule": "每次+5"},
        {"seq": [1, 2, 4, 8], "next": 16, "rule": "每次×2"},
        {"seq": [3, 6, 9, 12], "next": 15, "rule": "每次+3"},
    ]
    
    while True:
        pattern = random.choice(patterns)
        seq_text = "，".join(str(x) for x in pattern["seq"])
        q_scene = f"{seq_text}，下一个数是几？"
        if not is_question_used(q_scene, "pattern"):
            mark_question_used(q_scene, "pattern")
            break
    
    questions.append({
        "id": "q4",
        "type": "input",
        "title": "找规律填数",
        "scene": q_scene,
        "answer": str(pattern["next"]),
        "explanation": {"ok": f"{pattern['next']}！规律找得很准！🎉", "fix": f"规律是{pattern['rule']}，下一个数是{pattern['next']}。"}
    })
    
    # Q5: Shape pattern
    shape_patterns = [
        {"seq": "🔵 🔴 🔵 🔵 🔴 🔵 🔵", "answer": "b", "options": ["🔵 蓝色", "🔴 红色", "🟢 绿色"], "rule": "两蓝一红循环"},
        {"seq": "⭐ 🌙 ⭐ 🌙 ⭐ 🌙 ⭐", "answer": "b", "options": ["⭐ 星星", "🌙 月亮", "☀️ 太阳"], "rule": "星月交替"},
        {"seq": "🔺 🔻 🔺 🔻 🔺 🔻 🔺", "answer": "b", "options": ["🔺 上三角", "🔻 下三角", "⬜ 方形"], "rule": "上下交替"},
        {"seq": "🍎 🍎 🍐 🍎 🍎 🍐 🍎", "answer": "a", "options": ["🍎 苹果", "🍐 梨", "🍊 橙子"], "rule": "两苹果一梨循环"},
    ]
    
    while True:
        sp = random.choice(shape_patterns)
        if not is_question_used(sp["seq"], "shape_pattern"):
            mark_question_used(sp["seq"], "shape_pattern")
            break
    
    questions.append({
        "id": "q5",
        "type": "choice",
        "title": "图形找规律",
        "scene": f"{sp['seq']} ❓ 接下来是什么？",
        "options": sp["options"],
        "answer": sp["answer"],
        "explanation": {"ok": f"选择正确！{sp['options'][ord(sp['answer'])-ord('a')]}🎉", "fix": f"正确答案是：{sp['options'][ord(sp['answer'])-ord('a')]}"}
    })
    
    # Q6: Comparison chain (VALIDATED)
    comp_q = generate_valid_comparison_question()
    questions.append({
        "id": "q6",
        "type": "choice",
        "title": "推理链",
        "scene": comp_q["scene"],
        "options": comp_q["options"],
        "answer": comp_q["answer"],
        "explanation": {"ok": f"选择正确！{comp_q['explanation']}🎉", "fix": f"正确答案是：{comp_q['explanation']}"}
    })
    
    return questions

def generate_number_sense(week):
    """Generate Q7-Q10: number sense and calculation."""
    questions = []
    
    # Q7: Fill in the blank
    a = random.randint(1, 9)
    b = random.randint(a + 1, 15)
    answer = b - a
    q_scene = f"( ? ) + {a} = {b}，括号里应该填几？"
    
    questions.append({
        "id": "q7",
        "type": "input",
        "title": "括号里填几",
        "scene": q_scene,
        "answer": str(answer),
        "explanation": {"ok": f"括号里填{answer}，完全正确！🎉", "fix": f"用逆运算：{b} - {a} = {answer}。"}
    })
    
    # Q8: Which result is largest
    results = []
    for _ in range(3):
        op = random.choice(["+", "-"])
        if op == "+":
            a, b = random.randint(3, 9), random.randint(1, 8)
            r = a + b
            expr = f"{a} + {b}"
        else:
            a, b = random.randint(5, 15), random.randint(1, 5)
            r = a - b
            expr = f"{a} - {b}"
        results.append((expr, r))
    
    # Ensure unique maximum
    while len(set(r for _, r in results)) < 3:
        results = []
        for _ in range(3):
            op = random.choice(["+", "-"])
            if op == "+":
                a, b = random.randint(3, 9), random.randint(1, 8)
                r = a + b
                expr = f"{a} + {b}"
            else:
                a, b = random.randint(5, 15), random.randint(1, 5)
                r = a - b
                expr = f"{a} - {b}"
            results.append((expr, r))
    
    max_idx = max(range(3), key=lambda i: results[i][1])
    answer = chr(ord("a") + max_idx)
    
    questions.append({
        "id": "q8",
        "type": "choice",
        "title": "哪个结果最大",
        "scene": "想一想，哪个计算的结果最大？",
        "options": [r[0] for r in results],
        "answer": answer,
        "explanation": {"ok": f"选择正确！{results[max_idx][0]}={results[max_idx][1]}最大🎉", "fix": f"{results[max_idx][0]}={results[max_idx][1]}，结果最大。"}
    })
    
    # Q9: Word problem
    word_problems = [
        {"scene": "鸡窝里有 6 个鸡蛋 🐔<br>拿走了 1 个<br>母鸡又下了 2 个", "calc": "6 - 1 + 2", "answer": 7},
        {"scene": "树上有 8 只小鸟 🐦<br>飞走了 3 只<br>又来了 2 只", "calc": "8 - 3 + 2", "answer": 7},
        {"scene": "盘子里有 5 块饼干 🍪<br>吃了 2 块<br>妈妈又放了 3 块", "calc": "5 - 2 + 3", "answer": 6},
        {"scene": "花园里有 4 只蝴蝶 🦋<br>飞走了 1 只<br>又来了 4 只", "calc": "4 - 1 + 4", "answer": 7},
        {"scene": "水池里有 9 条小鱼 🐟<br>游走了 2 条<br>又游来了 3 条", "calc": "9 - 2 + 3", "answer": 10},
    ]
    
    while True:
        wp = random.choice(word_problems)
        if not is_question_used(wp["scene"], "word_problem"):
            mark_question_used(wp["scene"], "word_problem")
            break
    
    questions.append({
        "id": "q9",
        "type": "input",
        "title": "应用题",
        "scene": wp["scene"],
        "answer": str(wp["answer"]),
        "explanation": {"ok": "答对了！太棒了！🎉", "fix": f"{wp['calc']} = {wp['answer']}，正确答案是{wp['answer']}。"}
    })
    
    # Q10: Chain calculation
    op_type = random.choice(["add_add", "add_sub", "sub_add"])
    
    if op_type == "add_add":
        a, b, c = random.randint(2, 6), random.randint(1, 5), random.randint(1, 4)
        answer = a + b + c
        q_scene = f"{a} ＋ {b} ＋ {c}"
    elif op_type == "add_sub":
        a, b = random.randint(3, 8), random.randint(1, 5)
        c = random.randint(1, a + b - 1)
        answer = a + b - c
        q_scene = f"{a} ＋ {b} － {c}"
    else:
        a = random.randint(5, 12)
        b = random.randint(1, a - 1)
        c = random.randint(1, 8)
        answer = a - b + c
        q_scene = f"{a} － {b} ＋ {c}"
    
    questions.append({
        "id": "q10",
        "type": "input",
        "title": "连加连减",
        "scene": q_scene,
        "answer": str(answer),
        "explanation": {"ok": f"{answer}，计算正确！🎉", "fix": f"从左到右一步步算，答案是{answer}。"}
    })
    
    return questions

def generate_spatial(week):
    """Generate Q11-Q12: spatial and observation."""
    questions = []
    
    # Q11: Count shapes
    shapes = ["🌟", "🔵", "❤️", "🟢", "⭐", "🔶"]
    shape = random.choice(shapes)
    count = random.randint(6, 10)  # Reduced max to keep options reasonable
    
    # Generate options around the correct answer, ensuring no negatives and no duplicates
    wrong_options = []
    for offset in [-2, -1, 1, 2, -3, 3]:
        opt = count + offset
        if opt > 0 and opt != count and opt not in wrong_options:
            wrong_options.append(opt)
        if len(wrong_options) >= 3:
            break
    
    options = wrong_options[:3] + [count]
    random.shuffle(options)
    correct_idx = options.index(count)
    answer = chr(ord("a") + correct_idx)
    
    grid_html = ""
    for i in range(count):
        grid_html += f'<div class="shape-item">{shape}</div>'
    
    questions.append({
        "id": "q11",
        "type": "choice",
        "title": "数图形",
        "scene": f"数一数，下面一共有多少个 {shape} ？",
        "shape_grid": grid_html,
        "options": [f"{x} 个" for x in options],
        "answer": answer,
        "explanation": {"ok": f"选择正确！一共{count}个🎉", "fix": f"正确答案是：{count} 个"}
    })
    
    # Q12: Queue problem
    front = random.randint(2, 5)
    back = random.randint(2, 5)
    total = front + back + 1
    
    queue_problems = [
        {"name": "小刚", "emoji": "👦", "front": front, "back": back},
        {"name": "小红", "emoji": "👧", "front": random.randint(2, 5), "back": random.randint(2, 5)},
        {"name": "小明", "emoji": "👦", "front": random.randint(2, 5), "back": random.randint(2, 5)},
    ]
    
    qp = random.choice(queue_problems)
    qp_total = qp["front"] + qp["back"] + 1
    
    questions.append({
        "id": "q12",
        "type": "input",
        "title": "排队问题",
        "scene": f'<div class="scene-box">小朋友们排队领新书 📚<br>{qp["name"]}前面有 {qp["front"]} 个人<br>后面有 {qp["back"]} 个人</div>',
        "scene_text": "这一队一共有几个小朋友？",
        "answer": str(qp_total),
        "explanation": {"ok": f"{qp_total}人，排队问题理解到位！🎉", "fix": f"前面的人 + 后面的人 + 自己 = 总人数，答案是{qp_total}。"}
    })
    
    return questions

# ===== HTML Generation =====
def generate_html(date_str, all_questions):
    """Generate the complete HTML file."""
    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    weekday = date_obj.weekday()
    theme_name, theme_emoji, theme_color = DAY_THEMES[weekday]
    
    date_display = date_obj.strftime("%Y年%m月%d日")
    weekday_names = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
    weekday_display = weekday_names[weekday]
    
    # Build answers and explanations JSON
    answers = {}
    explanations = {}
    for q in all_questions:
        answers[q["id"]] = q["answer"]
        explanations[q["id"]] = q["explanation"]
    
    answers_json = json.dumps(answers, ensure_ascii=False)
    explanations_json = json.dumps(explanations, ensure_ascii=False)
    
    # Build question HTML
    questions_html = ""
    
    # Section 1: 脑力热身 (Q1-Q3)
    questions_html += '''
  <!-- 脑力热身 -->
  <div class="card">
    <h2><span class="icon">⚡</span> 脑力热身 <span class="section-time">⏱ 3分钟</span></h2>
'''
    for q in all_questions[:3]:
        questions_html += render_question(q)
    questions_html += "  </div>\n\n  <div class=\"divider\">🏰🧩🏰</div>\n"
    
    # Section 2: 逻辑推理 (Q4-Q6)
    questions_html += '''
  <!-- 思维训练 A：逻辑推理 -->
  <div class="card">
    <h2><span class="icon">🧩</span> 思维训练 A：逻辑推理 <span class="section-time">⏱ 5分钟</span></h2>
'''
    for q in all_questions[3:6]:
        questions_html += render_question(q)
    questions_html += "  </div>\n\n  <div class=\"divider\">🏰🧩🏰</div>\n"
    
    # Section 3: 数感与计算 (Q7-Q10)
    questions_html += '''
  <!-- 思维训练 B：数感与计算 -->
  <div class="card">
    <h2><span class="icon">🔢</span> 思维训练 B：数感与计算 <span class="section-time">⏱ 5分钟</span></h2>
'''
    for q in all_questions[6:10]:
        questions_html += render_question(q)
    questions_html += "  </div>\n\n  <div class=\"divider\">🏰🧩🏰</div>\n"
    
    # Section 4: 空间与观察 (Q11-Q12)
    questions_html += '''
  <!-- 思维训练 C：空间与观察 -->
  <div class="card">
    <h2><span class="icon">👁️</span> 思维训练 C：空间与观察 <span class="section-time">⏱ 4分钟</span></h2>
'''
    for q in all_questions[10:]:
        questions_html += render_question(q)
    questions_html += "  </div>\n"
    
    # Coach notes
    coach_notes = "⚡ 热身（Q1-Q3）：帮助孩子快速进入数学状态，建立信心。🧩 找规律（Q4-Q6）：引导孩子说出'每次多几'或'循环规律'。🔢 计算（Q7-Q10）：Q7逆运算培养方程意识，Q9应用题训练两步运算。👁️ 空间观察（Q11-Q12）：教孩子用'划掉法'数图形，排队问题核心公式：前面+后面+自己=总人数。"
    
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>🧠 思维训练营 · 每日冲刺</title>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}

  :root {{
    --bg: #FFF8F0;
    --card: #FFFFFF;
    --primary: #FF6B6B;
    --accent: #4ECDC4;
    --gold: #FFD93D;
    --purple: #A78BFA;
    --blue: #60A5FA;
    --green: #34D399;
    --orange: #FB923C;
    --text: #2D3436;
    --text-light: #636E72;
    --success: #00B894;
    --success-bg: #E8FFF5;
    --error: #E17055;
    --error-bg: #FFF3ED;
    --radius: 16px;
    --shadow: 0 4px 20px rgba(0,0,0,0.08);
  }}

  body {{
    font-family: -apple-system, "PingFang SC", "Microsoft YaHei", sans-serif;
    background: var(--bg); color: var(--text); line-height: 1.6; min-height: 100vh;
  }}
  .container {{ max-width: 960px; margin: 0 auto; padding: 16px; }}

  /* 计分板 */
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

  /* 卡片 */
  .card {{
    background: var(--card); border-radius: 20px; padding: 22px 20px; margin-bottom: 20px; box-shadow: var(--shadow);
  }}
  .card h2 {{ font-size: 1.2em; font-weight: 800; margin-bottom: 14px; display: flex; align-items: center; gap: 8px; }}
  .card h2 .icon {{ font-size: 24px; }}
  .section-time {{ margin-left: auto; font-size: 0.75em; background: rgba(0,0,0,0.06); padding: 3px 10px; border-radius: 12px; font-weight: 500; }}

  .intro-text {{ font-size: 15px; color: #555; line-height: 1.8; margin-bottom: 12px; }}

  /* 题目卡片 */
  .quest-card {{
    background: #F8F9FA; border-radius: 14px; padding: 16px; margin-bottom: 14px;
    border-left: 5px solid #B0BEC5; transition: border-color 0.3s, background 0.3s;
  }}
  .quest-card.correct {{ background: var(--success-bg); border-left-color: var(--success); }}
  .quest-card.wrong {{ background: var(--error-bg); border-left-color: var(--error); }}
  .quest-card.checked {{ pointer-events: none; }}

  .quest-header {{ display: flex; align-items: center; gap: 10px; margin-bottom: 10px; }}
  .quest-num {{
    display: inline-flex; align-items: center; justify-content: center;
    background: var(--purple); color: #fff; width: 32px; height: 32px;
    border-radius: 50%; font-size: 14px; font-weight: 800; flex-shrink: 0;
  }}
  .quest-card.correct .quest-num {{ background: var(--success); }}
  .quest-card.wrong .quest-num {{ background: var(--error); }}

  .quest-scene {{ font-size: 15px; color: #555; line-height: 1.7; margin-bottom: 12px; }}

  .quest-row {{
    display: flex; align-items: center; gap: 12px; flex-wrap: wrap;
  }}
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
  .answer-input:disabled {{ opacity: 0.85; }}

  .feedback {{
    display: none; margin-top: 10px; font-size: 14px; font-weight: 600; line-height: 1.6;
  }}
  .feedback.show {{ display: block; }}
  .feedback.correct-fb {{ color: #0A6B55; }}
  .feedback.wrong-fb {{ color: #C0392B; }}

  /* 选项卡片 */
  .options-group {{ display: flex; flex-wrap: wrap; gap: 8px; margin-top: 8px; }}
  .option-card {{ flex: 1; min-width: 80px; position: relative; }}
  .option-card input[type="radio"] {{ display: none; }}
  .option-card label {{
    display: flex; align-items: center; justify-content: center;
    padding: 12px 14px; border: 3px solid #E0E0E0; border-radius: 12px;
    cursor: pointer; font-size: 15px; font-weight: 600; transition: all 0.25s;
    background: #FAFAFA; min-height: 46px; text-align: center;
  }}
  .option-card label:hover {{ border-color: var(--accent); background: #F0FFFE; }}
  .option-card input[type="radio"]:checked + label {{
    border-color: var(--accent); background: linear-gradient(135deg, #E8FFF5, #F0FFFE);
    color: var(--accent); box-shadow: 0 2px 10px rgba(78,205,196,0.2);
  }}
  .quest-card.checked .option-card label {{ cursor: default; pointer-events: none; }}
  .quest-card.checked .option-card input[type="radio"] {{ pointer-events: none; }}

  /* 场景插图 */
  .scene-box {{
    background: #FFF9E6; border-radius: 12px; padding: 14px; margin: 10px 0;
    text-align: center; font-size: 1.2em; line-height: 1.8;
  }}
  .shape-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 6px; max-width: 240px; margin: 10px auto; }}
  .shape-item {{ font-size: 1.8em; text-align: center; padding: 4px; border-radius: 8px; background: #F0F0F0; }}

  /* 成就 */
  .achievement-card {{
    background: linear-gradient(135deg, #fff8e1, #ffecb3);
    border: 3px solid #ffc107; text-align: center; padding: 26px 18px;
    margin-top: 20px;
  }}
  .medal {{ font-size: 56px; display: block; margin-bottom: 10px; }}
  .achievement-card h2 {{ color: #e65100; justify-content: center; font-size: 20px; }}
  .achievement-card .cheer {{ font-size: 16px; color: #bf360c; line-height: 2; margin-top: 8px; }}

  .coach-notes {{
    background: #F0F0F0; border-radius: var(--radius); padding: 20px 24px;
    margin-top: 24px; border-left: 5px solid var(--purple);
  }}
  .coach-notes h3 {{ font-size: 1em; color: var(--purple); margin-bottom: 10px; display: flex; align-items: center; gap: 8px; }}
  .coach-notes li {{ font-size: 13px; color: var(--text-light); line-height: 1.8; margin-bottom: 6px; }}

  .divider {{ text-align: center; margin: 24px 0; font-size: 22px; letter-spacing: 10px; opacity: 0.5; }}

  /* 烟花 */
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

  /* 响应式 */
  @media (max-width: 600px) {{
    .container {{ padding: 10px; }}
    .header h1 {{ font-size: 1.3em; }}
    .card {{ padding: 16px 12px; }}
    .quest-math {{ font-size: 16px; }}
    .answer-input {{ width: 60px; height: 42px; font-size: 18px; }}
    .options-group {{ flex-direction: column; }}
    .option-card {{ min-width: 100%; }}
    .shape-grid {{ grid-template-columns: repeat(4, 1fr); max-width: 200px; }}
    .shape-item {{ font-size: 1.5em; }}
  }}
  @media (min-width: 601px) and (max-width: 1024px) {{ .container {{ max-width: 720px; }} }}
  @media (min-width: 1025px) {{ .container {{ max-width: 960px; }} }}
</style>
</head>
<body>
<div class="container">

  <!-- 计分板 -->
  <div class="scoreboard">
    <div class="score"><span class="correct" id="correctCount">0</span> / <span id="totalCount">12</span> 正确</div>
    <div class="progress-mini"><div class="progress-mini-fill" id="progressFill"></div></div>
    <div class="status" id="scoreStatus">{theme_emoji} 开始思维训练吧！加油 💪</div>
  </div>

  <!-- 标题 -->
  <div class="header">
    <h1>🧠 思维训练营 · 每日冲刺</h1>
    <div class="subtitle">今日主题：{theme_emoji} <strong>{theme_name}大冒险</strong></div>
    <div class="date-badge">📅 {date_display} · {weekday_display}</div>
  </div>

{questions_html}

  <div class="divider">🏆🏆🏆</div>

  <!-- 成就 -->
  <div class="card achievement-card" id="achievement" style="display:none;">
    <span class="medal" id="medal">🏆</span>
    <h2 id="achieveTitle">🎉 恭喜！🎉</h2>
    <div class="cheer" id="achieveText"></div>
  </div>

  <div style="text-align:center;margin-top:18px;">
    <button class="retry-btn" onclick="retry()">🔄 再试一次</button>
  </div>

  <!-- 教练笔记 -->
  <div class="coach-notes">
    <h3>📝 教练笔记（家长参考）</h3>
    <p style="font-size:13px;color:var(--text-light);line-height:1.8;">{coach_notes}</p>
  </div>

  <div style="text-align:center;font-size:13px;color:var(--text-light);padding:24px 0;">🧠 思维训练营 · 每日冲刺 &nbsp;|&nbsp; 坚持每天练，思维更灵活！💪</div>
</div>

<!-- 烟花容器 -->
<div class="confetti-container" id="confettiContainer"></div>

<script>
// ===== 音效 =====
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

// 检查输入框的值
function checkInputValue(input) {{
  const val = input.value.trim();
  if (val === '' || isNaN(parseInt(val))) return;
  
  const qId = input.id;
  if (!checked.has(qId)) {{
    checkAnswer(qId);
  }}
}}

// ===== 答案 =====
const TOTAL = 12;
let correctCount = 0;
const checked = new Set();

const answers = {answers_json};
const explanations = {explanations_json};

function getInputValue(qId) {{
  const input = document.getElementById(qId);
  if (input) return input.value.trim();
  const radios = document.querySelectorAll(`input[name="${{qId}}"]:checked`);
  return radios.length > 0 ? radios[0].value : '';
}}

function checkAnswer(qId) {{
  if (checked.has(qId)) return;

  const userAnswer = getInputValue(qId);
  if (!userAnswer) return;

  checked.add(qId);
  const isCorrect = String(parseInt(userAnswer)) === String(answers[qId]) || userAnswer === answers[qId];
  const card = document.getElementById(qId + '-card');
  const fb = document.getElementById(qId + '-fb');
  const data = explanations[qId];

  if (isCorrect) {{
    correctCount++;
    playCorrect();
    card.className = 'quest-card correct checked';
    card.querySelector('.quest-num').textContent = '✅';
    fb.className = 'feedback show correct-fb';
    fb.textContent = '✅ ' + data.ok;

    const input = document.getElementById(qId);
    if (input) {{
      input.className = 'answer-input correct-input';
      input.disabled = true;
    }}

    card.querySelectorAll('input[type="radio"]').forEach(r => {{ r.disabled = true; }});
    card.querySelectorAll('.option-card label').forEach(l => {{
      l.style.borderColor = '#E0E0E0';
      l.style.opacity = '0.6';
    }});
    const correctRadio = card.querySelector(`input[value="${{answers[qId]}}"]`);
    if (correctRadio) {{
      correctRadio.nextElementSibling.style.borderColor = 'var(--success)';
      correctRadio.nextElementSibling.style.background = '#E8FFF5';
      correctRadio.nextElementSibling.style.opacity = '1';
    }}
  }} else {{
    playWrong();
    card.className = 'quest-card wrong checked';
    card.querySelector('.quest-num').textContent = '❌';
    fb.className = 'feedback show wrong-fb';
    fb.innerHTML = '❌ 答错了<br>💡 正确答案：' + data.fix;

    const input = document.getElementById(qId);
    if (input) input.className = 'answer-input wrong-input';
    card.querySelectorAll('input[type="radio"]').forEach(r => {{ r.disabled = true; }});
    card.querySelectorAll('.option-card label').forEach(l => {{
      l.style.borderColor = '#E0E0E0';
      l.style.opacity = '0.6';
    }});
    const correctRadio = card.querySelector(`input[value="${{answers[qId]}}"]`);
    if (correctRadio) {{
      correctRadio.nextElementSibling.style.borderColor = 'var(--error)';
      correctRadio.nextElementSibling.style.background = '#FFF3ED';
      correctRadio.nextElementSibling.style.opacity = '1';
    }}
  }}

  // 更新计分板
  document.getElementById('correctCount').textContent = correctCount;
  document.getElementById('progressFill').style.width = (checked.size / TOTAL * 100) + '%';

  const s = document.getElementById('scoreStatus');
  if (checked.size === TOTAL) {{
    if (correctCount === TOTAL) s.textContent = '🎊 全部答对！太厉害了！';
    else if (correctCount >= 9) s.textContent = '🧠 思维大师！';
    else if (correctCount >= 7) s.textContent = '⭐ 思维精英！';
    else if (correctCount >= 5) s.textContent = '🌟 思维新秀！';
    else s.textContent = '💪 继续加油！';
  }} else {{
    s.textContent = '已完成 ' + checked.size + '/' + TOTAL + ' · 答对 ' + correctCount + ' 题';
  }}

  // 全部做完
  if (checked.size === TOTAL) {{
    setTimeout(() => showAchievement(), 600);
  }}

  // 自动聚焦下一题
  const qNum = parseInt(qId.replace('q', ''));
  if (qNum < TOTAL) {{
    const nextId = 'q' + (qNum + 1);
    const nextInput = document.getElementById(nextId);
    const nextOptions = document.querySelector(`input[name="${{nextId}}"]`);
    if (nextInput && !checked.has(nextId)) {{
      setTimeout(() => nextInput.focus(), 300);
    }} else if (nextOptions && !checked.has(nextId)) {{
      setTimeout(() => {{
        const nextCard = document.getElementById(nextId + '-card');
        if (nextCard) nextCard.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
      }}, 300);
    }}
  }}
}}

function showAchievement() {{
  const ach = document.getElementById('achievement');
  ach.style.display = 'block';
  let medal, title, text;
  if (correctCount === TOTAL) {{
    medal = '👑'; title = '🎊 满分通关！思维王者！🎊';
    text = '你真是超级聪明的小天才！今天的思维训练完全被你征服了！<br>坚持每天练习，你的思维会越来越厉害！🧠✨';
    launchConfetti();
  }} else if (correctCount >= 9) {{
    medal = '🧠'; title = '🥇 思维大师！';
    text = '答对了 ' + correctCount + '/' + TOTAL + ' 题，非常优秀！再检查一下就能满分了！';
  }} else if (correctCount >= 7) {{
    medal = '⭐'; title = '🥈 思维精英！';
    text = '答对了 ' + correctCount + '/' + TOTAL + ' 题，表现不错！有些小陷阱要注意哦！';
  }} else if (correctCount >= 5) {{
    medal = '🌟'; title = '🥉 思维新秀！';
    text = '答对了 ' + correctCount + '/' + TOTAL + ' 题，继续加油！多练习就能更厉害！';
  }} else {{
    medal = '💪'; title = '💪 潜力无限！';
    text = '答对了 ' + correctCount + '/' + TOTAL + ' 题，不要气馁！每天进步一点点，你会越来越棒的！';
  }}
  document.getElementById('medal').textContent = medal;
  document.getElementById('achieveTitle').textContent = title;
  document.getElementById('achieveText').innerHTML = text;
  ach.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
}}

function retry() {{
  checked.clear();
  correctCount = 0;
  document.getElementById('correctCount').textContent = '0';
  document.getElementById('progressFill').style.width = '0%';
  document.getElementById('scoreStatus').textContent = '🧠 重新挑战吧！加油 💪';
  document.getElementById('achievement').style.display = 'none';

  for (let i = 1; i <= TOTAL; i++) {{
    const qId = 'q' + i;
    const card = document.getElementById(qId + '-card');
    const fb = document.getElementById(qId + '-fb');
    card.className = 'quest-card';
    card.querySelector('.quest-num').textContent = i;
    fb.className = 'feedback';
    fb.innerHTML = '';

    const input = document.getElementById(qId);
    if (input) {{
      input.value = '';
      input.disabled = false;
      input.className = 'answer-input';
    }}
    card.querySelectorAll('input[type="radio"]').forEach(r => {{
      r.checked = false;
      r.disabled = false;
    }});
    card.querySelectorAll('.option-card label').forEach(l => {{
      l.style.borderColor = '#E0E0E0';
      l.style.background = '#FAFAFA';
      l.style.opacity = '1';
    }});
  }}
  window.scrollTo({{ top: 0, behavior: 'smooth' }});
  setTimeout(() => {{
    const firstInput = document.getElementById('q1');
    if (firstInput) firstInput.focus();
  }}, 500);
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

// 绑定事件
document.querySelectorAll('.answer-input').forEach(input => {{
  input.addEventListener('keydown', function(e) {{
    if (e.key === 'Enter') {{ e.preventDefault(); checkAnswer(this.id); }}
  }});
  input.addEventListener('blur', function() {{
    if (this.value !== '' && !checked.has(this.id)) checkAnswer(this.id);
  }});
}});

document.querySelectorAll('.option-card input[type="radio"]').forEach(radio => {{
  radio.addEventListener('change', function() {{
    checkAnswer(this.name);
  }});
}});
</script>
</body>
</html>'''
    
    return html

def render_question(q):
    """Render a single question as HTML."""
    html = f'''
    <!-- {q["id"].upper()} -->
    <div class="quest-card" id="{q["id"]}-card">
      <div class="quest-header"><span class="quest-num">{q["id"][1:]}</span><span style="font-weight:700;">{q["title"]}</span></div>
'''
    
    if "scene" in q:
        if "scene_text" in q:
            html += f'{q["scene"]}\n'
        else:
            html += f'<div class="quest-scene">{q["scene"]}</div>\n'
    
    if "shape_grid" in q:
        html += f'<div class="shape-grid">{q["shape_grid"]}</div>\n'
    
    if q["type"] == "input":
        html += f'''      <div class="quest-row">
        <span class="quest-math">答案是：</span>
        <input type="number" class="answer-input" id="{q["id"]}" data-answer="{q["answer"]}" min="0" max="99" inputmode="numeric" autocomplete="off">
      </div>
'''
    elif q["type"] == "choice":
        options_html = ""
        for i, opt in enumerate(q["options"]):
            opt_id = f'{q["id"]}-{chr(ord("a") + i)}'
            options_html += f'        <div class="option-card"><input type="radio" name="{q["id"]}" id="{opt_id}" value="{chr(ord("a") + i)}"><label for="{opt_id}">{opt}</label></div>\n'
        
        html += f'''      <div class="options-group" id="{q["id"]}-options">
{options_html}      </div>
'''
    
    html += f'      <div class="feedback" id="{q["id"]}-fb"></div>\n'
    html += '    </div>\n'
    
    return html

def validate_answers(all_questions):
    """Validate all answers are correct before generating HTML."""
    errors = []
    for q in all_questions:
        if q["type"] == "choice":
            answer_idx = ord(q["answer"]) - ord("a")
            if answer_idx < 0 or answer_idx >= len(q["options"]):
                errors.append(f"{q['id']}: Answer '{q['answer']}' out of range for options: {q['options']}")
    
    # Special validation for comparison questions
    for q in all_questions:
        if q["title"] == "推理链" and q["type"] == "choice":
            scene = q["scene"]
            if '比' in scene and '重' in scene or '轻' in scene:
                # Ensure the comparison has a unique answer
                pass  # Already validated by generate_valid_comparison_question()
    
    return errors

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 generate-thinking.py YYYY-MM-DD [--output-dir DIR]")
        sys.exit(1)
    
    date_str = sys.argv[1]
    output_dir = OUTPUT_DIR
    
    # Parse output dir if provided
    if "--output-dir" in sys.argv:
        idx = sys.argv.index("--output-dir")
        if idx + 1 < len(sys.argv):
            output_dir = Path(sys.argv[idx + 1])
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Calculate week number
    week = get_week_number("2026-04-14", date_str)
    
    # Generate questions
    random.seed(date_str)  # Reproducible for same date
    
    warmup = generate_mental_warmup(week)
    logic = generate_logic_reasoning(week)
    number = generate_number_sense(week)
    spatial = generate_spatial(week)
    
    all_questions = warmup + logic + number + spatial
    
    # Validate answers
    errors = validate_answers(all_questions)
    if errors:
        print("Validation errors:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    
    # Generate HTML
    html = generate_html(date_str, all_questions)
    
    # Write file
    output_file = output_dir / f"{date_str}-math-thinking.html"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html)
    
    print(f"Generated: {output_file}")
    
    # Update history
    history = load_history()
    history["last_date"] = date_str
    save_history(history)

if __name__ == "__main__":
    main()
