#!/usr/bin/env python3
"""
Math Magic - Daily Math Practice HTML Generator

Generates standalone HTML math practice pages for a 5-year-old,
following the curriculum plan at math-magic/curriculum-plan.html.

Usage:
    python3 generate.py [date] [--output-dir DIR]

If no date is given, uses today's date.
"""

import sys
import os
import random
import hashlib
from datetime import date

# ============ Configuration ============

START_DATE = date(2026, 4, 14)  # Week 1 Day 1 (Tuesday)

# Theme definitions
THEMES = {
    0: {  # Monday - 超市购物
        'name': '超市购物', 'emoji': '🛒',
        'body_gradient': 'linear-gradient(180deg, #1a5c2e 0%, #2d8a4e 20%, #4caf50 40%, #81c784 60%, #a5d6a7 80%, #c8e6c9 100%)',
        'header_gradient': 'linear-gradient(135deg, #2e7d32, #4caf50)',
        'header_shadow': 'rgba(0,100,0,0.35)',
        'quest_bg': 'linear-gradient(135deg, #e8f5e9, #c8e6c9)', 'quest_border': '#4caf50',
        'quest_num_bg': '#4caf50', 'quest_math_color': '#1b5e20',
        'input_border': '#a5d6a7', 'input_focus': '#4caf50',
        'tip_bg': '#e8f5e9', 'tip_border': '#66bb6a', 'tip_color': '#2e7d32',
        'submit_gradient': 'linear-gradient(135deg, #2e7d32, #4caf50)', 'submit_shadow': 'rgba(46,125,50,0.4)',
        'footer_text': '数学魔法师 · 超市购物篇',
        'character': '小兔子', 'character_emoji': '🐰', 'treasure': '胡萝卜金币', 'treasure_emoji': '🥕',
        'divider_emojis': '🛒🧺🥕🍎🛍️',
    },
    1: {  # Tuesday - 太空探险
        'name': '太空探险', 'emoji': '🚀',
        'body_gradient': 'linear-gradient(180deg, #0a1a3a 0%, #1a237e 20%, #283593 40%, #3f51b5 60%, #7986cb 80%, #9fa8da 100%)',
        'header_gradient': 'linear-gradient(135deg, #1a237e, #3f51b5)',
        'header_shadow': 'rgba(0,0,80,0.35)',
        'quest_bg': 'linear-gradient(135deg, #e8eaf6, #c5cae9)', 'quest_border': '#3f51b5',
        'quest_num_bg': '#3f51b5', 'quest_math_color': '#0d1b6e',
        'input_border': '#9fa8da', 'input_focus': '#3f51b5',
        'tip_bg': '#e8eaf6', 'tip_border': '#5c6bc0', 'tip_color': '#1a237e',
        'submit_gradient': 'linear-gradient(135deg, #1a237e, #3f51b5)', 'submit_shadow': 'rgba(26,35,126,0.4)',
        'footer_text': '数学魔法师 · 太空探险篇',
        'character': '小宇航员', 'character_emoji': '👨‍🚀', 'treasure': '星际能源宝石', 'treasure_emoji': '💎',
        'divider_emojis': '🚀⭐🌙🛸🪐',
    },
    2: {  # Wednesday - 海底世界
        'name': '海底世界', 'emoji': '🌊',
        'body_gradient': 'linear-gradient(180deg, #0a4c7a 0%, #0d6ebd 20%, #1a8fc4 40%, #2db5d4 60%, #52d1e0 80%, #8ae0ee 100%)',
        'header_gradient': 'linear-gradient(135deg, #0077b6, #00b4d8)',
        'header_shadow': 'rgba(0,100,180,0.35)',
        'quest_bg': 'linear-gradient(135deg, #e3f2fd, #bbdefb)', 'quest_border': '#1976d2',
        'quest_num_bg': '#1976d2', 'quest_math_color': '#0d47a1',
        'input_border': '#90caf9', 'input_focus': '#1976d2',
        'tip_bg': '#e3f2fd', 'tip_border': '#42a5f5', 'tip_color': '#1565c0',
        'submit_gradient': 'linear-gradient(135deg, #ff6f00, #ff8f00)', 'submit_shadow': 'rgba(255,111,0,0.4)',
        'footer_text': '数学魔法师 · 海底寻宝篇',
        'character': '小螃蟹卡卡', 'character_emoji': '🦀', 'treasure': '珍珠', 'treasure_emoji': '💎',
        'divider_emojis': '🐠🐡🐙🦀🐚',
    },
    3: {  # Thursday - 动物园
        'name': '动物园', 'emoji': '🦁',
        'body_gradient': 'linear-gradient(180deg, #5c3a1a 0%, #8a5a2d 20%, #bf7a3a 40%, #d4a052 60%, #e0c08a 80%, #eedcb5 100%)',
        'header_gradient': 'linear-gradient(135deg, #8a5a2d, #bf7a3a)',
        'header_shadow': 'rgba(80,50,0,0.35)',
        'quest_bg': 'linear-gradient(135deg, #fff8e1, #ffecb3)', 'quest_border': '#f9a825',
        'quest_num_bg': '#f9a825', 'quest_math_color': '#5c3a1a',
        'input_border': '#ffe082', 'input_focus': '#f9a825',
        'tip_bg': '#fff8e1', 'tip_border': '#fdd835', 'tip_color': '#5c3a1a',
        'submit_gradient': 'linear-gradient(135deg, #8a5a2d, #bf7a3a)', 'submit_shadow': 'rgba(138,90,45,0.4)',
        'footer_text': '数学魔法师 · 动物园篇',
        'character': '小狮子', 'character_emoji': '🦁', 'treasure': '动物王冠', 'treasure_emoji': '👑',
        'divider_emojis': '🦁🐘🐒🦒🐼',
    },
    4: {  # Friday - 魔法城堡
        'name': '魔法城堡', 'emoji': '🏰',
        'body_gradient': 'linear-gradient(180deg, #2d1b69 0%, #5b2c8e 20%, #7c3aed 40%, #a78bfa 60%, #c4b5fd 80%, #ddd6fe 100%)',
        'header_gradient': 'linear-gradient(135deg, #7c3aed, #a78bfa)',
        'header_shadow': 'rgba(124,58,237,0.35)',
        'quest_bg': 'linear-gradient(135deg, #ede9fe, #ddd6fe)', 'quest_border': '#7c3aed',
        'quest_num_bg': '#7c3aed', 'quest_math_color': '#4a148c',
        'input_border': '#c4b5fd', 'input_focus': '#7c3aed',
        'tip_bg': '#ede9fe', 'tip_border': '#8b5cf6', 'tip_color': '#5b21b6',
        'submit_gradient': 'linear-gradient(135deg, #7c3aed, #a78bfa)', 'submit_shadow': 'rgba(124,58,237,0.4)',
        'footer_text': '数学魔法师 · 魔法城堡篇',
        'character': '小魔法师米娅', 'character_emoji': '🧙', 'treasure': '魔法书', 'treasure_emoji': '📖',
        'divider_emojis': '🏰🔮🗝️👑🧙',
    },
}

WEEKDAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
WEEKDAY_ZH = ['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日']

# ============ Curriculum Difficulty Mapping ============

def get_week_number(target_date):
    delta = (target_date - START_DATE).days
    if delta < 0:
        return 1
    return (delta // 7) + 1

def get_difficulty_for_week(week):
    if week <= 2:
        return 'within_10'
    elif week <= 4:
        return 'teens_add_no_carry'
    elif week <= 6:
        return 'teens_sub_no_borrow'
    elif week <= 8:
        return 'carry_add'
    elif week <= 10:
        return 'borrow_sub'
    elif week <= 12:
        return 'mixed'
    else:
        return 'within_100'

def make_q(a, b, op):
    answer = a + b if op == '+' else a - b
    return {'a': a, 'b': b, 'op': op, 'answer': answer}

def generate_questions_within_10(count=11):
    """Generate 9 regular + 2 for Q10's two locks = 11 questions total."""
    questions = []
    for i in range(9):
        if random.random() < 0.55:  # addition
            a = random.randint(1, 8)
            b = random.randint(1, 10 - a)
            questions.append(make_q(a, b, '+'))
        else:
            a = random.randint(2, 10)
            b = random.randint(1, a - 1)
            questions.append(make_q(a, b, '-'))
    # Q10 lock 1: subtraction from 10
    b = random.randint(2, 8)
    questions.append(make_q(10, b, '-'))
    # Q10 lock 2: making 10
    a = random.randint(1, 9)
    questions.append(make_q(a, 10 - a, '+'))
    return questions

def generate_questions_teens_add_no_carry(count=11):
    questions = []
    for i in range(9):
        a = random.randint(11, 18)
        ones = a % 10
        b = random.randint(1, 9 - ones)
        questions.append(make_q(a, b, '+'))
    # Q10 locks
    a = random.randint(10, 16)
    b = random.randint(1, 9)
    if a % 10 + b <= 9:
        questions.append(make_q(a, b, '+'))
    else:
        questions.append(make_q(a, b, '-'))
    a = random.randint(11, 18)
    ones = a % 10
    b = random.randint(1, 9 - ones)
    questions.append(make_q(a, b, '+'))
    return questions

def generate_questions_teens_sub_no_borrow(count=11):
    questions = []
    for i in range(9):
        a = random.randint(12, 19)
        ones = a % 10
        b = random.randint(1, ones)
        questions.append(make_q(a, b, '-'))
    a = random.randint(12, 19)
    ones = a % 10
    b = random.randint(1, ones)
    questions.append(make_q(a, b, '-'))
    a = random.randint(11, 18)
    b = random.randint(1, 5)
    if a - b >= 10:
        questions.append(make_q(a, b, '-'))
    else:
        questions.append(make_q(a, b, '+'))
    return questions

def generate_questions_carry_add(count=11):
    questions = []
    for i in range(9):
        a = random.randint(6, 9)
        b = random.randint(10 - a, 9)
        questions.append(make_q(a, b, '+'))
    a = random.randint(8, 9)
    b = random.randint(10 - a, 9)
    questions.append(make_q(a, b, '+'))
    a = random.randint(7, 9)
    b = random.randint(10 - a, 9)
    questions.append(make_q(a, b, '+'))
    return questions

def generate_questions_borrow_sub(count=11):
    questions = []
    for i in range(9):
        a = random.randint(12, 18)
        ones = a % 10
        b = random.randint(ones + 1, 9)
        questions.append(make_q(a, b, '-'))
    a = random.randint(11, 15)
    ones = a % 10
    b = random.randint(ones + 1, 9)
    questions.append(make_q(a, b, '-'))
    a = random.randint(12, 17)
    ones = a % 10
    b = random.randint(ones + 1, 9)
    questions.append(make_q(a, b, '-'))
    return questions

def generate_questions_mixed(count=11):
    questions = []
    generators = [generate_questions_carry_add, generate_questions_borrow_sub]
    for i in range(11):
        gen = random.choice(generators)
        qs = gen(1)
        questions.extend(qs)
    return questions

# ============ Scene Generation ============

# ============ Scene Generation ============
# Each item type has its own compatible scenarios with proper classifiers and verbs

ITEM_SCENES = {
    # Space items that fly/exist in space
    'space_fly': {
        'items': ['火箭模型', '小行星', '卫星', '太空探测器', '彗星'],
        'classifier': '枚', 'measure_fly': '枚',
        'add': [
            "太空中有 {a} {cls}{item}，又发现了 {b} {cls}，现在一共有多少{cls}？",
            "飞船雷达探测到 {a} {cls}{item}，又发现了 {b} {cls}，一共探测到多少{cls}？",
            "空间站附近有 {a} {cls}{item}，又飞来 {b} {cls}，现在有几{cls}？",
        ],
        'sub': [
            "太空中有 {a} {cls}{item}，飞走了 {b} {cls}，还剩几{cls}？",
            "空间站附近有 {a} {cls}{item}，离开轨道 {b} {cls}，还剩几{cls}？",
            "飞船探测到 {a} {cls}{item}，有 {b} {cls}偏离轨道，还剩几{cls}？",
        ],
    },
    # Space items that are collected/stored
    'space_collect': {
        'items': ['太空种子', '太空水母', '星星虫', '银河鱼', '太空珊瑚', '月亮石', '银河蟹', '太空花', '星球花', '太空种子', '彗星草', '月光石', '太空晶体'],
        'classifier_map': {
            '太空种子': '颗', '星星虫': '只', '太空水母': '只', '银河鱼': '条',
            '太空珊瑚': '朵', '月亮石': '块', '银河蟹': '只', '太空花': '朵',
            '星球花': '朵', '彗星草': '株', '月光石': '块', '太空晶体': '块',
        },
        'verb_map': {
            '太空种子': ('种', '收获'), '星星虫': ('养', '送走'), '太空水母': ('养', '放生'),
            '银河鱼': ('养', '放生'), '太空珊瑚': ('种', '采摘'), '月亮石': ('收集', '使用'),
            '银河蟹': ('养', '放生'), '太空花': ('种', '采摘'), '星球花': ('种', '采摘'),
            '彗星草': ('种', '收割'), '月光石': ('收集', '使用'), '太空晶体': ('收集', '使用'),
        },
        'add': [
            "月球基地有 {a} {cls}{item}，地球又送来 {b} {cls}，现在有几{cls}？",
            "太空温室里种了 {a} {cls}{item}，又种了 {b} {cls}，现在有几{cls}？",
            "宇航员收集了 {a} {cls}{item}，又找到 {b} {cls}，一共几{cls}？",
            "空间站里有 {a} {cls}{item}，又运来 {b} {cls}，现在有几{cls}？",
        ],
        'sub': [
            "月球基地有 {a} {cls}{item}，用了 {b} {cls}做实验，还剩几{cls}？",
            "太空温室里有 {a} {cls}{item}，送给外星人 {b} {cls}，还剩几{cls}？",
            "宇航员有 {a} {cls}{item}，送给外星朋友 {b} {cls}，还剩几{cls}？",
            "空间站里有 {a} {cls}{item}，消耗了 {b} {cls}，还剩几{cls}？",
        ],
    },
    # Space station items (equipment, supplies)
    'space_supply': {
        'items': ['能量模块', '太阳能板', '轨道标记', '太空天线', '星际种子', '导航芯片',
                  '太空电池', '轨道燃料', '宇航芯片', '太空胶囊', '生命维持器', '太空种子罐', '通讯器',
                  '行星矿石', '太空合金', '星际能量石', '宇宙射线收集器', '暗物质样本', '恒星碎片', '星云粉尘',
                  '太空燃料棒', '轨道修正器', '宇航氧气瓶', '星际导航仪', '太空通讯器', '行星探测器', '太阳能芯片', '太空防护罩'],
        'classifier': '个',
        'add': [
            "空间站里有 {a} {cls}{item}，地球又送来 {b} {cls}，现在有几个？",
            "火箭上装了 {a} {cls}{item}，又装了 {b} {cls}，现在有几个？",
            "宇航员有 {a} {cls}{item}，又找到 {b} {cls}，一共有几个？",
            "太空仓库里有 {a} {cls}{item}，又补货 {b} {cls}，现在有几个？",
        ],
        'sub': [
            "空间站里有 {a} {cls}{item}，用了 {b} {cls}做实验，还剩几个？",
            "火箭上有 {a} {cls}{item}，发射消耗了 {b} {cls}，还剩几个？",
            "宇航员有 {a} {cls}{item}，送给外星人 {b} {cls}，还剩几个？",
            "太空仓库有 {a} {cls}{item}，运走了 {b} {cls}，还剩几个？",
        ],
    },
}

STORE_NAMES = [
    '火箭发射台', '空间站控制室', '月球基地', '火星探测站', '太空实验室',
    '星际导航塔', '太阳能电站', '外星生物馆', '银河观测站', '彗星研究中心',
    '轨道维修站', '行星探索舱', '太空植物园', '宇航训练中心', '星际通讯站',
    '深空探测站', '卫星发射场', '太空博物馆', '航天指挥所', '星际补给站',
]

# ============ HTML Generation ============

def format_date_zh(d):
    return f"{d.year}年{d.month}月{d.day}日 · {WEEKDAY_ZH[d.weekday()]}"

def generate_warmup(theme):
    return f'''  <!-- 热身 -->
  <div class="card warmup-card">
    <h2><span class="icon">🔥</span> 热身小游戏：{theme['name']}热身操</h2>
    <div class="intro-text">👋 小宝贝，准备好了吗？我们一起活动活动身体！</div>
    <div class="warmup-step">
      <div class="step-title">🫧 倒数热身</div>
      <div class="step-content">从 <b>20</b> 倒数到 <b>1</b>，每数一个数就拍一下手 👏</div>
    </div>
    <div class="warmup-step">
      <div class="step-title">{theme['emoji']} 数字游戏</div>
      <div class="step-content">家长说数字，孩子用手比出来："{theme['emoji']}说——<b>{random.randint(11, 18)}</b>！"</div>
    </div>
  </div>'''

def _get_item_scene(q, idx, theme, difficulty, is_lock=False):
    """Generate a semantically correct scene for a question."""
    if is_lock:
        return None
    
    # Pick item category based on difficulty
    items_pool = {
        'within_10': 'space_collect',
        'teens_add_no_carry': 'space_supply',
        'teens_sub_no_borrow': 'space_supply',
        'carry_add': 'space_supply',
        'borrow_sub': 'space_supply',
        'mixed': 'space_supply',
    }
    category = items_pool.get(difficulty, 'space_collect')
    scene_set = ITEM_SCENES[category]
    
    # Pick an item
    item = random.choice(scene_set['items'])
    
    # Get classifier
    if 'classifier_map' in scene_set:
        cls = scene_set['classifier_map'].get(item, '个')
    else:
        cls = scene_set['classifier']
    
    # Pick add or sub template
    if q['op'] == '+':
        templates = scene_set['add']
    else:
        templates = scene_set['sub']
    
    template = random.choice(templates)
    scene = template.format(a=q['a'], b=q['b'], cls=cls, item=item)
    return scene

def generate_question_html(q, idx, theme, difficulty, is_lock=False, lock_label=''):
    """Generate HTML for a single question card."""
    num = idx + 1

    op_display = '＋' if q['op'] == '+' else '－'

    if is_lock:
        return f'''      <div class="quest-row">
        <span class="quest-math">🔒 {q['a']} {op_display} {q['b']} ＝</span>
        <input type="number" class="answer-input" id="q10{lock_label}" data-answer="{q['answer']}" min="0" max="99" inputmode="numeric" autocomplete="off" oninput="checkSingle(this)" onblur="checkSingle(this)">
      </div>'''
    else:
        chinese_num = "一二三四五六七八九"[idx]
        store = random.choice(STORE_NAMES)
        scene = _get_item_scene(q, idx, theme, difficulty)
        return f'''    <!-- Q{num} -->
    <div class="quest-card" id="q{num}-card">
      <div class="quest-header"><span class="quest-num">{num}</span><span style="font-weight:700;">🚪 第{chinese_num}道门——{store}</span></div>
      <div class="quest-scene">{scene}</div>
      <div class="quest-row">
        <span class="quest-math">{q['a']} {op_display} {q['b']} ＝</span>
        <input type="number" class="answer-input" id="q{num}" data-answer="{q['answer']}" min="0" max="99" inputmode="numeric" autocomplete="off" oninput="checkSingle(this)" onblur="checkSingle(this)">
      </div>
      <div class="feedback" id="q{num}-fb"></div>
    </div>'''

def generate_full_html(date_obj, theme, difficulty, questions):
    """Generate the complete HTML file."""
    date_str = format_date_zh(date_obj)
    date_iso = date_obj.isoformat()
    filename = f"{date_iso}-math-magic.html"

    total_q = 11  # 10 questions, Q10 has 2 inputs = 11 total answer fields

    # Build questions list for JS
    q_entries = []
    for i in range(9):
        q_entries.append(f"    {{ id: 'q{i+1}', card: 'q{i+1}-card', fb: 'q{i+1}-fb' }},")
    q_entries.append(f"    {{ id: 'q10a', card: 'q10-card', fb: 'q10-fb', label: '第一把锁' }},")
    q_entries.append(f"    {{ id: 'q10b', card: 'q10-card', fb: 'q10-fb', label: '第二把锁' }},")
    questions_js = '\n'.join(q_entries)

    warmup = generate_warmup(theme)

    # Question cards - 9 regular + Q10 with 2 locks
    question_parts = []

    # Q1-Q9
    for i in range(9):
        card_html = generate_question_html(questions[i], i, theme, difficulty)
        question_parts.append(card_html)

    # Q10 with two locks
    q10_lock1 = questions[9]
    q10_lock2 = questions[10]
    op1 = '＋' if q10_lock1['op'] == '+' else '－'
    op2 = '＋' if q10_lock2['op'] == '+' else '－'

    q10_html = f'''    <!-- Q10 -->
    <div class="quest-card" id="q10-card">
      <div class="quest-header"><span class="quest-num">10</span><span style="font-weight:700;">🚪 最后一道门——宝藏大门 🏆</span></div>
      <div class="quest-scene">大门上有两把锁，都要解开！</div>
      <div class="quest-row">
        <span class="quest-math">🔒 第一把锁：{q10_lock1['a']} {op1} {q10_lock1['b']} ＝</span>
        <input type="number" class="answer-input" id="q10a" data-answer="{q10_lock1['answer']}" min="0" max="99" inputmode="numeric" autocomplete="off" oninput="checkSingle(this)" onblur="checkSingle(this)">
      </div>
      <div class="quest-row" style="margin-top:8px;">
        <span class="quest-math">🔒 第二把锁：{q10_lock2['a']} {op2} {q10_lock2['b']} ＝</span>
        <input type="number" class="answer-input" id="q10b" data-answer="{q10_lock2['answer']}" min="0" max="99" inputmode="numeric" autocomplete="off" oninput="checkSingle(this)" onblur="checkSingle(this)">
      </div>
      <div class="feedback" id="q10-fb"></div>
    </div>'''
    question_parts.append(q10_html)

    questions_html = '\n\n'.join(question_parts)

    # Achievement text
    char = theme['character']
    char_emoji = theme['character_emoji']
    treasure = theme['treasure']
    treasure_emoji = theme['treasure_emoji']

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{theme['emoji']} {theme['name']}大冒险 — 数学魔法任务</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;700;900&display=swap');

  * {{ margin: 0; padding: 0; box-sizing: border-box; }}

  body {{
    font-family: 'Noto Sans SC', 'PingFang SC', 'Microsoft YaHei', sans-serif;
    background: {theme['body_gradient']};
    min-height: 100vh;
    padding: 24px 24px 60px;
    color: #1a3a5c;
  }}

  .container {{ max-width: 960px; margin: 0 auto; }}

  /* 顶部计分板 */
  .scoreboard {{
    position: sticky; top: 12px; z-index: 100;
    background: rgba(255,255,255,0.95);
    backdrop-filter: blur(12px);
    border-radius: 16px;
    padding: 14px 22px;
    margin-bottom: 20px;
    box-shadow: 0 4px 20px rgba(0,60,120,0.2);
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 10px;
  }}
  .scoreboard .score {{
    font-size: 20px;
    font-weight: 900;
    color: #0d47a1;
  }}
  .scoreboard .score .correct {{ color: #2e7d32; }}
  .scoreboard .score .wrong {{ color: #c62828; }}
  .scoreboard .status {{ font-size: 14px; color: #555; }}

  .header {{
    text-align: center;
    background: {theme['header_gradient']};
    border-radius: 24px;
    padding: 28px 18px 22px;
    margin-bottom: 20px;
    box-shadow: 0 8px 30px {theme['header_shadow']};
  }}
  .header h1 {{ font-size: 28px; font-weight: 900; color: #fff; text-shadow: 2px 2px 6px rgba(0,0,0,0.2); margin-top: 20px; }}
  .header .subtitle {{ font-size: 15px; color: #ede9fe; margin-top: 8px; line-height: 1.6; }}
  .header .date-badge {{ display: inline-block; background: rgba(255,255,255,0.25); border-radius: 20px; padding: 4px 16px; font-size: 13px; color: #fff; margin-top: 10px; }}

  .card {{
    background: rgba(255,255,255,0.95);
    border-radius: 20px;
    padding: 22px 20px;
    margin-bottom: 20px;
    box-shadow: 0 4px 18px rgba(0,60,120,0.15);
  }}
  .card h2 {{ font-size: 20px; font-weight: 900; margin-bottom: 14px; display: flex; align-items: center; gap: 8px; }}
  .card h2 .icon {{ font-size: 26px; }}

  .warmup-card {{ background: linear-gradient(135deg, #fff9e6, #fff3cc); border: 3px solid #ffc107; }}
  .warmup-card h2 {{ color: #e65100; }}
  .warmup-step {{ background: rgba(255,255,255,0.8); border-radius: 14px; padding: 14px; margin-bottom: 12px; border-left: 4px solid #ff9800; }}
  .warmup-step .step-title {{ font-size: 16px; font-weight: 700; color: #e65100; margin-bottom: 6px; }}
  .warmup-step .step-content {{ font-size: 15px; color: #4a3520; line-height: 1.8; }}

  /* 题目卡片 */
  .quest-card {{
    background: {theme['quest_bg']};
    border-radius: 18px;
    padding: 18px 16px;
    margin-bottom: 16px;
    border-left: 5px solid {theme['quest_border']};
    transition: border-color 0.3s, background 0.3s;
  }}
  .quest-card.correct {{ background: linear-gradient(135deg, #e8f5e9, #c8e6c9); border-left-color: #43a047; }}
  .quest-card.wrong {{ background: linear-gradient(135deg, #fff3e0, #ffe0b2); border-left-color: #f57c00; }}

  .quest-header {{ display: flex; align-items: center; gap: 10px; margin-bottom: 10px; }}
  .quest-num {{
    display: inline-flex; align-items: center; justify-content: center;
    background: {theme['quest_num_bg']}; color: #fff; width: 36px; height: 36px;
    border-radius: 50%; font-size: 16px; font-weight: 900; flex-shrink: 0;
  }}
  .quest-card.correct .quest-num {{ background: #43a047; }}
  .quest-card.wrong .quest-num {{ background: #f57c00; }}

  .quest-scene {{ font-size: 15px; color: #555; line-height: 1.7; margin-bottom: 12px; padding-left: 46px; }}

  .quest-row {{
    display: flex; align-items: center; gap: 12px; padding-left: 46px; flex-wrap: wrap;
  }}
  .quest-math {{ font-size: 24px; font-weight: 900; color: {theme['quest_math_color']}; letter-spacing: 3px; }}
  .quest-card.correct .quest-math {{ color: #1b5e20; }}
  .quest-card.wrong .quest-math {{ color: #e65100; }}

  .answer-input {{
    width: 80px; height: 48px;
    border: 3px solid {theme['input_border']}; border-radius: 12px;
    font-size: 22px; font-weight: 700; text-align: center;
    color: {theme['quest_math_color']}; background: rgba(255,255,255,0.8);
    outline: none; transition: border-color 0.3s, background 0.3s;
    -webkit-appearance: none; appearance: none;
  }}
  .answer-input:focus {{ border-color: {theme['input_focus']}; background: #fff; }}
  .answer-input.correct-input {{ border-color: #43a047; background: #e8f5e9; color: #2e7d32; }}
  .answer-input.wrong-input {{ border-color: #f57c00; background: #fff3e0; color: #e65100; }}

  .feedback {{
    display: none; margin-top: 10px; padding-left: 46px;
    font-size: 15px; font-weight: 600; line-height: 1.6;
  }}
  .feedback.show {{ display: block; }}
  .feedback.correct-fb {{ color: #2e7d32; }}
  .feedback.wrong-fb {{ color: #e65100; }}

  /* 提交按钮 */
  .submit-area {{ text-align: center; margin: 32px 0; }}
  .submit-btn {{
    display: inline-flex; align-items: center; gap: 10px;
    background: {theme['submit_gradient']};
    color: #fff; border: none; border-radius: 20px;
    padding: 16px 48px; font-size: 22px; font-weight: 900;
    cursor: pointer; box-shadow: 0 6px 20px {theme['submit_shadow']};
    transition: transform 0.2s, box-shadow 0.2s;
    min-width: 200px; justify-content: center;
  }}
  .submit-btn:hover {{ transform: scale(1.05); box-shadow: 0 8px 30px {theme['submit_shadow']}; }}
  .submit-btn:active {{ transform: scale(0.97); }}

  .retry-btn {{
    display: none; margin-top: 14px;
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    color: #fff; border: none; border-radius: 16px;
    padding: 12px 36px; font-size: 18px; font-weight: 700;
    cursor: pointer; box-shadow: 0 4px 15px rgba(99,102,241,0.3);
    transition: transform 0.2s;
  }}
  .retry-btn:hover {{ transform: scale(1.05); }}

  /* 成就 */
  .achievement-card {{
    background: linear-gradient(135deg, #fff8e1, #ffecb3);
    border: 3px solid #ffc107; text-align: center; padding: 26px 18px;
  }}
  .medal {{ font-size: 64px; display: block; margin-bottom: 10px; animation: bounce 2s infinite; }}
  @keyframes bounce {{ 0%,100%{{transform:translateY(0)}} 50%{{transform:translateY(-10px)}} }}
  .achievement-card h2 {{ color: #e65100; justify-content: center; font-size: 22px; }}
  .achievement-card .cheer {{ font-size: 17px; color: #bf360c; line-height: 2; margin-top: 10px; }}
  .stars-row {{ font-size: 32px; letter-spacing: 8px; margin-top: 12px; }}

  .tip {{ background: {theme['tip_bg']}; border-radius: 14px; padding: 12px 14px; margin-top: 12px; font-size: 14px; color: {theme['tip_color']}; line-height: 1.7; border-left: 4px solid {theme['tip_border']}; }}
  .intro-text {{ font-size: 16px; color: #333; line-height: 2; margin-bottom: 10px; }}
  .divider {{ text-align: center; margin: 24px 0; font-size: 24px; letter-spacing: 12px; opacity: 0.6; }}

  /* 庆祝动画 */
  .confetti-container {{ position: fixed; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; z-index: 9999; overflow: hidden; }}
  .confetti {{
    position: absolute; width: 10px; height: 10px;
    top: -10px; opacity: 0;
    animation: confetti-fall 3s ease-out forwards;
  }}
  @keyframes confetti-fall {{
    0% {{ opacity: 1; transform: translateY(0) rotate(0deg); }}
    100% {{ opacity: 0; transform: translateY(100vh) rotate(720deg); }}
  }}

  /* 响应式 */
  @media (max-width: 600px) {{
    body {{ padding: 12px 8px 40px; }}
    .container {{ max-width: 100%; }}
    .header {{ padding: 22px 14px 16px; }}
    .header h1 {{ font-size: 22px; }}
    .card {{ padding: 16px 12px; }}
    .quest-row {{ padding-left: 0; }}
    .quest-scene {{ padding-left: 0; }}
    .feedback {{ padding-left: 0; }}
    .quest-math {{ font-size: 20px; }}
    .answer-input {{ width: 70px; height: 44px; font-size: 20px; }}
    .submit-btn {{ padding: 14px 36px; font-size: 18px; }}
  }}
  @media (min-width: 601px) and (max-width: 1024px) {{ .container {{ max-width: 760px; }} }}
  @media (min-width: 1025px) {{ .container {{ max-width: 860px; }} }}
</style>
</head>
<body>
<div class="container">

  <!-- 计分板 -->
  <div class="scoreboard" id="scoreboard">
    <div class="score">
      <span class="correct" id="correctCount">0</span> / <span id="totalCount">{total_q}</span> 正确
    </div>
    <div class="status" id="scoreStatus">{theme['emoji']} 开始{theme['name']}大冒险吧！加油 💪</div>
  </div>

  <!-- 标题 -->
  <div class="header">
    <h1>{theme['emoji']} {theme['name']}大冒险 {theme['emoji']}</h1>
    <div class="subtitle">帮{theme['character']}找到{theme['treasure']}！每道数学题都是一把钥匙 🔑<br>填完每道题会自动检查，也可以点提交按钮统一检查！</div>
    <div class="date-badge">📅 {date_str}</div>
  </div>

{warmup}

  <div class="divider">{theme['divider_emojis']}</div>

  <!-- 核心任务 -->
  <div class="card">
    <h2><span class="icon">⭐</span> 核心任务：帮{theme['character']}找{theme['treasure']}钥匙</h2>
    <div class="intro-text">{theme['character_emoji']} <b>{theme['character']}</b>听说藏着一本{theme['treasure']} {theme['treasure_emoji']}<br>通往宝藏的路上有 <b>10 道门</b>，在输入框里写上答案，答对就能打开宝藏！</div>

{questions_html}

    <div class="tip">💡 <b>提示：</b>如果算不出来，可以用手指头或小糖果帮忙哦！每道题填完会自动检查。</div>
  </div>

  <!-- 提交按钮 -->
  <div class="submit-area">
    <button class="submit-btn" id="submitBtn" onclick="checkAnswers()">🔑 提交全部答案</button>
    <br>
    <button class="retry-btn" id="retryBtn" onclick="retry()">🔄 再试一次</button>
  </div>

  <div class="divider">🏆🏆🏆</div>

  <!-- 成就 -->
  <div class="card achievement-card" id="achievement" style="display:none;">
    <span class="medal" id="medal">🏆</span>
    <h2 id="achieveTitle">🎉 恭喜！🎉</h2>
    <div class="cheer" id="achieveText"></div>
    <div class="stars-row" id="starsRow"></div>
  </div>

  <div class="footer" style="text-align:center;font-size:13px;color:rgba(255,255,255,0.7);padding:16px 0;">
    {theme['emoji']} {theme['footer_text']} · 第 {get_week_number(date_obj)} 期 {theme['emoji']}
  </div>

</div>

<script>
const totalQuestions = {total_q};

// 单题即时检查
function checkSingle(input) {{
  const val = input.value.trim();
  if (val === '') {{
    // 清空时恢复默认状态
    input.className = 'answer-input';
    const card = input.closest('.quest-card');
    if (card) card.className = 'quest-card';
    return;
  }}
  const answer = parseInt(input.dataset.answer);
  const userAnswer = parseInt(val);
  if (isNaN(userAnswer)) return;

  const card = input.closest('.quest-card');

  if (userAnswer === answer) {{
    input.className = 'answer-input correct-input';
    if (card) card.className = 'quest-card correct';
    // Show brief feedback
    const fb = card ? card.querySelector('.feedback') : null;
    if (fb) {{
      fb.className = 'feedback show correct-fb';
      fb.textContent = '✅ 答对了！太棒了！🌟';
    }}
  }} else {{
    input.className = 'answer-input wrong-input';
    if (card) card.className = 'quest-card wrong';
    const fb = card ? card.querySelector('.feedback') : null;
    if (fb) {{
      fb.className = 'feedback show wrong-fb';
      fb.textContent = '❌ 不对哦，再想想！正确答案是 ' + answer + '。';
    }}
  }}

  // Update scoreboard live
  updateScoreboard();
}}

function updateScoreboard() {{
  let correct = 0;
  let answered = 0;
  document.querySelectorAll('.answer-input').forEach(input => {{
    if (input.value.trim() !== '') {{
      answered++;
      const answer = parseInt(input.dataset.answer);
      const userAnswer = parseInt(input.value);
      if (userAnswer === answer) correct++;
    }}
  }});
  document.getElementById('correctCount').textContent = correct;
  const statusEl = document.getElementById('scoreStatus');
  if (correct === totalQuestions) {{
    statusEl.textContent = '🎊 全部答对！太厉害了！';
  }} else if (answered > 0) {{
    statusEl.textContent = '已答 ' + answered + ' 题，对 ' + correct + ' 题';
  }}
}}

// 提交按钮统一检查
function checkAnswers() {{
  let correct = 0;
  const questions = [
{questions_js}
  ];

  const encouragements = [
    '答对了！太棒了！🌟', '真聪明！🎉', '太厉害了！⭐', '好棒啊！👏',
    '答对了！继续加油！💪', '正确！你是小天才！✨', '完美！🎊', '厉害！🏆',
    '太对了！给你一个大大的赞！👍', '正确！门打开啦！🚪', '答对了！🌟'
  ];

  questions.forEach((q, i) => {{
    const input = document.getElementById(q.id);
    const card = document.getElementById(q.card);
    const fb = document.getElementById(q.fb);
    const answer = parseInt(input.dataset.answer);
    const userAnswer = parseInt(input.value);

    if (userAnswer === answer) {{
      correct++;
      input.className = 'answer-input correct-input';
      card.className = 'quest-card correct';
      fb.className = 'feedback show correct-fb';
      fb.textContent = '✅ ' + encouragements[i];
    }} else {{
      input.className = 'answer-input wrong-input';
      card.className = 'quest-card wrong';
      fb.className = 'feedback show wrong-fb';
      const label = q.label ? q.label + '：' : '';
      fb.textContent = '❌ ' + label + '正确答案是 ' + answer + '，下次一定能答对！加油 💪';
    }}
  }});

  updateScoreboard();

  // Show achievement
  if (correct === totalQuestions) {{
    showAchievement('full', correct);
  }} else if (correct >= 8) {{
    showAchievement('great', correct);
  }} else if (correct >= 5) {{
    showAchievement('good', correct);
  }} else {{
    showAchievement('try', correct);
  }}

  document.getElementById('submitBtn').style.display = 'none';
  document.getElementById('retryBtn').style.display = 'inline-flex';
}}

function showAchievement(level, correct) {{
  const ach = document.getElementById('achievement');
  ach.style.display = 'block';

  let medal, title, text, stars;
  if (level === 'full') {{
    medal = '👑'; title = '🎊 完美！宝藏找到了！🎊';
    text = '{theme['character']}说："谢谢你帮我找到了{theme['treasure']}！你是最棒的数学魔法师！"{theme['character_emoji']}{theme['treasure_emoji']}';
    stars = '⭐⭐⭐⭐⭐';
    launchConfetti();
  }} else if (level === 'great') {{
    medal = '🥇'; title = '🌟 太厉害了！🌟';
    text = '答对了 ' + correct + ' 题！{theme['character']}说："你太聪明了，马上就能找到宝藏了！"';
    stars = '⭐⭐⭐⭐';
  }} else if (level === 'good') {{
    medal = '🥈'; title = '👍 做得不错！👍';
    text = '答对了 ' + correct + ' 题！再试一次，你会更棒的！';
    stars = '⭐⭐⭐';
  }} else {{
    medal = '🥉'; title = '💪 继续加油！💪';
    text = '答对了 ' + correct + ' 题，没关系，多练习就会越来越厉害的！';
    stars = '⭐⭐';
  }}

  document.getElementById('medal').textContent = medal;
  document.getElementById('achieveTitle').textContent = title;
  document.getElementById('achieveText').innerHTML = text;
  document.getElementById('starsRow').textContent = stars;

  ach.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
}}

function retry() {{
  document.querySelectorAll('.answer-input').forEach(input => {{
    input.value = '';
    input.className = 'answer-input';
  }});
  document.querySelectorAll('.quest-card').forEach(card => {{
    card.className = 'quest-card';
  }});
  document.querySelectorAll('.feedback').forEach(fb => {{
    fb.className = 'feedback';
    fb.textContent = '';
  }});
  document.getElementById('correctCount').textContent = '0';
  document.getElementById('scoreStatus').textContent = '{theme['emoji']} 重新挑战吧！加油 💪';
  document.getElementById('achievement').style.display = 'none';
  document.getElementById('submitBtn').style.display = 'inline-flex';
  document.getElementById('retryBtn').style.display = 'none';
  window.scrollTo({{ top: 0, behavior: 'smooth' }});
}}

function launchConfetti() {{
  const container = document.createElement('div');
  container.className = 'confetti-container';
  document.body.appendChild(container);
  const colors = ['#ff6b6b','#ffd93d','#6bcb77','#4d96ff','#ff6bc6','#845ef7'];
  for (let i = 0; i < 60; i++) {{
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
  setTimeout(() => container.remove(), 5000);
}}
</script>
</body>
</html>"""

    return filename, html


def main():
    target_date = date.today()
    output_dir = None

    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == '--output-dir' and i + 1 < len(args):
            output_dir = args[i + 1]
            i += 2
        else:
            try:
                target_date = date.fromisoformat(args[i])
            except ValueError:
                print(f"Invalid date: {args[i]}. Use YYYY-MM-DD format.")
                sys.exit(1)
            i += 1

    if output_dir is None:
        output_dir = os.path.dirname(os.path.abspath(__file__))

    week = get_week_number(target_date)
    difficulty = get_difficulty_for_week(week)

    # Get theme - weekends use Friday theme as fallback
    weekday = target_date.weekday()
    if weekday > 4:
        print(f"ℹ️  {target_date} is a weekend. Using Friday's theme as fallback.")
        weekday = 4
    theme = THEMES[weekday]

    # Generate questions
    generators = {
        'within_10': generate_questions_within_10,
        'teens_add_no_carry': generate_questions_teens_add_no_carry,
        'teens_sub_no_borrow': generate_questions_teens_sub_no_borrow,
        'carry_add': generate_questions_carry_add,
        'borrow_sub': generate_questions_borrow_sub,
        'mixed': generate_questions_mixed,
    }

    gen_func = generators.get(difficulty, generate_questions_within_10)

    # Use a hash-based seed for better day-to-day variation
    date_str = target_date.isoformat()
    seed_val = int(hashlib.md5(f"math-magic-{date_str}".encode()).hexdigest(), 16) % (2**31)
    random.seed(seed_val)

    # Generate questions (11 to get 10 cards after possible dedup)
    questions = gen_func()[:11]

    # Generate HTML
    filename, html = generate_full_html(target_date, theme, difficulty, questions)

    # Write file
    filepath = os.path.join(output_dir, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"✅ Generated: {filepath}")
    print(f"   Theme: {theme['emoji']} {theme['name']}")
    print(f"   Difficulty: {difficulty}")
    print(f"   Week: {week}")
    print(f"   Questions: 10 cards (12 answer slots)")

    abs_path = os.path.abspath(filepath)
    file_url = f"file://{abs_path}"
    github_url = f"https://solomonhe-hgx.github.io/math-magic/{filename}"
    print(f"\n📎 Local: {file_url}")
    print(f"🌐 GitHub Pages: {github_url}")


if __name__ == '__main__':
    main()
