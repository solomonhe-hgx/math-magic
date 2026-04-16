#!/bin/bash
# 数学魔法师 - 每日自动练习生成脚本
# 根据学习计划自动生成当天的数学练习HTML

set -e

WORKSPACE="/Users/solomon/workspace/QoderWork/math-magic"
TODAY=$(date +%Y-%m-%d)
FILE_NAME="${TODAY}-math-magic.html"
FILE_PATH="${WORKSPACE}/${FILE_NAME}"

# 如果今天已存在则跳过
if [ -f "$FILE_PATH" ]; then
    echo "今日练习已存在: $FILE_NAME"
    exit 0
fi

cd "$WORKSPACE"

# 计算当前是第几周（从2026-04-14开始）
START_DATE="2026-04-14"
START_EPOCH=$(date -j -f "%Y-%m-%d" "$START_DATE" +%s 2>/dev/null || date -d "$START_DATE" +%s)
TODAY_EPOCH=$(date -j -f "%Y-%m-%d" "$TODAY" +%s 2>/dev/null || date -d "$TODAY" +%s)
ELAPSED_DAYS=$(( (TODAY_EPOCH - START_EPOCH) / 86400 ))
CURRENT_WEEK=$(( ELAPSED_DAYS / 7 + 1 ))

# 获取星期几（1=周一, 5=周五）
DAY_OF_WEEK=$(date +%u)

# 主题轮换
case $DAY_OF_WEEK in
    1) THEME_NAME="超市购物"; THEME_EMOJI="🛒"; THEME_ICON1="🛒"; THEME_ICON2="🧺"; THEME_ICON3="💰";;
    2) THEME_NAME="太空探险"; THEME_EMOJI="🚀"; THEME_ICON1="🚀"; THEME_ICON2="🌙"; THEME_ICON3="🛸";;
    3) THEME_NAME="海底世界"; THEME_EMOJI="🌊"; THEME_ICON1="🐠"; THEME_ICON2="🦀"; THEME_ICON3="🐙";;
    4) THEME_NAME="动物园"; THEME_EMOJI="🦁"; THEME_ICON1="🦁"; THEME_ICON2="🐘"; THEME_ICON3="🐼";;
    5) THEME_NAME="魔法城堡"; THEME_EMOJI="🏰"; THEME_ICON1="🧙"; THEME_ICON2="🧚"; THEME_ICON3="🦄";;
    *) THEME_NAME="周末复习"; THEME_EMOJI="📝"; THEME_ICON1="📝"; THEME_ICON2="📝"; THEME_ICON3="📝";;
esac

# 根据周数确定难度
if [ $CURRENT_WEEK -le 2 ]; then
    # 第1-2周：10以内加减法
    DIFFICULTY="10以内加减法"
    PHASE_NAME="10以内加减法复习巩固"
    # 生成10以内加减法题目
    generate_questions() {
        local questions=()
        local ops=("+" "-")
        for i in $(seq 1 10); do
            local op=${ops[$((RANDOM % 2))]}
            if [ "$op" = "+" ]; then
                local a=$((RANDOM % 9 + 1))
                local b=$((RANDOM % (10 - a) + 1))
                local ans=$((a + b))
            else
                local a=$((RANDOM % 9 + 2))
                local b=$((RANDOM % (a - 1) + 1))
                local ans=$((a - b))
            fi
            questions+=("${a} ${op} ${b}")
        done
        echo "${questions[@]}"
    }
elif [ $CURRENT_WEEK -le 4 ]; then
    # 第3-4周：10-20不进位加法
    DIFFICULTY="10-20不进位加法"
    PHASE_NAME="10-20不进位加减法学习"
    generate_questions() {
        local questions=()
        for i in $(seq 1 5); do
            local a=$((RANDOM % 9 + 11))  # 11-19
            local b=$((RANDOM % (19 - a) + 1))
            # 确保不进位：个位相加<=9
            local a_unit=$((a % 10))
            local max_b=$((9 - a_unit))
            if [ $max_b -le 0 ]; then max_b=1; fi
            b=$((RANDOM % max_b + 1))
            local ans=$((a + b))
            questions+=("${a} + ${b}")
        done
        for i in $(seq 6 10); do
            local a=$((RANDOM % 8 + 12))  # 12-19
            local a_unit=$((a % 10))
            local b=$((RANDOM % a_unit + 1))
            local ans=$((a - b))
            questions+=("${a} - ${b}")
        done
        echo "${questions[@]}"
    }
elif [ $CURRENT_WEEK -le 6 ]; then
    # 第5-6周：10-20不退位减法
    DIFFICULTY="10-20不退位减法"
    PHASE_NAME="10-20不退位减法"
    generate_questions() {
        local questions=()
        for i in $(seq 1 5); do
            local a=$((RANDOM % 9 + 11))
            local a_unit=$((a % 10))
            local b=$((RANDOM % a_unit + 1))
            local ans=$((a - b))
            questions+=("${a} - ${b}")
        done
        for i in $(seq 6 10); do
            local a=$((RANDOM % 9 + 11))
            local b=$((RANDOM % 9 + 1))
            local a_unit=$((a % 10))
            local b_unit=$((b % 10))
            if [ $((a_unit + b_unit)) -gt 9 ]; then
                b=$((9 - a_unit))
            fi
            local ans=$((a + b))
            questions+=("${a} + ${b}")
        done
        echo "${questions[@]}"
    }
elif [ $CURRENT_WEEK -le 8 ]; then
    # 第7-8周：20以内进位加法
    DIFFICULTY="20以内进位加法"
    PHASE_NAME="20以内进位加法（凑十法）"
    generate_questions() {
        local questions=()
        for i in $(seq 1 10); do
            local a=$((RANDOM % 9 + 2))
            local b=$((RANDOM % 9 + 2))
            # 确保进位
            local a_unit=$((a % 10))
            local b_unit=$((b % 10))
            if [ $((a_unit + b_unit)) -le 9 ]; then
                b=$((10 - a_unit + RANDOM % 3))
            fi
            if [ $((a + b)) -gt 20 ]; then
                b=$((20 - a))
            fi
            if [ $b -lt 1 ]; then b=1; fi
            local ans=$((a + b))
            questions+=("${a} + ${b}")
        done
        echo "${questions[@]}"
    }
elif [ $CURRENT_WEEK -le 10 ]; then
    # 第9-10周：20以内退位减法
    DIFFICULTY="20以内退位减法"
    PHASE_NAME="20以内退位减法（破十法）"
    generate_questions() {
        local questions=()
        for i in $(seq 1 10); do
            local a=$((RANDOM % 8 + 12))  # 12-19
            local b=$((RANDOM % 9 + 2))
            # 确保退位
            local a_unit=$((a % 10))
            local b_unit=$((b % 10))
            if [ $a_unit -ge $b_unit ]; then
                b=$((a_unit + RANDOM % 3 + 1))
                if [ $b -ge $a ]; then b=$((a - 1)); fi
            fi
            local ans=$((a - b))
            questions+=("${a} - ${b}")
        done
        echo "${questions[@]}"
    }
elif [ $CURRENT_WEEK -le 12 ]; then
    # 第11-12周：混合运算
    DIFFICULTY="20以内加减法混合"
    PHASE_NAME="20以内加减法综合"
    generate_questions() {
        local questions=()
        for i in $(seq 1 10); do
            local a=$((RANDOM % 19 + 2))
            local b=$((RANDOM % 19 + 1))
            if [ $((RANDOM % 2)) -eq 0 ]; then
                local op="+"
                if [ $((a + b)) -gt 20 ]; then b=$((20 - a)); fi
                local ans=$((a + b))
            else
                local op="-"
                if [ $b -ge $a ]; then b=$((a - 1)); fi
                local ans=$((a - b))
            fi
            questions+=("${a} ${op} ${b}")
        done
        echo "${questions[@]}"
    }
else
    # 第13周及以后：100以内计算
    DIFFICULTY="100以内加减法"
    PHASE_NAME="100以内加减法"
    generate_questions() {
        local questions=()
        for i in $(seq 1 10); do
            local a=$((RANDOM % 80 + 10))
            local b=$((RANDOM % 80 + 10))
            if [ $((RANDOM % 2)) -eq 0 ]; then
                local op="+"
                if [ $((a + b)) -gt 100 ]; then b=$((100 - a)); fi
                local ans=$((a + b))
            else
                local op="-"
                if [ $b -ge $a ]; then b=$((a - 1)); fi
                if [ $b -lt 1 ]; then b=1; fi
                local ans=$((a - b))
            fi
            questions+=("${a} ${op} ${b}")
        done
        echo "${questions[@]}"
    }
fi

# 生成题目数组
read -ra Q_ARRAY <<< "$(generate_questions)"

# 构建题目HTML
CORE_QUESTIONS=""
for i in $(seq 0 9); do
    local_q="${Q_ARRAY[$i]}"
    IFS=' ' read -ra parts <<< "$local_q"
    num1="${parts[0]}"
    op="${parts[1]}"
    num2="${parts[2]}"
    ans=$(($num1 $op $num2))
    
    # 场景文字
    case $DAY_OF_WEEK in
        1) scene="${num1}个苹果，又买了${num2}个，一共有几个？"; if [ "$op" = "-" ]; then scene="${num1}个苹果，卖了${num2}个，还剩几个？"; fi;;
        2) scene="${num1}颗星星，又发现${num2}颗，一共几颗？"; if [ "$op" = "-" ]; then scene="${num1}颗流星，飞走了${num2}颗，还剩几颗？"; fi;;
        3) scene="${num1}条小鱼，又来了${num2}条，一共几条？"; if [ "$op" = "-" ]; then scene="${num1}条小鱼，游走了${num2}条，还剩几条？"; fi;;
        4) scene="${num1}只小鸟，又飞来${num2}只，一共几只？"; if [ "$op" = "-" ]; then scene="${num1}只小鸟，飞走了${num2}只，还剩几只？"; fi;;
        5) scene="魔法书${num1}页，又学了${num2}页，一共几页？"; if [ "$op" = "-" ]; then scene="魔法书${num1}页，学会了${num2}页，还有几页？"; fi;;
        *) scene="有${num1}个，又来了${num2}个，一共几个？";;
    esac

    CORE_QUESTIONS+="
    <div class=\"question-card\" id=\"core$((i+1))\">
      <div class=\"question-text\">${THEME_EMOJI} ${scene}<input type=\"number\" class=\"answer-input\" data-answer=\"${ans}\" oninput=\"checkAnswer(this)\" onblur=\"checkAnswer(this)\" onkeydown=\"handleEnter(event, this)\"></div>
      <div class=\"feedback\"></div>
    </div>"
done

# 热身题
if [ "$op" = "+" ]; then
    w1_a=$((RANDOM % 9 + 5))
    w1_b=$((RANDOM % (10 - w1_a) + 1))
    w1_ans=$((w1_a + w1_b))
else
    w1_a=$((RANDOM % 8 + 10))
    w1_b=$((RANDOM % 5 + 1))
    w1_ans=$((w1_a - w1_b))
fi
w2_a=$((RANDOM % 9 + 5))
w2_b=$((RANDOM % 5 + 1))
w2_ans=$((w2_a + w2_b))

# 互动挑战
c1_a=$((RANDOM % 9 + 10))
c1_b=$((RANDOM % 5 + 1))
c1_ans=$((c1_a + c1_b))
c2_a=$((RANDOM % 9 + 12))
c2_b=$((RANDOM % 5 + 1))
c2_ans=$((c2_a - c2_b))
c3_a=$((RANDOM % 9 + 10))
c3_b=$((RANDOM % 5 + 1))
c3_ans=$((c3_a + c3_b))
c4_a=$((RANDOM % 9 + 12))
c4_b=$((RANDOM % 5 + 1))
c4_ans=$((c4_a - c4_b))

# 找出最大值
max_ans=$c1_ans
max_name="A"
if [ $c2_ans -gt $max_ans ]; then max_ans=$c2_ans; max_name="B"; fi
if [ $c3_ans -gt $max_ans ]; then max_ans=$c3_ans; max_name="C"; fi
if [ $c4_ans -gt $max_ans ]; then max_ans=$c4_ans; max_name="D"; fi

# 生成完整HTML
cat > "$FILE_PATH" << HTMLEOF
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>${THEME_EMOJI} ${THEME_NAME} - 数学魔法任务 ${TODAY}</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }

  body {
    font-family: "Comic Sans MS", "PingFang SC", "Microsoft YaHei", sans-serif;
    background: linear-gradient(180deg, #0d1b2a 0%, #1b2838 30%, #2d3a5e 60%, #4a5f8a 100%);
    min-height: 100vh;
    padding: 20px;
    color: #fff;
    overflow-x: hidden;
  }

  .container { max-width: 960px; margin: 0 auto; }

  .header {
    text-align: center; margin-bottom: 24px;
    background: rgba(255,255,255,0.1); backdrop-filter: blur(8px);
    border-radius: 24px; padding: 20px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    border: 3px solid rgba(255,255,255,0.2);
  }
  .header h1 { font-size: 32px; margin-bottom: 8px; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }

  .scoreboard {
    display: flex; justify-content: center; align-items: center; gap: 16px;
    font-size: 22px; font-weight: bold;
  }
  .scoreboard .score {
    background: #ffd166; color: #2d3436;
    padding: 8px 24px; border-radius: 16px; min-width: 120px;
  }
  .retry-btn {
    background: #e17055; color: #fff; border: none;
    padding: 10px 24px; border-radius: 16px; font-size: 18px;
    cursor: pointer; transition: transform 0.2s, background 0.2s;
    min-height: 44px; min-width: 44px;
  }
  .retry-btn:hover { background: #d35400; transform: scale(1.05); }
  .retry-btn:active { transform: scale(0.95); }

  .section {
    background: rgba(255,255,255,0.08); backdrop-filter: blur(6px);
    border-radius: 24px; padding: 24px; margin-bottom: 24px;
    box-shadow: 0 4px 16px rgba(0,0,0,0.2);
    border: 2px solid rgba(255,255,255,0.15);
  }
  .section-title {
    font-size: 26px; margin-bottom: 16px; text-align: center;
    text-shadow: 1px 1px 3px rgba(0,0,0,0.3);
  }

  .question-card {
    background: rgba(255,255,255,0.1); border-radius: 16px;
    padding: 16px 20px; margin-bottom: 12px;
    display: flex; align-items: center; justify-content: space-between;
    flex-wrap: wrap; gap: 12px; transition: background 0.3s, transform 0.2s;
  }
  .question-card.correct { background: rgba(81, 207, 102, 0.3); transform: scale(1.01); }
  .question-card.wrong { background: rgba(255, 183, 77, 0.3); }

  .question-text { font-size: 24px; font-weight: bold; flex: 1; min-width: 200px; }

  .answer-input {
    width: 80px; height: 50px; font-size: 26px; text-align: center;
    border: 3px solid #ffd166; border-radius: 14px; outline: none;
    background: #fff; color: #2d3436; font-weight: bold;
    transition: border-color 0.3s, background 0.3s;
    -moz-appearance: textfield;
  }
  .answer-input::-webkit-outer-spin-button,
  .answer-input::-webkit-inner-spin-button { -webkit-appearance: none; margin: 0; }
  .answer-input.correct { border-color: #51cf66; background: #d3f9d8; }
  .answer-input.wrong { border-color: #ffa94d; background: #fff3e0; }

  .feedback { font-size: 22px; min-width: 80px; min-height: 30px; }

  .challenge-question {
    background: rgba(255,255,255,0.1); border-radius: 16px;
    padding: 16px; margin-bottom: 16px;
  }
  .challenge-question p { font-size: 20px; margin-bottom: 12px; }
  .challenge-options { display: flex; flex-wrap: wrap; gap: 10px; justify-content: center; }
  .challenge-option {
    display: inline-flex; align-items: center; justify-content: center;
    background: rgba(255,255,255,0.2); border: 3px solid #ffd166;
    border-radius: 14px; padding: 12px 20px; font-size: 20px; font-weight: bold;
    cursor: pointer; transition: all 0.2s; min-height: 44px; min-width: 44px;
  }
  .challenge-option:hover { background: rgba(255,255,255,0.4); transform: scale(1.05); }
  .challenge-option.correct-choice { background: #51cf66; border-color: #51cf66; color: #fff; }
  .challenge-option.wrong-choice { background: #ef476f; border-color: #ef476f; color: #fff; }

  .achievement { text-align: center; padding: 30px; display: none; }
  .achievement.show { display: block; }
  .achievement h2 { font-size: 36px; margin-bottom: 16px; animation: bounce 0.6s ease infinite alternate; }
  .achievement .badge { font-size: 64px; margin: 16px 0; }
  .achievement p { font-size: 22px; margin-bottom: 8px; }
  @keyframes bounce { from { transform: translateY(0); } to { transform: translateY(-10px); } }

  .confetti-container {
    position: fixed; top: 0; left: 0; right: 0; bottom: 0;
    pointer-events: none; z-index: 999; overflow: hidden;
  }
  .confetti {
    position: absolute; width: 10px; height: 10px; border-radius: 2px;
    animation: fall 2.5s ease-out forwards;
  }
  @keyframes fall {
    0% { transform: translateY(-20px) rotate(0deg); opacity: 1; }
    100% { transform: translateY(100vh) rotate(720deg); opacity: 0; }
  }

  .star {
    position: fixed; color: #fff; opacity: 0.6;
    animation: twinkle 3s ease-in-out infinite alternate; pointer-events: none;
  }
  @keyframes twinkle {
    0% { opacity: 0.3; transform: scale(0.8); }
    100% { opacity: 1; transform: scale(1.2); }
  }

  @media (max-width: 599px) {
    body { padding: 12px; }
    .header h1 { font-size: 24px; }
    .scoreboard { font-size: 18px; gap: 10px; flex-wrap: wrap; }
    .scoreboard .score { padding: 6px 16px; min-width: 100px; }
    .section { padding: 16px; border-radius: 18px; }
    .section-title { font-size: 22px; }
    .question-card { padding: 12px 14px; flex-direction: column; align-items: flex-start; }
    .question-text { font-size: 20px; }
    .answer-input { width: 70px; height: 46px; font-size: 22px; }
    .feedback { font-size: 18px; }
    .challenge-option { font-size: 18px; padding: 10px 16px; }
    .achievement h2 { font-size: 28px; }
    .achievement .badge { font-size: 48px; }
  }
  @media (min-width: 600px) and (max-width: 1023px) { .container { max-width: 700px; } }
  @media (min-width: 1024px) { .container { max-width: 960px; } }
</style>
</head>
<body>

<div id="stars"></div>
<div class="confetti-container" id="confetti-container"></div>

<div class="container">
  <div class="header">
    <h1>${THEME_EMOJI} ${THEME_NAME} ${THEME_EMOJI}</h1>
    <p style="font-size:16px; margin-bottom:12px; opacity:0.85;">数学魔法任务 · ${TODAY} · 第${CURRENT_WEEK}周 · ${DIFFICULTY}</p>
    <div class="scoreboard">
      <span>答对：</span>
      <span class="score" id="score-display">0 / 11</span>
      <button class="retry-btn" id="retry-btn" onclick="retryAll()">🔄 再试一次</button>
    </div>
  </div>

  <!-- 热身 -->
  <div class="section">
    <div class="section-title">🔥 热身小游戏：动动身体算一算（2分钟）</div>
    <p style="text-align:center; font-size:18px; margin-bottom:16px;">站起来！像小探险家一样，边做动作边算题！</p>
    <div style="text-align:center; font-size:18px; margin-bottom:16px; padding:16px; background:rgba(255,255,255,0.1); border-radius:16px;">
      <p style="font-size:22px; margin-bottom:12px;">👋 <strong>第一题：</strong>有 <strong style="color:#ffd166; font-size:26px;">${w1_a}</strong> 个，再去 <strong style="color:#ffd166; font-size:26px;">${w1_b}</strong> 个，一共几个？</p>
      <p style="font-size:16px; opacity:0.8; margin-bottom:12px;">（踮起脚尖，用手指比出答案，然后输入）</p>
      <input type="number" class="answer-input" data-answer="${w1_ans}" oninput="checkAnswer(this)" onblur="checkAnswer(this)" onkeydown="handleEnter(event, this)" style="margin:0 auto; display:block;">
    </div>
    <div style="text-align:center; font-size:18px; padding:16px; background:rgba(255,255,255,0.1); border-radius:16px;">
      <p style="font-size:22px; margin-bottom:12px;">👋 <strong>第二题：</strong>有 <strong style="color:#ffd166; font-size:26px;">${w2_a}</strong> 个，又加 <strong style="color:#ffd166; font-size:26px;">${w2_b}</strong> 个，一共几个？</p>
      <p style="font-size:16px; opacity:0.8; margin-bottom:12px;">（挥动双臂，然后输入答案）</p>
      <input type="number" class="answer-input" data-answer="${w2_ans}" oninput="checkAnswer(this)" onblur="checkAnswer(this)" onkeydown="handleEnter(event, this)" style="margin:0 auto; display:block;">
    </div>
  </div>

  <!-- 核心任务 -->
  <div class="section">
    <div class="section-title">⭐ 今日核心任务：${THEME_NAME}计算（8分钟）</div>
    <p style="text-align:center; font-size:18px; margin-bottom:16px;">${DIFFICULTY} · 帮小朋友算出正确答案吧！</p>
    ${CORE_QUESTIONS}
  </div>

  <!-- 互动挑战 -->
  <div class="section">
    <div class="section-title">🎮 互动挑战：哪个结果最大？（3-5分钟）</div>
    <p style="text-align:center; font-size:18px; margin-bottom:16px;">算出每个式子的结果，选出最大的！</p>

    <div class="challenge-question">
      <p>A. ${c1_a} + ${c1_b} = ?</p>
      <div class="challenge-options">
        <div class="challenge-option" data-value="${c1_ans}" data-correct="$( [ $c1_ans -eq $max_ans ] && echo true || echo false )" onclick="selectChallenge(this, event)">A. ${c1_ans}</div>
      </div>
    </div>

    <div class="challenge-question">
      <p>B. ${c2_a} - ${c2_b} = ?</p>
      <div class="challenge-options">
        <div class="challenge-option" data-value="${c2_ans}" data-correct="$( [ $c2_ans -eq $max_ans ] && echo true || echo false )" onclick="selectChallenge(this, event)">B. ${c2_ans}</div>
      </div>
    </div>

    <div class="challenge-question">
      <p>C. ${c3_a} + ${c3_b} = ?</p>
      <div class="challenge-options">
        <div class="challenge-option" data-value="${c3_ans}" data-correct="$( [ $c3_ans -eq $max_ans ] && echo true || echo false )" onclick="selectChallenge(this, event)">C. ${c3_ans}</div>
      </div>
    </div>

    <div class="challenge-question">
      <p>D. ${c4_a} - ${c4_b} = ?</p>
      <div class="challenge-options">
        <div class="challenge-option" data-value="${c4_ans}" data-correct="$( [ $c4_ans -eq $max_ans ] && echo true || echo false )" onclick="selectChallenge(this, event)">D. ${c4_ans}</div>
      </div>
    </div>

    <p style="text-align:center; font-size:20px; margin:16px 0;">🤔 <strong style="color:#ffd166;">哪个结果最大？选出所有最大的选项！</strong></p>

    <div style="text-align:center;">
      <div class="challenge-option" data-challenge-final="A" onclick="selectFinalAnswer(this, event)">A. ${c1_ans}</div>
      <div class="challenge-option" data-challenge-final="B" onclick="selectFinalAnswer(this, event)">B. ${c2_ans}</div>
      <div class="challenge-option" data-challenge-final="C" onclick="selectFinalAnswer(this, event)">C. ${c3_ans}</div>
      <div class="challenge-option" data-challenge-final="D" onclick="selectFinalAnswer(this, event)">D. ${c4_ans}</div>
    </div>

    <div id="challenge-feedback" style="text-align:center; font-size:20px; min-height:36px; margin-top:16px;"></div>
  </div>

  <!-- 成就 -->
  <div class="section achievement" id="achievement">
    <h2>🎉 太棒了！</h2>
    <div class="badge">🏆${THEME_EMOJI}🌟</div>
    <p>你完成了所有${THEME_NAME}数学魔法任务！</p>
    <p id="achievement-detail"></p>
    <p style="font-size:18px; margin-top:12px; opacity:0.8;">明天继续来探险吧！🎈</p>
  </div>
</div>

<script>
const AudioCtx = window.AudioContext || window.webkitAudioContext;
let audioCtx = null;
function getAudioCtx() { if (!audioCtx) audioCtx = new AudioCtx(); return audioCtx; }

function playCorrectSound() {
  try {
    const ctx = getAudioCtx();
    [523.25, 659.25, 783.99].forEach((f, i) => {
      const o = ctx.createOscillator(), g = ctx.createGain();
      o.type = 'sine'; o.frequency.value = f;
      g.gain.setValueAtTime(0.2, ctx.currentTime + i * 0.1);
      g.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + i * 0.1 + 0.4);
      o.connect(g); g.connect(ctx.destination);
      o.start(ctx.currentTime + i * 0.1); o.stop(ctx.currentTime + i * 0.1 + 0.4);
    });
  } catch(e) {}
}

function playWrongSound() {
  try {
    const ctx = getAudioCtx(), o = ctx.createOscillator(), g = ctx.createGain();
    o.type = 'triangle';
    o.frequency.setValueAtTime(392, ctx.currentTime);
    o.frequency.exponentialRampToValueAtTime(349.23, ctx.currentTime + 0.3);
    g.gain.setValueAtTime(0.2, ctx.currentTime);
    g.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.3);
    o.connect(g); g.connect(ctx.destination); o.start(); o.stop(ctx.currentTime + 0.3);
  } catch(e) {}
}

function launchConfetti() {
  const c = document.getElementById('confetti-container');
  const colors = ['#ff6b6b','#ffd166','#51cf66','#339af0','#cc5de8','#ff922b','#20c997'];
  for (let i = 0; i < 80; i++) {
    const d = document.createElement('div');
    d.className = 'confetti';
    d.style.left = Math.random() * 100 + '%';
    d.style.backgroundColor = colors[Math.floor(Math.random() * colors.length)];
    d.style.animationDelay = Math.random() * 1.5 + 's';
    d.style.animationDuration = (2 + Math.random() * 1.5) + 's';
    d.style.width = (6 + Math.random() * 8) + 'px';
    d.style.height = (6 + Math.random() * 8) + 'px';
    c.appendChild(d);
  }
  setTimeout(() => { c.innerHTML = ''; }, 4000);
}

function createStars() {
  const c = document.getElementById('stars');
  for (let i = 0; i < 20; i++) {
    const s = document.createElement('div');
    s.className = 'star'; s.textContent = '✦';
    s.style.left = Math.random() * 100 + '%';
    s.style.top = Math.random() * 100 + '%';
    s.style.fontSize = (10 + Math.random() * 16) + 'px';
    s.style.animationDelay = Math.random() * 3 + 's';
    s.style.animationDuration = (2 + Math.random() * 3) + 's';
    c.appendChild(s);
  }
}
createStars();

let challengeCorrect = false;
function updateScore() {
  const inputs = document.querySelectorAll('.section:nth-of-type(3) .answer-input');
  let coreCorrect = 0;
  inputs.forEach(i => { if (i.classList.contains('correct')) coreCorrect++; });
  let total = coreCorrect + (challengeCorrect ? 1 : 0);
  document.getElementById('score-display').textContent = total + ' / 11';
  if (coreCorrect === 10 && challengeCorrect) showAchievement();
}

function checkAnswer(input) {
  const userAnswer = parseInt(input.value);
  const correctAnswer = parseInt(input.dataset.answer);
  const card = input.closest('.question-card') || input.closest('div[style*="text-align"]');
  const fbSpan = card ? card.querySelector('.feedback') : null;
  if (isNaN(userAnswer) || input.value === '') {
    input.classList.remove('correct', 'wrong');
    if (card) card.classList.remove('correct', 'wrong');
    if (fbSpan) fbSpan.innerHTML = '';
    updateScore(); return;
  }
  if (userAnswer === correctAnswer) {
    input.classList.remove('wrong'); input.classList.add('correct');
    if (card) { card.classList.remove('wrong'); card.classList.add('correct'); }
    if (fbSpan) fbSpan.innerHTML = '<span style="color:#51cf66;">✅ 太棒了！</span>';
    playCorrectSound();
  } else {
    input.classList.remove('correct'); input.classList.add('wrong');
    if (card) { card.classList.remove('correct'); card.classList.add('wrong'); }
    if (fbSpan) fbSpan.innerHTML = '<span style="color:#ffa94d;">❌ 答案是 ' + correctAnswer + '</span>';
    playWrongSound();
  }
  updateScore();
}

function handleEnter(event, input) {
  if (event.key === 'Enter') {
    event.preventDefault(); checkAnswer(input);
    const allInputs = Array.from(document.querySelectorAll('.answer-input'));
    const idx = allInputs.indexOf(input);
    if (idx < allInputs.length - 1) allInputs[idx + 1].focus();
  }
}

function selectChallenge(el, event) {
  event.stopPropagation();
  const parent = el.closest('.challenge-question');
  const options = parent.querySelectorAll('.challenge-option');
  options.forEach(o => o.classList.remove('selected', 'correct-choice', 'wrong-choice'));
  if (el.dataset.correct === 'true') {
    el.classList.add('correct-choice');
    document.getElementById('challenge-feedback').innerHTML = '<span style="color:#51cf66;">✅ 算对了！</span>';
    playCorrectSound();
  } else {
    el.classList.add('wrong-choice');
    options.forEach(o => { if (o.dataset.correct === 'true') o.classList.add('correct-choice'); });
    document.getElementById('challenge-feedback').innerHTML = '<span style="color:#ffa94d;">❌ 看看正确答案吧！</span>';
    playWrongSound();
  }
}

function selectFinalAnswer(el, event) {
  event.stopPropagation();
  const options = document.querySelectorAll('[data-challenge-final]');
  const selected = el.dataset.challengeFinal;
  options.forEach(o => o.classList.remove('selected', 'correct-choice', 'wrong-choice'));
  // 找出所有最大值
  const maxOptions = Array.from(options).filter(o => {
    const val = parseInt(o.dataset.challengeFinal === 'A' ? '${c1_ans}' : o.dataset.challengeFinal === 'B' ? '${c2_ans}' : o.dataset.challengeFinal === 'C' ? '${c3_ans}' : '${c4_ans}');
    return val === ${max_ans};
  });
  const correctOnes = maxOptions.map(o => o.dataset.challengeFinal);
  if (correctOnes.includes(selected)) {
    el.classList.add('correct-choice');
    options.forEach(o => { if (correctOnes.includes(o.dataset.challengeFinal)) o.classList.add('correct-choice'); });
    document.getElementById('challenge-feedback').innerHTML = '<span style="color:#51cf66;">✅ 太聪明了！</span>';
    challengeCorrect = true; playCorrectSound();
  } else {
    el.classList.add('wrong-choice');
    options.forEach(o => { if (correctOnes.includes(o.dataset.challengeFinal)) o.classList.add('correct-choice'); });
    document.getElementById('challenge-feedback').innerHTML = '<span style="color:#ffa94d;">❌ 再想想哦！</span>';
    challengeCorrect = false; playWrongSound();
  }
  updateScore();
}

function showAchievement() {
  const ach = document.getElementById('achievement');
  if (ach.classList.contains('show')) return;
  ach.classList.add('show');
  document.getElementById('achievement-detail').textContent = '你答对了全部任务，真是数学小达人！';
  launchConfetti();
  try {
    const ctx = getAudioCtx();
    [523.25, 587.33, 659.25, 698.46, 783.99, 880, 987.77, 1046.5].forEach((f, i) => {
      const o = ctx.createOscillator(), g = ctx.createGain();
      o.type = 'sine'; o.frequency.value = f;
      g.gain.setValueAtTime(0.15, ctx.currentTime + i * 0.12);
      g.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + i * 0.12 + 0.3);
      o.connect(g); g.connect(ctx.destination);
      o.start(ctx.currentTime + i * 0.12); o.stop(ctx.currentTime + i * 0.12 + 0.3);
    });
  } catch(e) {}
}

function retryAll() {
  document.querySelectorAll('.answer-input').forEach(i => { i.value = ''; i.classList.remove('correct', 'wrong'); });
  document.querySelectorAll('.feedback').forEach(f => { f.innerHTML = ''; });
  document.querySelectorAll('.question-card').forEach(c => { c.classList.remove('correct', 'wrong'); });
  document.querySelectorAll('.section:nth-of-type(2) div[style*="text-align"]').forEach(d => { d.classList.remove('correct', 'wrong'); });
  document.querySelectorAll('.challenge-option, [data-challenge-final]').forEach(o => { o.classList.remove('selected', 'correct-choice', 'wrong-choice'); });
  document.getElementById('challenge-feedback').innerHTML = '';
  challengeCorrect = false; updateScore();
  document.getElementById('achievement').classList.remove('show');
  const first = document.querySelector('.answer-input');
  if (first) first.focus();
}

updateScore();
</script>
</body>
</html>
HTMLEOF

echo "✅ 已生成: $FILE_NAME"

# 提交到GitHub
cd "$WORKSPACE"
git add -f "$FILE_NAME"
git commit -m "每日数学练习自动生成: $TODAY $THEME_NAME 第${CURRENT_WEEK}周 ${DIFFICULTY}"
git push origin main

echo "✅ 已推送到GitHub"
