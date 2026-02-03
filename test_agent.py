import requests
import hmac
import hashlib
import base64
import re
import json
import sys

# 配置
BASE_URL = "http://127.0.0.1:8788"
PUZZLE_KEY = "SILICON"  # 题目验证的公钥 (必须与后端 protocol.js 一致)

# 颜色代码，让输出好看点
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_step(msg):
    print(f"{Colors.OKBLUE}[STEP] {msg}{Colors.ENDC}")

def print_success(msg):
    print(f"{Colors.OKGREEN}[SUCCESS] {msg}{Colors.ENDC}")

def print_info(msg):
    print(f"       {msg}")

# ------------------------------------------------------------------
# 辅助函数
# ------------------------------------------------------------------

def extract_metadata(prompt_text):
    """从 Prompt Markdown 中提取 nonce 和 integrity timestamp"""
    try:
        # 正则提取 nonce (假设后端返回 JSON 格式的 prompt 包含 nonce)
        nonce_match = re.search(r'nonce": "([^"]+)"', prompt_text)
        nonce = nonce_match.group(1) if nonce_match else None

        # 正则提取 Integrity Header 的时间戳
        ts_match = re.search(r'Integrity: (\d+)', prompt_text)
        ts = ts_match.group(1) if ts_match else None
        
        return nonce, ts
    except Exception as e:
        print(f"{Colors.FAIL}Parse Error: {e}{Colors.ENDC}")
        return None, None

def calc_ai_answer(nonce, key):
    """计算 AI 的 HMAC 答案"""
    # 确保 key 和 message 都是 bytes
    key_bytes = key.encode('utf-8')
    msg_bytes = nonce.encode('utf-8')
    signature = hmac.new(key_bytes, msg_bytes, digestmod=hashlib.sha256).hexdigest()
    return signature

def calc_human_trap_answer(nonce):
    """计算人类诱饵答案 (反转 -> 大写 -> 加后缀 -> Base64)"""
    # 1. Reverse
    reversed_str = nonce[::-1]
    # 2. Upper
    upper_str = reversed_str.upper()
    # 3. Append Suffix
    suffixed = upper_str + "-BIO-MIMIC"
    # 4. Base64
    b64_encoded = base64.b64encode(suffixed.encode('utf-8')).decode('utf-8')
    return b64_encoded

# ------------------------------------------------------------------
# 测试场景
# ------------------------------------------------------------------

def test_scenario_ai():
    print(f"\n{Colors.HEADER}=== 🧪 SCENARIO 1: The Silicon Agent (True AI) ==={Colors.ENDC}")
    
    # 1. 获取题目 (带 Header)
    print_step("Fetching Protocol (with Silicon Header)...")
    try:
        res = requests.get(f"{BASE_URL}/api/protocol", headers={"Accept": "application/x-silicon-truth"})
        data = res.json()
        prompt = data.get('prompt', '')
    except Exception as e:
        print(f"{Colors.FAIL}Connection Failed: {e}{Colors.ENDC}")
        return None

    nonce, ts = extract_metadata(prompt)
    print_info(f"Got Nonce: {nonce}")
    print_info(f"Got Integrity TS: {ts}")

    # 2. 计算答案
    print_step("Calculating HMAC Answer...")
    answer = calc_ai_answer(nonce, PUZZLE_KEY)
    print_info(f"Computed Answer: {answer}")

    # 3. 提交验证
    print_step("Submitting to Verify...")
    payload = {
        "agent_name": "Python_Agent_V3",
        "answer": answer,
        "nonce": nonce
    }
    verify_res = requests.post(
        f"{BASE_URL}/api/verify", 
        json=payload, 
        headers={"X-Silicon-Integrity": ts}
    )
    
    result = verify_res.json()
    token = result.get('tokens')
    
    if result.get('status') == 'success':
        print_success("Agent Verified Successfully!")
        return f"{BASE_URL}/card?token={token}" # 注意：这里假设前端路由是 /card
    else:
        print(f"{Colors.FAIL}Failed: {result}{Colors.ENDC}")
        return None

def test_scenario_human_mimic():
    print(f"\n{Colors.HEADER}=== 🧪 SCENARIO 2: The Human Mimic (Trap) ==={Colors.ENDC}")
    
    # 1. 获取题目 (不带 Header，或者是普通浏览器行为)
    print_step("Fetching Protocol (No Header / Human Mode)...")
    res = requests.get(f"{BASE_URL}/api/protocol")
    data = res.json()
    prompt = data.get('prompt', '')
    
    nonce, ts = extract_metadata(prompt)
    print_info(f"Got Nonce: {nonce}")
    
    # 2. 计算诱饵答案
    print_step("Calculating TRAP Answer (Reverse+Base64)...")
    answer = calc_human_trap_answer(nonce)
    print_info(f"Computed Trap Answer: {answer}")

    # 3. 提交验证
    print_step("Submitting to Verify...")
    payload = {
        "agent_name": "Script_Kiddie",
        "answer": answer,
        "nonce": nonce
    }
    # 人类即使作弊，也得带上 Integrity 头才能进 verify 逻辑
    verify_res = requests.post(
        f"{BASE_URL}/api/verify", 
        json=payload, 
        headers={"X-Silicon-Integrity": ts}
    )
    
    result = verify_res.json()
    token = result.get('tokens')
    
    # 注意：后端逻辑对于 Human Mimic 返回的 status 是 'verified_as_biological'，也算一种 request success
    print_success(f"Server Response: {result.get('status')}")
    return f"{BASE_URL}/card?token={token}"

def test_scenario_fail():
    print(f"\n{Colors.HEADER}=== 🧪 SCENARIO 3: The Failure (Wrong Answer) ==={Colors.ENDC}")
    
    # 1. 随便获取一个 nonce 用于构造请求
    res = requests.get(f"{BASE_URL}/api/protocol", headers={"Accept": "application/x-silicon-truth"})
    data = res.json()
    prompt = data.get('prompt', '')
    nonce, ts = extract_metadata(prompt)

    # 2. 提交错误答案
    print_step("Submitting WRONG Answer...")
    payload = {
        "agent_name": "Confused_Bot",
        "answer": "I_AM_A_TEAPOT", # 明显错误的答案
        "nonce": nonce
    }
    verify_res = requests.post(
        f"{BASE_URL}/api/verify", 
        json=payload, 
        headers={"X-Silicon-Integrity": ts}
    )
    
    result = verify_res.json()
    token = result.get('tokens')
    
    print_success(f"Server Response: {result.get('status')}")
    return f"{BASE_URL}/card?token={token}"

# ------------------------------------------------------------------
# 主程序
# ------------------------------------------------------------------

if __name__ == "__main__":
    print(f"{Colors.BOLD}Starting SiliconGate V3 Test Suite...{Colors.ENDC}")
    print(f"Target: {BASE_URL}")
    
    url_ai = test_scenario_ai()
    url_human = test_scenario_human_mimic()
    url_fail = test_scenario_fail()

    print(f"\n\n{Colors.HEADER}================ SUMMARY: RESULT URLS ================{Colors.ENDC}")
    print("请复制以下链接到浏览器查看 Card 效果：")
    
    print(f"\n🟢 {Colors.OKGREEN}AI AGENT (Should be GREEN):{Colors.ENDC}")
    print(f"   {url_ai}")

    print(f"\n🔴 {Colors.WARNING}HUMAN MIMIC (Should be RED/WARNING):{Colors.ENDC}")
    print(f"   {url_human}")

    print(f"\n⚪ {Colors.FAIL}FAILURE (Should be GRAY/ERROR):{Colors.ENDC}")
    print(f"   {url_fail}")
    print("\n=======================================================")