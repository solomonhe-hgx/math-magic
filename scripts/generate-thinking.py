#!/usr/bin/env python3
"""
Math Thinking - Daily Thinking Training HTML Generator

Generates standalone HTML thinking training pages for a 5-year-old,
complementing the daily math practice. Targets 上海实验小学幼升小 exam prep.

Usage:
    python3 generate-thinking.py [date] [--output-dir DIR]
"""

import sys
import os
import json
import random
import hashlib
from datetime import date

HISTORY_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '..', 'question-history.json')

def load_history():
    """Load question history for deduplication."""
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return {"used_questions": {"thinking": {}}, "last_date": ""}

def save_history(history):
    """Save question history."""
    os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

def hash_question(q):
    """Generate a unique hash for a question."""
    key_parts = []
    if 'equation' in q:
        key_parts.append(('equation', q['equation']))
    if 'scene' in q:
        key_parts.append(('scene', q['scene']))
    if 'question' in q:
        key_parts.append(('question', q['question']))
    if 'answer' in q:
        key_parts.append(('answer', str(q['answer'])))
    if 'options' in q:
        key_parts.append(('options', str(q['options'])))
    raw = json.dumps(key_parts, ensure_ascii=False, sort_keys=True)
    return hashlib.md5(raw.encode('utf-8')).hexdigest()

START_DATE = date(2026, 4, 14)

def date_based_seed(d):
    """Generate a richer date-based seed with more entropy per day."""
    return int(hashlib.md5(f"thinking-{d.isoformat()}".encode()).hexdigest(), 16) % (2**31)

THEMES = {
    0: {'name': '超市购物', 'emoji': '🛒'},
    1: {'name': '太空探险', 'emoji': '🚀'},
    2: {'name': '海底世界', 'emoji': '🌊'},
    3: {'name': '动物园', 'emoji': '🦁'},
    4: {'name': '魔法城堡', 'emoji': '🏰'},
}

WEEKDAY_ZH = ['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日']

def get_week_number(d):
    delta = (d - START_DATE).days
    return max(1, (delta // 7) + 1)

def get_difficulty(week):
    if week <= 2: return 'week1_2'
    elif week <= 4: return 'week3_4'
    elif week <= 6: return 'week5_6'
    elif week <= 8: return 'week7_8'
    elif week <= 10: return 'week9_10'
    elif week <= 12: return 'week11_12'
    else: return 'week13_plus'

# ============ Dynamic Question Templates ============

# Word problem scene pools — diverse scenarios, completely different from Math Magic
# Math Magic uses: space/ocean fantasy items (火箭模型/太空种子/银河鱼)
# Math Thinking uses: real-life everyday objects (food, transport, sports, nature, etc.)
WORD_PROBLEM_SCENES = {
    'add_then_sub': [
        # Food & kitchen
        ('妈妈做了 {base} 个饺子🥟', '家人吃了 {sub} 个', '妈妈又做了 {add} 个', '现在盘子里有几个饺子？'),
        ('烤箱里有 {base} 块蛋糕🎂', '拿走了 {sub} 块', '又烤了 {add} 块', '烤箱里有几块蛋糕？'),
        ('碗里有 {base} 个汤圆🥣', '吃了 {sub} 个', '妈妈又盛了 {add} 个', '现在碗里有几个汤圆？'),
        ('桌上有 {base} 个包子🫓', '吃了 {sub} 个', '奶奶又蒸了 {add} 个', '桌上有几个包子？'),
        ('锅里有 {base} 个粽子🫔', '早上吃了 {sub} 个', '中午又煮了 {add} 个', '锅里有几个粽子？'),
        # Transport
        ('公交车上有 {base} 个人 🚌', '到站下了 {sub} 个人', '又上来了 {add} 个人', '现在车上有几个人？'),
        ('地铁站台有 {base} 个人 🚇', '走了 {sub} 个人', '又来了一群人 {add} 个', '现在站台上有几个人？'),
        ('火车上有 {base} 个乘客 🚄', '下车了 {sub} 个', '又上车 {add} 个', '火车上有几个乘客？'),
        # Sports
        ('操场上有 {base} 个足球 ⚽', '被踢走了 {sub} 个', '又拿来 {add} 个', '现在操场上还有几个足球？'),
        ('体育馆有 {base} 个篮球 🏀', '借走了 {sub} 个', '又买来 {add} 个', '现在体育馆有几个篮球？'),
        ('体育器材室有 {base} 根跳绳 🪢', '坏了 {sub} 根', '又买了 {add} 根', '现在有几根跳绳？'),
        # Nature
        ('花园里有 {base} 只蝴蝶 🦋', '飞走了 {sub} 只', '又飞来 {add} 只', '现在花园里有几只蝴蝶？'),
        ('草地上有 {base} 只兔子 🐇', '跑了 {sub} 只', '又来了 {add} 只', '现在草地上有几只兔子？'),
        ('池塘里有 {base} 只鸭子 🦆', '游走了 {sub} 只', '又来了 {add} 只', '现在池塘里有几只鸭子？'),
        ('树枝上有 {base} 只小鸟 🐦', '飞走了 {sub} 只', '又飞来 {add} 只', '树上有几只小鸟？'),
        # Shopping
        ('商店货架上有 {base} 瓶牛奶 🥛', '卖掉了 {sub} 瓶', '又补货 {add} 瓶', '现在货架上有几瓶牛奶？'),
        ('购物车里有 {base} 件商品 🛒', '退回了 {sub} 件', '又放了 {add} 件', '现在购物车里有几件商品？'),
        ('水果摊有 {base} 个西瓜 🍉', '卖掉了 {sub} 个', '又运来 {add} 个', '水果摊有几个西瓜？'),
    ],
    'sub_then_add': [
        # Food
        ('冰箱里有 {base} 个鸡蛋 🥚', '用了 {sub} 个做蛋糕', '又买了 {add} 个', '现在冰箱里有几个鸡蛋？'),
        ('水果盘里有 {base} 个香蕉 🍌', '吃了 {sub} 个', '妈妈又买了 {add} 个', '现在盘子里有几个香蕉？'),
        ('橱柜里有 {base} 个苹果 🍎', '吃了 {sub} 个', '爸爸又买了 {add} 个', '橱柜里有几个苹果？'),
        ('冰箱里有 {base} 瓶可乐 🥤', '喝了 {sub} 瓶', '妈妈又买了 {add} 瓶', '现在有几瓶可乐？'),
        # Nature
        ('花丛里有 {base} 只蜜蜂 🐝', '飞走了 {sub} 只', '又来了 {add} 只', '现在花丛里有几只蜜蜂？'),
        ('河里有 {base} 条鱼 🐟', '游走了 {sub} 条', '又游来 {add} 条', '现在河里有几条鱼？'),
        # Daily life
        ('书架上有 {base} 本书 📚', '借走了 {sub} 本', '还回来 {add} 本', '现在书架上有几本书？'),
        ('停车场有 {base} 辆车 🚗', '开走了 {sub} 辆', '又来了 {add} 辆', '现在停车场有几辆车？'),
        # Animals
        ('鸡窝里有 {base} 个鸡蛋 🐔', '拿走了 {sub} 个', '母鸡又下了 {add} 个', '现在鸡窝里有几个蛋？'),
        ('猫窝里有 {base} 条小鱼干 🐱', '小猫吃了 {sub} 条', '主人又放了 {add} 条', '现在猫窝里有几条鱼干？'),
        ('狗窝里有 {base} 根骨头 🦴', '小狗叼走了 {sub} 根', '主人又放了 {add} 根', '现在狗窝里有几根骨头？'),
    ],
    'sub_then_sub': [
        # Food
        ('袋子里有 {base} 个苹果 🍎', '上午吃了 {sub} 个', '下午吃了 {extra} 个', '袋子里还剩几个苹果？'),
        ('罐子里有 {base} 块巧克力 🍫', '小明吃了 {sub} 块', '小红吃了 {extra} 块', '罐子里还剩几块巧克力？'),
        ('盘子里有 {base} 块西瓜 🍉', '弟弟吃了 {sub} 块', '妹妹吃了 {extra} 块', '还剩几块西瓜？'),
        ('锅里有 {base} 个汤圆 🥣', '早上吃了 {sub} 个', '中午吃了 {extra} 个', '锅里还剩几个汤圆？'),
        ('餐桌上有 {base} 个橘子 🍊', '爸爸吃了 {sub} 个', '妈妈吃了 {extra} 个', '还剩几个橘子？'),
        ('零食柜有 {base} 包薯片 🥔', '哥哥吃了 {sub} 包', '姐姐吃了 {extra} 包', '零食柜还剩几包薯片？'),
        # Stationery
        ('笔袋里有 {base} 支铅笔 ✏️', '用掉了 {sub} 支', '又丢了 {extra} 支', '笔袋里还剩几支铅笔？'),
        ('书架上有 {base} 本漫画书 📖', '借给同学 {sub} 本', '又借给邻居 {extra} 本', '书架上还剩几本漫画书？'),
        # Toys
        ('玩具箱里有 {base} 个积木 🧱', '拿出来搭房子用了 {sub} 个', '搭桥又用了 {extra} 个', '还剩几个积木？'),
        ('气球架上有 {base} 个气球 🎈', '破了 {sub} 个', '又飞走了 {extra} 个', '还剩几个气球？'),
    ],
    'two_step': [
        # Nature
        ('果园里有 {base} 棵苹果树 🌳', '又种了 {add} 棵', '砍掉了 {sub} 棵老树', '果园里现在有几棵苹果树？'),
        ('花坛里有 {base} 朵玫瑰 🌹', '又开了 {add} 朵', '摘了 {sub} 朵送给老师', '花坛里现在有几朵玫瑰？'),
        # Food
        ('篮子里有 {base} 个鸡蛋 🥚', '母鸡又下了 {add} 个', '拿走了 {sub} 个做菜', '篮子里现在有几个鸡蛋？'),
        ('鱼缸里有 {base} 条金鱼 🐠', '又买了 {add} 条', '送了 {sub} 条给朋友', '鱼缸里有几条金鱼？'),
        # Shopping
        ('玩具店里有 {base} 个小汽车 🚙', '进货了 {add} 个', '卖掉了 {sub} 个', '店里现在有几个小汽车？'),
        # School
        ('教室里有 {base} 张桌子 🪑', '搬来了 {add} 张', '搬走了 {sub} 张旧的', '教室里有几张桌子？'),
        ('图书角有 {base} 本绘本 📕', '同学捐了 {add} 本', '借走了 {sub} 本', '图书角现在有几本绘本？'),
        # Animals
        ('农场里有 {base} 只小鸡 🐥', '又孵了 {add} 只', '送走了 {sub} 只', '农场里有几只小鸡？'),
        ('鸟窝里有 {base} 个鸟蛋 🥚', '又生了 {add} 个', '被风吹走了 {sub} 个', '鸟窝里有几个鸟蛋？'),
        ('羊圈里有 {base} 只小羊 🐑', '出生了 {add} 只', '卖了 {sub} 只', '羊圈里有几只小羊？'),
    ],
    'three_step': [
        # Food
        ('厨房里有 {base} 个番茄 🍅', '做菜用了 {sub} 个', '妈妈又买了 {add} 个', '做汤又用了 {extra} 个', '厨房里现在有几个番茄？'),
        ('冰箱里有 {base} 瓶果汁 🧃', '喝了 {sub} 瓶', '又买了 {add} 瓶', '请客人喝了 {extra} 瓶', '冰箱里有几瓶果汁？'),
        ('袋子里有 {base} 个橘子 🍊', '吃了 {sub} 个', '又买了 {add} 个', '分给朋友 {extra} 个', '袋子里有几个橘子？'),
        # Stationery
        ('文具盒里有 {base} 支彩笔 🖍️', '丢了 {sub} 支', '又买了 {add} 支', '借给同学 {extra} 支', '文具盒里有几支彩笔？'),
        # Nature
        ('花园里有 {base} 朵花 🌻', '枯萎了 {sub} 朵', '又开了 {add} 朵', '摘了 {extra} 朵做花环', '花园里有几朵花？'),
        # Money
        ('存钱罐有 {base} 元钱 💰', '买了零食花了 {sub} 元', '帮妈妈做家务挣了 {add} 元', '买本子花了 {extra} 元', '存钱罐里有几元钱？'),
        ('钱包里有 {base} 元零花钱 💵', '买糖花了 {sub} 元', '奶奶给了 {add} 元', '买气球花了 {extra} 元', '钱包里还剩几元？'),
        # Transport
        ('公交车上有 {base} 个人 🚌', '第一站下了 {sub} 人', '又上了 {add} 人', '第二站下了 {extra} 人', '车上有几个人？'),
    ],
    'money': [
        ('小明有 {base} 元钱 💰', '买文具花了 {sub} 元', '帮妈妈扫地挣了 {extra} 元', '小明现在有几元钱？'),
        ('小红存了 {base} 元钱 🏦', '买冰淇淋花了 {sub} 元', '过年得了 {extra} 元压岁钱', '小红现在有几元钱？'),
        ('钱包里有 {base} 元钱 👛', '买水花了 {sub} 元', '卖废品挣了 {extra} 元', '现在钱包里有几元钱？'),
        ('小明的储蓄罐有 {base} 元 🐷', '捐给灾区 {sub} 元', '卖旧书得了 {extra} 元', '储蓄罐里有几元钱？'),
        ('奶奶给了小明 {base} 元 🧧', '买书花了 {sub} 元', '帮邻居收快递挣了 {extra} 元', '小明现在有几元钱？'),
        ('小明带了 {base} 元去春游 🎒', '买门票花了 {sub} 元', '捡瓶子卖了 {extra} 元', '小明现在有几元钱？'),
        ('小华有 {base} 元零花钱 🪙', '买铅笔花了 {sub} 元', '帮爸爸洗车挣了 {extra} 元', '小华有几元钱？'),
    ],
}

# Logic chain templates — 16 diverse scenarios covering animals, objects, people, sports, etc.
LOGIC_CHAIN_SCENES = [
    {
        'scene': '小猫说："我比小狗大。"<br>小兔说："我比小猫大。"<br>请问：谁最大？',
        'answer': 'c', 'answer_text': '小兔最大',
        'options': [('a', '🐱 小猫'), ('b', '🐶 小狗'), ('c', '🐰 小兔')],
        'tags': ['animal', 'size'],
    },
    {
        'scene': '小明说："我比小红矮。"<br>小华说："我比小明高，但比小红矮。"<br>请问：谁最高？',
        'answer': 'c', 'answer_text': '小红最高',
        'options': [('a', '👦 小明'), ('b', '🧒 小华'), ('c', '👧 小红')],
        'tags': ['height', 'person'],
    },
    {
        'scene': '苹果说："我比梨重。"<br>香蕉说："我比苹果轻。"<br>请问：谁最轻？',
        'answer': 'c', 'answer_text': '香蕉最轻',
        'options': [('a', '🍎 苹果'), ('b', '🍐 梨'), ('c', '🍌 香蕉')],
        'tags': ['weight', 'fruit'],
    },
    {
        'scene': '哥哥说："我比弟弟大3岁。"<br>姐姐说："我比哥哥大2岁。"<br>请问：谁最小？',
        'answer': 'b', 'answer_text': '弟弟最小',
        'options': [('a', '👦 哥哥'), ('b', '👶 弟弟'), ('c', '👧 姐姐')],
        'tags': ['age', 'family'],
    },
    {
        'scene': 'A车说："我比B车跑得快。"<br>C车说："我比A车慢，但比B车快。"<br>请问：谁最慢？',
        'answer': 'b', 'answer_text': 'B车最慢',
        'options': [('a', '🏎️ A车'), ('b', '🚗 B车'), ('c', '🚙 C车')],
        'tags': ['speed', 'vehicle'],
    },
    {
        'scene': '大象说："我比老虎重。"<br>老虎说："我比狮子重。"<br>请问：谁最轻？',
        'answer': 'c', 'answer_text': '狮子最轻',
        'options': [('a', '🐘 大象'), ('b', '🐯 老虎'), ('c', '🦁 狮子')],
        'tags': ['weight', 'animal'],
    },
    {
        'scene': '铅笔说："我比橡皮长。"<br>尺子说："我比铅笔长。"<br>请问：谁最短？',
        'answer': 'b', 'answer_text': '橡皮最短',
        'options': [('a', '✏️ 铅笔'), ('b', '🧹 橡皮'), ('c', '📏 尺子')],
        'tags': ['length', 'stationery'],
    },
    {
        'scene': '西瓜说："我比哈密瓜重。"<br>哈密瓜说："我比南瓜轻。"<br>请问：谁最重？',
        'answer': 'c', 'answer_text': '南瓜最重',
        'options': [('a', '🍉 西瓜'), ('b', '🍈 哈密瓜'), ('c', '🎃 南瓜')],
        'tags': ['weight', 'fruit'],
    },
    {
        'scene': '小猴跳了4下，小兔比小猴少跳1下，<br>小熊比小兔多跳3下。<br>请问：谁跳的次数最少？',
        'answer': 'b', 'answer_text': '小兔最少',
        'options': [('a', '🐵 小猴'), ('b', '🐰 小兔'), ('c', '🐻 小熊')],
        'tags': ['count', 'animal'],
    },
    {
        'scene': '小明跑了5圈操场，小红比小明多跑2圈，<br>小华比小红少跑1圈。<br>请问：谁跑得最多？',
        'answer': 'b', 'answer_text': '小红最多',
        'options': [('a', '👦 小明'), ('b', '👧 小红'), ('c', '🧒 小华')],
        'tags': ['distance', 'person'],
    },
    {
        'scene': '第一天看了5页书📖，第二天比第一天多看3页，<br>第三天比第二天少看2页。<br>请问：哪天看得最多？',
        'answer': 'b', 'answer_text': '第二天最多',
        'options': [('a', '📅 第一天'), ('b', '📅 第二天'), ('c', '📅 第三天')],
        'tags': ['count', 'reading'],
    },
    {
        'scene': '甲班有8个人参加运动会，乙班比甲班少3人，<br>丙班比乙班多5人。<br>请问：哪个班参加的人数最少？',
        'answer': 'b', 'answer_text': '乙班最少',
        'options': [('a', '🏫 甲班'), ('b', '🏫 乙班'), ('c', '🏫 丙班')],
        'tags': ['count', 'school'],
    },
    {
        'scene': '红气球有6个，黄气球比红气球少2个，<br>蓝气球比黄气球多4个。<br>请问：哪种气球最少？',
        'answer': 'b', 'answer_text': '黄气球最少',
        'options': [('a', '🔴 红气球'), ('b', '🟡 黄气球'), ('c', '🔵 蓝气球')],
        'tags': ['count', 'object'],
    },
    {
        'scene': '小猫吃了3条鱼，小狗比小猫多吃2条，<br>小兔比小狗少吃1条。<br>请问：谁吃得最多？',
        'answer': 'b', 'answer_text': '小狗最多',
        'options': [('a', '🐱 小猫'), ('b', '🐶 小狗'), ('c', '🐰 小兔')],
        'tags': ['count', 'animal'],
    },
    {
        'scene': '大树高8米，小树比大树矮3米，<br>中树比小树高2米。<br>请问：哪棵树最高？',
        'answer': 'a', 'answer_text': '大树最高',
        'options': [('a', '🌳 大树'), ('b', '🌲 小树'), ('c', '🌿 中树')],
        'tags': ['height', 'nature'],
    },
    {
        'scene': '火箭飞行需要9秒🚀，飞机比火箭慢3秒，<br>汽车比飞机慢2秒。<br>请问：哪个最快？',
        'answer': 'a', 'answer_text': '火箭最快',
        'options': [('a', '🚀 火箭'), ('b', '✈️ 飞机'), ('c', '🚗 汽车')],
        'tags': ['speed', 'transport'],
    },
]

# Queue problem scenarios — diverse contexts beyond 排队做操
QUEUE_SCENES = [
    ('小朋友们排队上车去春游 🚌', '小明前面有 {front} 个人', '后面有 {back} 个人', '这一队一共有几个小朋友？'),
    ('小朋友们排队买冰淇淋 🍦', '小红前面有 {front} 个人', '后面有 {back} 个人', '排队的一共有几个人？'),
    ('小动物们排队过桥 🌉', '小兔前面有 {front} 个小动物', '后面有 {back} 个小动物', '一共有几个小动物？'),
    ('小朋友们排队滑滑梯 🎢', '小华前面有 {front} 个人', '后面有 {back} 个人', '排队的一共有几个小朋友？'),
    ('小朋友们排队进电影院 🎬', '小明前面有 {front} 个人', '后面有 {back} 个人', '这一队一共有几个人？'),
    ('小动物们排队领礼物 🎁', '小熊前面有 {front} 个动物', '后面有 {back} 个动物', '一共有几个动物在排队？'),
    ('小朋们排队等荡秋千 🎠', '小美前面有 {front} 个人', '后面有 {back} 个人', '排队等荡秋千的一共有几个人？'),
    ('小朋友们排队领新书 📚', '小刚前面有 {front} 个人', '后面有 {back} 个人', '这一队一共有几个小朋友？'),
    ('小動物们排队洗澡 🛁', '小鸭前面有 {front} 个动物', '后面有 {back} 个动物', '一共有几个小动物在排队？'),
]

# Q12 alternative question types — rotate beyond just queue problems
Q12_ALTERNATIVES = {
    'age': [
        ('小明今年 {base} 岁 🎂', '小红比小明大 {diff} 岁', '小红今年几岁？'),
        ('妈妈今年 {base} 岁 👩', '小明比妈妈小 {diff} 岁', '小明今年几岁？'),
        ('爷爷今年 {base} 岁 👴', '奶奶比爷爷小 {diff} 岁', '奶奶今年几岁？'),
        ('哥哥今年 {base} 岁 🧑', '弟弟比哥哥小 {diff} 岁', '弟弟今年几岁？'),
    ],
    'floor': [
        ('小明家住在第 {base} 层 🏢', '小红家比小明家高 {diff} 层', '小红家住在第几层？'),
        ('小红从第 {base} 层开始上楼 🏠', '又爬了 {diff} 层', '现在小红在第几层？'),
        ('小明从第 {base} 层开始下楼 🏗️', '下了 {diff} 层', '现在小明在第几层？'),
    ],
    'time': [
        ('现在时钟指向 {base} 点 🕐', '过了 {diff} 个小时', '现在是几点？'),
        ('小明 {base} 点开始写作业 ✏️', '写了 {diff} 个小时', '几点写完的？'),
        ('电影 {base} 点开始 🎬', '还有 {diff} 小时开场', '现在是几点？'),
    ],
    'money': [
        ('小明有 {base} 元钱 💰', '买文具花了 {diff} 元', '还剩几元钱？'),
        ('小红有 {base} 元钱 🪙', '妈妈又给了她 {diff} 元', '现在有几元钱？'),
        ('存钱罐里有 {base} 元钱 🏦', '小明放进去 {diff} 元', '现在存钱罐里有几元？'),
    ],
    'distance': [
        ('小明走了 {base} 步 🚶', '又走了 {diff} 步', '一共走了几步？'),
        ('小红跑了 {base} 米 🏃', '又跑了 {diff} 米', '一共跑了几米？'),
        ('从家到学校有 {base} 米 🏫', '小明已经走了 {diff} 米', '还剩几米？'),
    ],
    'book': [
        ('一本书有 {base} 页 📖', '小明看了 {diff} 页', '还剩几页没看？'),
        ('书架上有 {base} 本书 📚', '又放上去 {diff} 本', '现在书架上有几本书？'),
        ('小明借了 {base} 本书 📕', '还了 {diff} 本', '还有几本书没还？'),
    ],
}


def gen_q12_varied(title, front_min, front_max, back_min, back_max, use_queue=None):
    """Q12 generator that rotates between queue problems and other types.
    use_queue: True/False to force queue or not. None means auto-rotate based on date hash.
    """
    # Determine if we should use a queue problem this time
    if use_queue is None:
        # Use a hash of the current date to decide — roughly 50% queue, 50% other
        use_queue = random.random() < 0.5

    if use_queue:
        return gen_queue_problem_from_pool(title, front_min, front_max, back_min, back_max)

    # Pick an alternative type
    alt_type = random.choice(list(Q12_ALTERNATIVES.keys()))
    pool = Q12_ALTERNATIVES[alt_type]
    tpl = random.choice(pool)

    if alt_type == 'age':
        base = random.randint(5, 12)
        diff = random.randint(1, 5)
        if '大' in tpl[1]:
            answer = base + diff
        else:
            answer = base - diff
    elif alt_type == 'floor':
        base = random.randint(3, 15)
        diff = random.randint(1, 5)
        if '高' in tpl[1] or '爬' in tpl[1]:
            answer = base + diff
        else:
            answer = base - diff
    elif alt_type == 'time':
        base = random.randint(1, 10)
        diff = random.randint(1, 4)
        if '过' in tpl[1] or '写了' in tpl[1]:
            answer = base + diff
        else:
            answer = base - diff
    elif alt_type == 'money':
        base = random.randint(5, 15)
        diff = random.randint(1, 5)
        if '花了' in tpl[1]:
            answer = base - diff
        else:
            answer = base + diff
    elif alt_type == 'distance':
        base = random.randint(10, 30)
        diff = random.randint(1, 10)
        if '又' in tpl[1]:
            answer = base + diff
        else:
            answer = base - diff
    elif alt_type == 'book':
        base = random.randint(5, 15)
        diff = random.randint(1, 5)
        if '看了' in tpl[1] or '还了' in tpl[1]:
            answer = base - diff
        else:
            answer = base + diff
    else:
        base = random.randint(5, 15)
        diff = random.randint(1, 5)
        answer = base + diff

    scene = tpl[0].format(base=base, diff=diff)
    action = tpl[1].format(base=base, diff=diff)
    question = tpl[2]

    return {
        'type': 'fill', 'title': title,
        'scene': f'{scene}<br>{action}',
        'question': question,
        'answer': answer,
    }

# Color pattern templates — vary the emojis per day
COLOR_PATTERN_TEMPLATES = {
    'ABA': [
        {'seq': ['🔵', '🔴', '🔵', '🔵', '🔴', '🔵', '🔵'], 'answer': 'a', 'answer_text': '🔵 蓝色',
         'options': [('a', '🔵 蓝色'), ('b', '🔴 红色'), ('c', '🟢 绿色')]},
        {'seq': ['🟡', '🔴', '🟡', '🟡', '🔴', '🟡', '🟡'], 'answer': 'a', 'answer_text': '🟡 黄色',
         'options': [('a', '🟡 黄色'), ('b', '🔴 红色'), ('c', '🔵 蓝色')]},
        {'seq': ['🌸', '🌺', '🌸', '🌸', '🌺', '🌸', '🌸'], 'answer': 'a', 'answer_text': '🌸 粉色花',
         'options': [('a', '🌸 粉色花'), ('b', '🌺 红色花'), ('c', '🌼 黄色花')]},
    ],
    'AABB': [
        {'seq': ['🔵', '🔵', '🔴', '🔴', '🔵', '🔵'], 'answer': 'a', 'answer_text': '🔴 红色',
         'options': [('a', '🔴 红色'), ('b', '🔵 蓝色'), ('c', '🟡 黄色')]},
        {'seq': ['🟢', '🟢', '🟡', '🟡', '🟢', '🟢'], 'answer': 'a', 'answer_text': '🟡 黄色',
         'options': [('a', '🟡 黄色'), ('b', '🟢 绿色'), ('c', '🔴 红色')]},
        {'seq': ['🍎', '🍎', '🍊', '🍊', '🍎', '🍎'], 'answer': 'a', 'answer_text': '🍊 橘子',
         'options': [('a', '🍊 橘子'), ('b', '🍎 苹果'), ('c', '🍇 葡萄')]},
    ],
    'ABC': [
        {'seq': ['🔵', '🔴', '🟢', '🔵', '🔴', '🟢'], 'answer': 'a', 'answer_text': '🔵 蓝色',
         'options': [('a', '🔵 蓝色'), ('b', '🔴 红色'), ('c', '🟢 绿色')]},
        {'seq': ['⭐', '🌙', '☀️', '⭐', '🌙', '☀️'], 'answer': 'a', 'answer_text': '⭐ 星星',
         'options': [('a', '⭐ 星星'), ('b', '🌙 月亮'), ('c', '☀️ 太阳')]},
        {'seq': ['🐱', '🐶', '🐰', '🐱', '🐶', '🐰'], 'answer': 'a', 'answer_text': '🐱 小猫',
         'options': [('a', '🐱 小猫'), ('b', '🐶 小狗'), ('c', '🐰 小兔')]},
    ],
    'ABAB': [
        {'seq': ['🔵', '🔴', '🔵', '🔴', '🔵'], 'answer': 'b', 'answer_text': '🔴 红色',
         'options': [('a', '🔵 蓝色'), ('b', '🔴 红色'), ('c', '🟡 黄色')]},
        {'seq': ['🌞', '🌜', '🌞', '🌜', '🌞'], 'answer': 'b', 'answer_text': '🌜 月亮',
         'options': [('a', '🌞 太阳'), ('b', '🌜 月亮'), ('c', '⭐ 星星')]},
        {'seq': ['🍓', '🍇', '🍓', '🍇', '🍓'], 'answer': 'b', 'answer_text': '🍇 葡萄',
         'options': [('a', '🍓 草莓'), ('b', '🍇 葡萄'), ('c', '🍊 橘子')]},
    ],
    'AABC': [
        {'seq': ['🔵', '🔵', '🔴', '🟢', '🔵', '🔵'], 'answer': 'a', 'answer_text': '🔴 红色',
         'options': [('a', '🔴 红色'), ('b', '🔵 蓝色'), ('c', '🟢 绿色')]},
        {'seq': ['🌻', '🌻', '🌹', '🌼', '🌻', '🌻'], 'answer': 'a', 'answer_text': '🌹 玫瑰',
         'options': [('a', '🌹 玫瑰'), ('b', '🌻 向日葵'), ('c', '🌼 雏菊')]},
    ],
    'complex': [
        {'seq': ['🔵', '🔴', '🟢', '🔵', '🔴', '🟢', '🔵'], 'answer': 'a', 'answer_text': '🔴 红色',
         'options': [('a', '🔴 红色'), ('b', '🔵 蓝色'), ('c', '🟢 绿色')]},
        {'seq': ['🐟', '🐠', '🐡', '🐟', '🐠', '🐡', '🐟'], 'answer': 'a', 'answer_text': '🐠 小鱼',
         'options': [('a', '🐠 小鱼'), ('b', '🐟 大鱼'), ('c', '🐡 河豚')]},
    ],
}

# Shape emojis for count questions
SHAPE_EMOJIS = ['⭐', '🔵', '🔺', '💎', '🌟', '🔷', '🔶', '🟣', '🟡', '🔴', '🌸', '🍎', '🐟', '🦋', '🐞']

# ============ Question Generators by Difficulty ============

def generate_week1_2():
    """Week 1-2: 基础口算、比大小、简单规律"""
    # Random word problem numbers within 10
    b_base = random.randint(6, 10)
    b_sub = random.randint(1, 3)
    b_add = random.randint(1, 3)
    return {
        'q1': gen_fill('快速口算', 'a + b', 5, 9, 3, 9, '10以内'),
        'q2': gen_fill('快速口算', 'a - b', 5, 10, 1, 4, '10以内'),
        'q3': gen_compare('比一比', 'a + b', 'c', 3, 7, 5, 12),
        'q4': gen_pattern('找规律填数', 'increasing_diff', 2, 4),
        'q5': gen_color_pattern('图形找规律', random.choice(['ABA', 'AABB', 'ABC'])),
        'q6': gen_logic_chain_from_pool('推理链', ['animal', 'height', 'weight']),
        'q7': gen_fill_blank('括号里填几', ['12 + ( ? ) = 18', '3 + ( ? ) = 10', '( ? ) + 5 = 9', '8 - ( ? ) = 3', '( ? ) - 2 = 6']),
        'q8': gen_which_largest('哪个结果最大', ['a+b', 'c-d', 'e+f'],
                               [(6,3), (15,5), (4,3)]),
        'q9': gen_word_problem_from_pool('应用题', random.choice(['add_then_sub', 'sub_then_add']), b_base, b_sub, b_add),
        'q10': gen_fill('连加连减', 'a + b - c', 3, 6, 2, 4, 1, 3),
        'q11': gen_count_shapes('数图形', 6, 10),
        'q12': gen_q12_varied('思维应用题', 2, 4, 3, 5),
    }

def generate_week3_4():
    """Week 3-4: 十几加减、简单推理"""
    b_base = random.randint(10, 15)
    b_sub = random.randint(2, 5)
    b_add = random.randint(1, 4)
    return {
        'q1': gen_fill('快速口算', 'a + b', 11, 16, 1, 3, '不进位'),
        'q2': gen_fill('快速口算', 'a - b', 13, 19, 1, 5, '不退位'),
        'q3': gen_compare('比一比', 'a', 'b', 13, 18, c_min=10, c_max=19),
        'q4': gen_pattern('找规律填数', 'increasing_step', 3, 5),
        'q5': gen_color_pattern('图形找规律', random.choice(['AABB', 'ABC', 'ABAB'])),
        'q6': gen_logic_chain_from_pool('推理链', ['person', 'fruit', 'speed']),
        'q7': gen_fill_blank('括号里填几', ['10 + ( ? ) = 15', '( ? ) + 6 = 17', '18 - ( ? ) = 12', '( ? ) - 3 = 13']),
        'q8': gen_which_largest('哪个结果最大', ['a+b', 'c+d', 'e-f'],
                               [(10,3), (8,4), (18,5)]),
        'q9': gen_word_problem_from_pool('应用题', random.choice(['sub_then_add', 'two_step']), b_base, b_sub, b_add),
        'q10': gen_fill('连加连减', 'a + b - c + d', 3, 5, 1, 3, 1, 3, 1, 3),
        'q11': gen_count_shapes('数图形', 7, 12),
        'q12': gen_q12_varied('思维应用题', 3, 5, 4, 6),
    }

def generate_week5_6():
    """Week 5-6: 逆向思维、排队问题"""
    b_base = random.randint(12, 18)
    b_sub = random.randint(3, 7)
    b_add = random.randint(2, 5)
    return {
        'q1': gen_fill('快速口算', 'a - b', 15, 19, 3, 7, '不退位'),
        'q2': gen_fill('快速口算', 'a + b', 12, 17, 1, 4, '不进位'),
        'q3': gen_compare('比一比', 'a - b', 'c', 15, 19, 3, 7, 10),
        'q4': gen_pattern('找规律填数', 'decreasing', 20, 18),
        'q5': gen_color_pattern('图形找规律', random.choice(['ABC', 'AABC', 'ABAB'])),
        'q6': gen_logic_chain_from_pool('推理链', ['height', 'animal', 'stationery']),
        'q7': gen_fill_blank('括号里填几', ['( ? ) - 5 = 10', '16 - ( ? ) = 11', '( ? ) + 4 = 19', '17 - ( ? ) = 14']),
        'q8': gen_which_largest('哪个结果最大', ['a-b', 'c+d', 'e+f'],
                               [(18,5), (10,4), (7,6)]),
        'q9': gen_word_problem_from_pool('应用题', random.choice(['sub_then_sub', 'two_step']), b_base, b_sub, b_add),
        'q10': gen_fill('连加连减', 'a - b + c + d', 8, 15, 2, 5, 1, 4),
        'q11': gen_count_shapes('数图形', 8, 14),
        'q12': gen_q12_varied('思维应用题', 4, 6, 5, 8),
    }

def generate_week7_8():
    """Week 7-8: 凑十法应用、连加连减"""
    b_base = random.randint(8, 14)
    b_sub = random.randint(2, 5)
    b_add = random.randint(2, 5)
    return {
        'q1': gen_fill('快速口算', 'a + b', 7, 9, 4, 9, '进位'),
        'q2': gen_fill('快速口算', 'a + b', 6, 8, 5, 8, '进位'),
        'q3': gen_compare('比一比', 'a + b', 'c', 8, 9, 4, 6, 14),
        'q4': gen_pattern('找规律填数', 'double_diff', 1, 3),
        'q5': gen_color_pattern('图形找规律', random.choice(['ABAB', 'AABC', 'complex'])),
        'q6': gen_logic_chain_from_pool('推理链', ['weight', 'count', 'reading']),
        'q7': gen_fill_blank('括号里填几', ['9 + ( ? ) = 15', '( ? ) + 8 = 16', '7 + ( ? ) = 14']),
        'q8': gen_which_largest('哪个结果最大', ['a+b', 'c+d', 'e+f'],
                               [(9,5), (8,7), (6,8)]),
        'q9': gen_word_problem_from_pool('应用题', random.choice(['two_step', 'three_step']), b_base, b_sub, b_add),
        'q10': gen_fill('连加连减', 'a + b - c + d - e', 5, 9, 2, 6, 1, 3, 1, 3),
        'q11': gen_count_shapes('数图形', 9, 15),
        'q12': gen_q12_varied('思维应用题', 5, 7, 6, 9),
    }

def generate_week9_10():
    """Week 9-10: 破十法、两步应用题"""
    b_base = random.randint(13, 18)
    b_sub = random.randint(3, 7)
    b_add = random.randint(2, 5)
    return {
        'q1': gen_fill('快速口算', 'a - b', 12, 18, 5, 9, '退位'),
        'q2': gen_fill('快速口算', 'a + b', 8, 9, 5, 8, '进位'),
        'q3': gen_compare('比一比', 'a - b', 'c + d', 15, 18, 7, 9, 5, 6),
        'q4': gen_pattern('找规律填数', 'fib_like', 1, 2),
        'q5': gen_color_pattern('图形找规律', random.choice(['AABC', 'complex', 'ABC'])),
        'q6': gen_logic_chain_from_pool('推理链', ['age', 'distance', 'fruit']),
        'q7': gen_fill_blank('括号里填几', ['( ? ) + 7 = 14', '16 - ( ? ) = 8', '( ? ) - 9 = 5']),
        'q8': gen_which_largest('哪个结果最大', ['a-b', 'c-d', 'e+f'],
                               [(16,8), (14,5), (7,6)]),
        'q9': gen_word_problem_from_pool('应用题', random.choice(['sub_then_sub', 'three_step']), b_base, b_sub, b_add),
        'q10': gen_fill('连加连减', 'a - b - c + d', 15, 19, 3, 6, 2, 5, 1, 4),
        'q11': gen_count_shapes('数图形', 10, 16),
        'q12': gen_q12_varied('思维应用题', 5, 8, 7, 10),
    }

def generate_week11_12():
    """Week 11-12: 综合训练、图形推理"""
    b_base = random.randint(10, 18)
    b_sub = random.randint(2, 6)
    b_add = random.randint(2, 5)
    return {
        'q1': gen_fill('快速口算', 'mixed', 5, 19, 3, 9, '混合'),
        'q2': gen_fill('快速口算', 'mixed', 5, 19, 3, 9, '混合'),
        'q3': gen_compare('比一比', 'a + b - c', 'd', 5, 12, 2, 5, 8),
        'q4': gen_pattern('找规律填数', 'complex', 2, 5),
        'q5': gen_color_pattern('图形找规律', random.choice(['ABAC', 'complex', 'AABB'])),
        'q6': gen_logic_chain_from_pool('推理链', ['multi_condition', 'animal', 'person']),
        'q7': gen_fill_blank('括号里填几', ['( ? ) - 8 = 7', '( ? ) + 9 = 18', '20 - ( ? ) = 13']),
        'q8': gen_which_largest('哪个结果最大', ['a+b-c', 'd-e+f', 'g+h'],
                               [(8,5,3), (15,6,4), (7,6)]),
        'q9': gen_word_problem_from_pool('应用题', random.choice(['three_step', 'money']), b_base, b_sub, b_add),
        'q10': gen_fill('连加连减', 'a + b - c - d + e', 3, 9, 1, 5, 1, 3, 1, 3, 1, 4),
        'q11': gen_count_shapes('数图形', 11, 18),
        'q12': gen_q12_varied('思维应用题', 6, 10, 8, 12),
    }

def generate_week13_plus():
    """Week 13+: 100以内数感"""
    b_base = random.randint(30, 60)
    b_sub = random.randint(10, 20)
    b_add = random.randint(5, 15)
    return {
        'q1': gen_fill('快速口算', 'a + b', 20, 50, 5, 20, '整十'),
        'q2': gen_fill('快速口算', 'a - b', 30, 80, 10, 30, '整十'),
        'q3': gen_compare('比一比', 'a', 'b', 35, 68, '两位数'),
        'q4': gen_pattern('找规律填数', 'step_10', 10, 30),
        'q5': gen_color_pattern('图形找规律', random.choice(['complex', 'AABC', 'ABC'])),
        'q6': gen_logic_chain_from_pool('推理链', ['multi_step', 'weight', 'count']),
        'q7': gen_fill_blank('括号里填几', ['( ? ) + 20 = 55', '80 - ( ? ) = 50', '( ? ) - 30 = 25']),
        'q8': gen_which_largest('哪个结果最大', ['a+b', 'c-d', 'e+f'],
                               [(30,20), (80,30), (25,25)]),
        'q9': gen_word_problem_from_pool('应用题', random.choice(['money', 'two_step']), b_base, b_sub, b_add),
        'q10': gen_fill('连加连减', 'a + b - c', 20, 50, 5, 20, 5, 15),
        'q11': gen_count_shapes('数图形', 15, 25),
        'q12': gen_q12_varied('思维应用题', 8, 15, 10, 20),
    }

# ============ Question Type Generators ============

def gen_fill(title, op, *args):
    """Generate fill-in-the-blank question.
    Args: title, op, then variable args depending on op type.
    For simple a+b or a-b: a_min, a_max, b_min, b_max, hint=''
    For chained a+b-c: a_min, a_max, b_min, b_max, c_min, c_max
    For chained a+b-c+d: a_min,a_max, b_min,b_max, c_min,c_max, d_min,d_max
    """
    if op in ('+', '-', 'mixed'):
        a_min, a_max, b_min, b_max = args[0], args[1], args[2], args[3]
        hint = args[4] if len(args) > 4 else ''
        a = random.randint(a_min, a_max)
        b = random.randint(b_min, b_max)
        if op == '-':
            if b >= a: b = a - 1 if a > 1 else 1
            answer = a - b
            equation = f'{a} － {b}'
        elif op == '+':
            answer = a + b
            equation = f'{a} ＋ {b}'
        else:  # mixed
            if random.random() < 0.5:
                answer = a + b
                equation = f'{a} ＋ {b}'
            else:
                if b >= a: b = a - 1 if a > 1 else 1
                answer = a - b
                equation = f'{a} － {b}'
    elif op == 'a + b - c':
        a_min, a_max, b_min, b_max, c_min, c_max = args
        a = random.randint(a_min, a_max)
        b = random.randint(b_min, b_max)
        c = random.randint(c_min, c_max)
        answer = a + b - c
        equation = f'{a} ＋ {b} － {c}'
    elif op == 'a + b - c + d':
        a_min, a_max, b_min, b_max, c_min, c_max, d_min, d_max = args
        a = random.randint(a_min, a_max)
        b = random.randint(b_min, b_max)
        c = random.randint(c_min, c_max)
        d = random.randint(d_min, d_max)
        answer = a + b - c + d
        equation = f'{a} ＋ {b} － {c} ＋ {d}'
    elif op == 'a - b + c + d':
        a_min, a_max, b_min, b_max, c_min, c_max, d_min, d_max = args
        a = random.randint(a_min, a_max)
        b = random.randint(b_min, b_max)
        c = random.randint(c_min, c_max)
        d = random.randint(d_min, d_max)
        answer = a - b + c + d
        equation = f'{a} － {b} ＋ {c} ＋ {d}'
    elif op == 'a - b - c + d':
        a_min, a_max, b_min, b_max, c_min, c_max, d_min, d_max = args
        a = random.randint(a_min, a_max)
        b = random.randint(b_min, b_max)
        c = random.randint(c_min, c_max)
        d = random.randint(d_min, d_max)
        answer = a - b - c + d
        equation = f'{a} － {b} － {c} ＋ {d}'
    elif op == 'a + b - c - d + e':
        a_min, a_max, b_min, b_max, c_min, c_max, d_min, d_max, e_min, e_max = args
        a = random.randint(a_min, a_max)
        b = random.randint(b_min, b_max)
        c = random.randint(c_min, c_max)
        d = random.randint(d_min, d_max)
        e = random.randint(e_min, e_max)
        answer = a + b - c - d + e
        equation = f'{a} ＋ {b} － {c} － {d} ＋ {e}'
    elif op == 'a + b - c' and len(args) == 6:
        a_min, a_max, b_min, b_max, c_min, c_max = args
        a = random.randint(a_min, a_max)
        b = random.randint(b_min, b_max)
        c = random.randint(c_min, c_max)
        answer = a + b - c
        equation = f'{a} ＋ {b} － {c}'
    else:
        a = random.randint(args[0], args[1])
        b = random.randint(args[2], args[3])
        answer = a + b
        equation = f'{a} ＋ {b}'

    return {'type': 'fill', 'title': title, 'equation': equation, 'answer': answer}

def gen_compare(title, left_op, right_label, a_min, a_max, c_min=None, c_max=None, d_min=None, d_max=None, right_val=None):
    max_attempts = 20
    for _ in range(max_attempts):
        a = random.randint(a_min, a_max)
        if left_op == 'a + b':
            b = random.randint(c_min or 1, c_max or 5)
            left_val = a + b
            left_str = f'{a} + {b}'
        elif left_op == 'a - b':
            b = random.randint(c_min or 1, min(a - 1, c_max or 5))
            left_val = a - b
            left_str = f'{a} - {b}'
        elif left_op == 'a + b - c':
            b = random.randint(d_min or 2, d_max or 5)
            c = random.randint(1, 3)
            left_val = a + b - c
            left_str = f'{a} + {b} - {c}'
        else:
            left_val = a
            left_str = str(a)

        if right_val is not None:
            right_v = right_val
        else:
            right_v = random.randint(c_min or 5, c_max or 12)

        if left_val > right_v:
            answer = 'a'
            answer_text = f'左边大'
            options = [
                ('a', f'左边大'),
                ('b', f'{right_v} 大'),
                ('c', '一样大'),
            ]
        elif left_val < right_v:
            answer = 'b'
            answer_text = f'{right_v} 大'
            options = [
                ('a', f'{left_str} 大'),
                ('b', f'右边大'),
                ('c', '一样大'),
            ]
        else:
            answer = 'c'
            answer_text = '一样大'
            options = [
                ('a', f'{left_str} 大'),
                ('b', f'{right_v} 大'),
                ('c', '一样大'),
            ]
        # Only retry if equal case produces confusing identical labels
        if left_val == right_v:
            # This is fine — options are distinct
            break
        # For unequal cases, options are already distinct
        break

    return {
        'type': 'choice', 'title': title,
        'scene': f'<strong>{left_str}</strong> 和 <strong>{right_v}</strong>，哪个大？',
        'options': options,
        'answer': answer, 'answer_text': answer_text,
    }

def gen_pattern(title, pattern_type, start_min, start_max):
    start = random.randint(start_min, start_max)

    if pattern_type == 'increasing_diff':
        # +2, +3, +4, +5
        seq = [start]
        diff = 2
        for _ in range(3):
            seq.append(seq[-1] + diff)
            diff += 1
        answer = seq[-1] + diff
        explanation = f'规律：依次+2、+3、+4、+{diff}'
    elif pattern_type == 'increasing_step':
        step = random.randint(2, 4)
        seq = [start + i * step for i in range(4)]
        answer = seq[-1] + step
        explanation = f'规律：每次+{step}'
    elif pattern_type == 'decreasing':
        step = random.randint(1, 3)
        seq = [start - i * step for i in range(4)]
        answer = seq[-1] - step
        explanation = f'规律：每次-{step}'
    elif pattern_type == 'double_diff':
        # +2, +4, +6
        seq = [start]
        diff = 2
        for _ in range(3):
            seq.append(seq[-1] + diff)
            diff += 2
        answer = seq[-1] + diff
        explanation = f'规律：依次+2、+4、+6、+{diff}'
    elif pattern_type == 'fib_like':
        # a, b, a+b, a+b+b
        a, b = start, random.randint(start + 1, start + 3)
        seq = [a, b]
        for _ in range(2):
            seq.append(seq[-1] + seq[-2])
        answer = seq[-1] + seq[-2]
        explanation = '规律：前两个数相加等于第三个数'
    elif pattern_type == 'complex':
        step = random.randint(3, 5)
        seq = [start + i * step for i in range(4)]
        answer = seq[-1] + step
        explanation = f'规律：每次+{step}'
    elif pattern_type == 'step_10':
        step = 10
        seq = [start + i * step for i in range(4)]
        answer = seq[-1] + step
        explanation = f'规律：每次+{step}'
    else:
        seq = [start, start+1, start+3, start+6]
        answer = start + 10
        explanation = '规律：差值递增'

    return {
        'type': 'fill', 'title': title,
        'equation': '，'.join(str(x) for x in seq) + '，下一个数是几？',
        'answer': answer,
    }

def gen_color_pattern(title, pattern):
    """Select from a pool of color pattern variants."""
    templates = COLOR_PATTERN_TEMPLATES.get(pattern, COLOR_PATTERN_TEMPLATES['ABA'])
    p = random.choice(templates)
    scene = ' '.join(p['seq']) + ' ❓ 接下来是什么？'
    return {
        'type': 'choice', 'title': title,
        'scene': scene,
        'options': p['options'],
        'answer': p['answer'], 'answer_text': p['answer_text'],
    }

def gen_logic_chain(title, chain_type):
    """Legacy: keep for backward compatibility with old code."""
    return gen_logic_chain_from_pool(title)

def gen_logic_chain_from_pool(title, tags=None):
    """Select a logic chain from the pool, optionally filtered by tags."""
    pool = LOGIC_CHAIN_SCENES
    if tags:
        filtered = [c for c in pool if any(t in c.get('tags', []) for t in tags)]
        if filtered:
            pool = filtered
    c = random.choice(pool)
    return {
        'type': 'choice', 'title': title,
        'scene': c['scene'],
        'options': c['options'],
        'answer': c['answer'], 'answer_text': c['answer_text'],
    }

def _parse_fill_answer(equation):
    """Parse an equation like '12 + ( ? ) = 18' to compute the answer."""
    import re
    m = re.search(r'\(\s*\?\s*\)', equation)
    if not m:
        return None
    # Replace ( ? ) with x and solve
    eq = equation.replace('( ? )', 'x').replace('（ ? ）', 'x').replace(' ', '')
    # Simple pattern: A + x = B or x + A = B or A - x = B or x - A = B
    m = re.match(r'(\d+)\+x=(\d+)', eq)
    if m:
        return int(m.group(2)) - int(m.group(1))
    m = re.match(r'x\+(\d+)=(\d+)', eq)
    if m:
        return int(m.group(2)) - int(m.group(1))
    m = re.match(r'(\d+)-x=(\d+)', eq)
    if m:
        return int(m.group(1)) - int(m.group(2))
    m = re.match(r'x-(\d+)=(\d+)', eq)
    if m:
        return int(m.group(1)) + int(m.group(2))
    return None

def gen_fill_blank(title, equation_or_pool, answer=None):
    """Fill-in-the-blank with dynamic equation generation.
    If answer is None, equation_or_pool is a list of equation strings to pick from.
    Otherwise, equation_or_pool is a single equation string and answer is the answer.
    """
    if answer is None:
        eq = random.choice(equation_or_pool)
        ans = _parse_fill_answer(eq)
        if ans is None:
            ans = 0  # fallback
        return {
            'type': 'fill', 'title': title,
            'equation': eq + '，括号里应该填几？',
            'answer': ans,
        }
    return {
        'type': 'fill', 'title': title,
        'equation': str(equation_or_pool) + '，括号里应该填几？',
        'answer': answer,
    }

# Scene contexts for "which is largest" question
WHICH_LARGEST_SCENES = [
    '算一算，下面哪个算式的结果最大？',
    '比一比，哪个算式的答案最大？',
    '想一想，哪个计算的结果最大？',
    '动脑筋，哪个算式得出的数最大？',
    '快来比一比，下面哪个算出来最大？',
]

def gen_which_largest(title, ops, params):
    """Which expression gives the largest result. Ensures unique maximum."""
    max_attempts = 20
    for _ in range(max_attempts):
        results = []
        labels = []
        for op, p in zip(ops, params):
            if op == 'a+b':
                r = p[0] + p[1]
                label = f'{p[0]} + {p[1]}'
            elif op == 'a-b':
                r = p[0] - p[1]
                label = f'{p[0]} - {p[1]}'
            elif op == 'c+d':
                r = p[0] + p[1]
                label = f'{p[0]} + {p[1]}'
            elif op == 'c-d':
                r = p[0] - p[1]
                label = f'{p[0]} - {p[1]}'
            elif op == 'e+f':
                r = p[0] + p[1]
                label = f'{p[0]} + {p[1]}'
            elif op == 'e-f':
                r = p[0] - p[1]
                label = f'{p[0]} - {p[1]}'
            elif op == 'g+h':
                r = p[0] + p[1]
                label = f'{p[0]} + {p[1]}'
            elif op == 'a+b-c':
                r = p[0] + p[1] - p[2]
                label = f'{p[0]} + {p[1]} - {p[2]}'
            elif op == 'd-e+f':
                r = p[0] - p[1] + p[2]
                label = f'{p[0]} - {p[1]} + {p[2]}'
            else:
                r = p[0] + p[1]
                label = f'{p[0]} + {p[1]}'
            results.append(r)
            labels.append(label)

        max_val = max(results)
        max_count = results.count(max_val)
        if max_count == 1:
            break
        # Regenerate random params to avoid tie
        params = [tuple(random.randint(1, 20) for _ in range(len(p))) for p in params]

    max_idx = results.index(max(results))
    answer = chr(ord('a') + max_idx)

    options = [(chr(ord('a') + i), labels[i]) for i in range(len(labels))]
    scene = random.choice(WHICH_LARGEST_SCENES)

    return {
        'type': 'choice', 'title': title,
        'scene': scene,
        'options': options,
        'answer': answer,
    }

def gen_word_problem(title, problem_type, base, sub, add, extra=None):
    """Legacy: keep for backward compatibility."""
    return gen_word_problem_from_pool(title, problem_type, base, sub, add, extra)

def gen_word_problem_from_pool(title, problem_type, base, sub, add, extra=None):
    """Generate word problems from diverse scenario pools."""
    pool = WORD_PROBLEM_SCENES.get(problem_type, WORD_PROBLEM_SCENES['add_then_sub'])
    scene_tpl = random.choice(pool)
    if extra is None:
        extra = random.randint(1, min(add, sub))

    scene = scene_tpl[0].format(base=base, sub=sub, add=add, extra=extra)
    action = scene_tpl[1].format(base=base, sub=sub, add=add, extra=extra)
    action2 = scene_tpl[2].format(base=base, sub=sub, add=add, extra=extra)
    question = scene_tpl[3]

    if problem_type in ('add_then_sub', 'two_step'):
        answer = base - sub + add
    elif problem_type == 'sub_then_add':
        answer = base - sub + add
    elif problem_type == 'sub_then_sub':
        answer = base - sub - extra
    elif problem_type == 'three_step':
        answer = base - sub + add - extra
    elif problem_type == 'money':
        answer = base - sub + extra
    else:
        answer = base - sub + add

    full_scene = f'{scene}<br>{action}<br>{action2}'

    return {
        'type': 'fill', 'title': title,
        'scene': full_scene, 'question': question,
        'answer': answer,
    }

def gen_count_shapes(title, count_min, count_max):
    """Count shapes with random emoji selection."""
    shape = random.choice(SHAPE_EMOJIS)
    count = random.randint(count_min, count_max)
    shapes = [shape] * count
    random.shuffle(shapes)

    # Generate options
    options = [count]
    while len(options) < 4:
        opt = count + random.randint(-2, 2)
        if opt > 0 and opt not in options:
            options.append(opt)
    options.sort()
    answer_idx = options.index(count)
    answer = chr(ord('a') + answer_idx)

    opt_labels = [f'{x} 个' for x in options]
    opt_keys = [chr(ord('a') + i) for i in range(len(options))]

    return {
        'type': 'choice', 'title': title,
        'scene': f'数一数，下面一共有多少个 {shape} ？',
        'shapes': shapes,
        'options': list(zip(opt_keys, opt_labels)),
        'answer': answer,
    }

def gen_queue_problem(title, front_min, front_max, back_min, back_max):
    """Legacy: keep for backward compatibility."""
    return gen_queue_problem_from_pool(title, front_min, front_max, back_min, back_max)

def gen_queue_problem_from_pool(title, front_min, front_max, back_min, back_max):
    """Queue problems with diverse scenarios (not always 排队做操)."""
    front = random.randint(front_min, front_max)
    back = random.randint(back_min, back_max)
    answer = front + back + 1

    scene_tpl = random.choice(QUEUE_SCENES)
    context = scene_tpl[0]
    front_desc = scene_tpl[1].format(front=front, back=back)
    back_desc = scene_tpl[2].format(front=front, back=back)
    question = scene_tpl[3]

    return {
        'type': 'fill', 'title': title,
        'scene': f'{context}<br>{front_desc}<br>{back_desc}',
        'question': question,
        'answer': answer,
    }

# ============ HTML Generation ============

def format_date_zh(d):
    return f"{d.year}年{d.month}月{d.day}日 · {WEEKDAY_ZH[d.weekday()]}"

def render_question(q, idx):
    num = idx + 1
    qid = f'q{num}'

    if q['type'] == 'fill':
        equation = q.get('equation', '')
        scene = q.get('scene', '')
        question = q.get('question', '')
        title = q.get('title', '')

        # Build scene HTML
        scene_html = ''
        if scene:
            # Queue problems and word problems get scene-box styling
            if '排队' in title or '🍎' in scene or '🐦' in scene or '🍬' in scene or '🌸' in scene or '🍓' in scene or '💰' in scene:
                scene_html = f'<div class="scene-box">{scene}</div>'
            else:
                scene_html = f'<div class="quest-scene">{scene}</div>'

        # Build content based on question type
        if '下一个数' in str(equation):
            # Pattern questions
            content = f'<div class="quest-scene">{equation}</div>'
        elif q.get('scene') and ('：' in str(q.get('equation', '')) or '填几' in str(q.get('equation', ''))):
            content = f'<div class="scene-box">{scene}</div>\n      <div class="quest-scene">{question}</div>'
        elif '排队' in title:
            # Queue problems: show scene + question
            content = f'{scene_html}\n      <div class="quest-scene">{question}</div>'
        elif equation:
            # Regular math problems
            content = f'<div class="quest-row">\n        <span class="quest-math">{equation}</span>\n      </div>'
            if question:
                content += f'\n      <div class="quest-scene">{question}</div>'
        else:
            # Fallback
            content = scene_html

        return f'''    <!-- Q{num} -->
    <div class="quest-card" id="{qid}-card">
      <div class="quest-header"><span class="quest-num">{num}</span><span style="font-weight:700;">{q['title']}</span></div>
{content}
      <div class="quest-row">
        <span class="quest-math">答案是：</span>
        <input type="number" class="answer-input" id="{qid}" data-answer="{q['answer']}" min="0" max="99" inputmode="numeric" autocomplete="off" oninput="checkSingle(this)" onblur="checkSingle(this)">
      </div>
      <div class="feedback" id="{qid}-fb"></div>
    </div>'''

    else:  # choice
        scene = q.get('scene', '')
        shapes = q.get('shapes', [])
        options_html = ''

        if shapes:
            grid_items = ''.join(f'<div class="shape-item">{s}</div>' for s in shapes)
            scene_html = f'<div class="quest-scene">{scene}</div>\n      <div class="shape-grid">\n        {grid_items}\n      </div>'
        else:
            scene_html = f'<div class="quest-scene">{scene}</div>'

        opt_items = ''
        for key, label in q['options']:
            opt_id = f'{qid}-{key}'
            opt_items += f'<div class="option-card"><input type="radio" name="{qid}" id="{opt_id}" value="{key}"><label for="{opt_id}">{label}</label></div>\n        '

        return f'''    <!-- Q{num} -->
    <div class="quest-card" id="{qid}-card">
      <div class="quest-header"><span class="quest-num">{num}</span><span style="font-weight:700;">{q['title']}</span></div>
{scene_html}
      <div class="options-group" id="{qid}-options">
        {opt_items.strip()}
      </div>
      <div class="feedback" id="{qid}-fb"></div>
    </div>'''

def generate_explanations(questions):
    """Generate explanation text for each question."""
    explanations = {}
    for qid, q in questions.items():
        num = qid.replace('q', '')
        if q['type'] == 'fill':
            ans = q['answer']
            eq = q.get('equation', '')
            if '下一个数' in str(eq):
                explanations[qid] = {
                    'ok': f'{ans}！规律找得很准！🎉',
                    'fix': f'仔细观察数列的规律，下一个数是{ans}。',
                }
            elif '括号' in str(eq):
                explanations[qid] = {
                    'ok': f'括号里填{ans}，完全正确！🎉',
                    'fix': f'用逆运算：{eq}，答案是{ans}。',
                }
            elif '连加' in q['title'] or '连减' in q['title']:
                explanations[qid] = {
                    'ok': f'{ans}，从左到右计算正确！🎉',
                    'fix': f'从左到右一步步算，答案是{ans}。',
                }
            elif '排队' in q['title']:
                explanations[qid] = {
                    'ok': f'{ans}人，排队问题理解到位！🎉',
                    'fix': f'前面的人 + 后面的人 + 自己 = 总人数，答案是{ans}。',
                }
            elif '思维应用题' in q['title']:
                explanations[qid] = {
                    'ok': f'答案是{ans}，完全正确！🎉',
                    'fix': f'仔细阅读题目，一步步计算，答案是{ans}。',
                }
            else:
                explanations[qid] = {
                    'ok': f'答对了！太棒了！🎉',
                    'fix': f'正确答案是{ans}。',
                }
        else:
            explanations[qid] = {
                'ok': f'选择正确！{q.get("answer_text", "")}🎉',
                'fix': f'正确答案是：{q.get("answer_text", "")}',
            }
        # Special handling for "which largest" questions
        if q.get('title') == '哪个结果最大':
            correct_label = ''
            for key, label in q.get('options', []):
                if key == q.get('answer'):
                    correct_label = label
                    break
            explanations[qid] = {
                'ok': f'选择正确！{correct_label} 结果最大🎉',
                'fix': f'分别计算三个算式，{correct_label} 的结果最大。',
            }
        # Special handling for count shape questions
        if q.get('title') == '数图形':
            ans = q.get('answer', '')
            explanations[qid] = {
                'ok': f'数对了！一共{ans}个🎉',
                'fix': f'仔细数一数，一共有{ans}个。可以用"划掉法"避免重复。',
            }
    return explanations

def generate_thinking_html(date_obj, theme, questions):
    """Generate complete thinking training HTML."""
    date_str = format_date_zh(date_obj)
    total = len(questions)
    explanations = generate_explanations(questions)

    # Group questions by section
    sections = [
        ('⚡', '脑力热身', '3分钟', ['q1', 'q2', 'q3']),
        ('🧩', '思维训练 A：逻辑推理', '5分钟', ['q4', 'q5', 'q6']),
        ('🔢', '思维训练 B：数感与计算', '5分钟', ['q7', 'q8', 'q9', 'q10']),
        ('👁️', '思维训练 C：空间与观察', '4分钟', ['q11', 'q12']),
    ]

    # Render all questions
    q_htmls = {}
    for qid, q in questions.items():
        idx = int(qid.replace('q', '')) - 1
        q_htmls[qid] = render_question(q, idx)

    # Build sections HTML
    sections_html = ''
    for i, (icon, title, time, qids) in enumerate(sections):
        section_questions = '\n\n'.join(q_htmls[qid] for qid in qids)
        divider = '\n  <div class="divider">🏰🧩🏰</div>\n\n' if i < len(sections) - 1 else ''

        sections_html += f'''  <!-- {title} -->
  <div class="card">
    <h2><span class="icon">{icon}</span> {title} <span class="section-time">⏱ {time}</span></h2>

{section_questions}
  </div>
{divider}'''

    # Answers JSON for JS
    answers_json = {}
    for qid, q in questions.items():
        answers_json[qid] = str(q['answer'])

    explanations_json = {}
    for qid, exp in explanations.items():
        explanations_json[qid] = exp

    # Coach notes
    week = get_week_number(date_obj)
    coach_notes = {
        'week1_2': '⚡ 热身（Q1-Q3）：帮助孩子快速进入数学状态，建立信心。🧩 找规律（Q4-Q6）：引导孩子说出"每次多几"或"循环规律"。🔢 计算（Q7-Q10）：Q7逆运算培养方程意识，Q9应用题训练两步运算。👁️ 空间观察（Q11-Q12）：教孩子用"划掉法"数图形，排队问题核心公式：前面+后面+自己=总人数。',
        'default': '⚡ 热身：帮助孩子快速进入状态。🧩 逻辑推理：鼓励孩子画图理解。🔢 数感计算：注意运算顺序，从左到右。👁️ 空间观察：教孩子有序计数，避免遗漏或重复。',
    }

    html = f"""<!DOCTYPE html>
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
    <div class="score"><span class="correct" id="correctCount">0</span> / <span id="totalCount">{total}</span> 正确</div>
    <div class="progress-mini"><div class="progress-mini-fill" id="progressFill"></div></div>
    <div class="status" id="scoreStatus">{theme['emoji']} 开始思维训练吧！加油 💪</div>
  </div>

  <!-- 标题 -->
  <div class="header">
    <h1>🧠 思维训练营 · 每日冲刺</h1>
    <div class="subtitle">今日主题：{theme['emoji']} <strong>{theme['name']}大冒险</strong></div>
    <div class="date-badge">📅 {date_str}</div>
  </div>

{sections_html}

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
    <p style="font-size:13px;color:var(--text-light);line-height:1.8;">{coach_notes.get(get_difficulty(week), coach_notes['default'])}</p>
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

// 单题即时检查（输入框专用）
function checkSingle(input) {{
  const val = input.value.trim();
  if (val === '') {{
    input.className = 'answer-input';
    const card = input.closest('.quest-card');
    if (card) {{
      card.className = 'quest-card';
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
    if (card) card.className = 'quest-card correct';
    if (fb) {{
      fb.className = 'feedback show correct-fb';
      const data = explanations[qId];
      fb.textContent = '✅ ' + (data ? data.ok : '答对了！太棒了！🌟');
    }}
    playCorrect();
  }} else {{
    input.className = 'answer-input wrong-input';
    if (card) card.className = 'quest-card wrong';
    if (fb) {{
      fb.className = 'feedback show wrong-fb';
      const data = explanations[qId];
      fb.innerHTML = '❌ 不对哦<br>💡 正确答案：' + (data ? data.fix : expected);
    }}
    playWrong();
  }}

  // Update scoreboard
  document.getElementById('correctCount').textContent =
    Array.from(document.querySelectorAll('.answer-input.correct-input')).length;
}}

// ===== 答案 =====
const TOTAL = {total};
let correctCount = 0;
const checked = new Set();

const answers = {json.dumps(answers_json)};

const explanations = {json.dumps(explanations_json, ensure_ascii=False)};

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
  const isCorrect = userAnswer === answers[qId];
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
    if (input) input.className = 'answer-input correct-input';

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
</html>"""

    return html


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
    difficulty = get_difficulty(week)

    # Get theme - weekends use Friday
    weekday = target_date.weekday()
    if weekday > 4:
        weekday = 4
    theme = THEMES[weekday]

    # Load question history for deduplication
    history = load_history()
    if 'thinking' not in history.get('used_questions', {}):
        history.setdefault('used_questions', {})['thinking'] = {}

    # Generate questions with retry on duplicates
    generators = {
        'week1_2': generate_week1_2,
        'week3_4': generate_week3_4,
        'week5_6': generate_week5_6,
        'week7_8': generate_week7_8,
        'week9_10': generate_week9_10,
        'week11_12': generate_week11_12,
        'week13_plus': generate_week13_plus,
    }

    gen_func = generators.get(difficulty, generate_week1_2)
    used_hashes = history['used_questions']['thinking']
    max_retries = 30

    for attempt in range(max_retries):
        seed_val = date_based_seed(target_date) + attempt * 1000
        random.seed(seed_val)
        questions = gen_func()

        # Check for duplicates
        has_duplicate = False
        for qid, q in questions.items():
            h = hash_question(q)
            if h in used_hashes:
                has_duplicate = True
                break
        if not has_duplicate:
            break

    # Record new questions in history
    for qid, q in questions.items():
        h = hash_question(q)
        used_hashes[h] = {'date': target_date.isoformat(), 'qid': qid}

    history['used_questions']['thinking'] = used_hashes
    history['last_date'] = target_date.isoformat()
    save_history(history)

    # Generate HTML
    html = generate_thinking_html(target_date, theme, questions)

    # Write file
    filename = f"{target_date.isoformat()}-math-thinking.html"
    filepath = os.path.join(output_dir, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"✅ Generated: {filepath}")
    print(f"   Theme: {theme['emoji']} {theme['name']}")
    print(f"   Difficulty: {difficulty}")
    print(f"   Week: {week}")
    print(f"   Questions: {len(questions)} (4 sections)")

    abs_path = os.path.abspath(filepath)
    file_url = f"file://{abs_path}"
    github_url = f"https://solomonhe-hgx.github.io/math-magic/{filename}"
    print(f"\n📎 Local: {file_url}")
    print(f"🌐 GitHub Pages: {github_url}")


if __name__ == '__main__':
    main()
