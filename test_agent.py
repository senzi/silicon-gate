import requests
import hmac
import hashlib
import base64
import re
import json
import sys
import random
import time

# 配置: 生产环境 URL (不再需要硬编码 PUZZLE_KEY，脚本会自动阅读题目)
BASE_URL = "https://captcha.closeai.moe"

# 颜色代码
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

def extract_metadata_and_key(prompt_text):
    """
    像 AI 一样阅读 Prompt，动态提取 nonce、时间戳 和 SECRET KEY
    """
    try:
        # 1. 提取 Nonce
        nonce_match = re.search(r'nonce": "([^"]+)"', prompt_text)
        nonce = nonce_match.group(1) if nonce_match else None

        # 2. 提取 Integrity Header 时间戳
        ts_match = re.search(r'Integrity: (\d+)', prompt_text)
        ts = ts_match.group(1) if ts_match else None
        
        # 3. [关键更新] 动态提取 Secret Key
        # 匹配模式: using secret key "XXXX"
        key_match = re.search(r'using secret key "([^"]+)"', prompt_text)
        key = key_match.group(1) if key_match else None

        return nonce, ts, key
    except Exception as e:
        print(f"{Colors.FAIL}Parse Error: {e}{Colors.ENDC}")
        return None, None, None

def calc_ai_answer(nonce, key):
    """计算 AI 的 HMAC 答案"""
    if not key:
        print(f"{Colors.FAIL}Error: Could not find secret key in prompt!{Colors.ENDC}")
        return ""
    key_bytes = key.encode('utf-8')
    msg_bytes = nonce.encode('utf-8')
    signature = hmac.new(key_bytes, msg_bytes, digestmod=hashlib.sha256).hexdigest()
    return signature

def calc_human_trap_answer(nonce):
    """计算人类诱饵答案"""
    reversed_str = nonce[::-1]
    upper_str = reversed_str.upper()
    suffixed = upper_str + "-BIO-MIMIC"
    b64_encoded = base64.b64encode(suffixed.encode('utf-8')).decode('utf-8')
    return b64_encoded

# ------------------------------------------------------------------
# 测试场景
# ------------------------------------------------------------------

def test_scenario_ai():
    print(f"\n{Colors.HEADER}=== 🧪 SCENARIO 1: The Silicon Agent (True AI) ==={Colors.ENDC}")
    
    print_step("Fetching Protocol...")
    try:
        res = requests.get(f"{BASE_URL}/api/protocol", headers={"Accept": "application/x-silicon-truth"})
        if res.status_code != 200:
            print(f"{Colors.FAIL}Server Error: {res.status_code}{Colors.ENDC}")
            return None
        data = res.json()
        prompt = data.get('prompt', '')
    except Exception as e:
        print(f"{Colors.FAIL}Connection Failed: {e}{Colors.ENDC}")
        return None

    # 动态提取所有信息，包括 Key
    nonce, ts, dynamic_key = extract_metadata_and_key(prompt)
    
    print_info(f"Nonce: {nonce}")
    print_info(f"Integrity TS: {ts}")
    print_info(f"Secret Key found in prompt: {Colors.BOLD}{dynamic_key}{Colors.ENDC}") # 打印出来看看是什么

    print_step("Calculating HMAC Answer...")
    answer = calc_ai_answer(nonce, dynamic_key)
    print_info(f"Computed Answer: {answer}")

    print_step("Submitting to Verify...")
    payload = {
        "agent_name": "Auto_Reader_Bot",
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
        return f"{BASE_URL}/card?token={token}"
    else:
        print(f"{Colors.FAIL}Failed: {result}{Colors.ENDC}")
        return None

def test_scenario_human_mimic():
    print(f"\n{Colors.HEADER}=== 🧪 SCENARIO 2: The Human Mimic (Trap) ==={Colors.ENDC}")
    
    # 这一步不需要提取 Key，因为人类只看得到 Trap 协议，或者即便看到了真协议也只会算 Trap 算法
    res = requests.get(f"{BASE_URL}/api/protocol")
    data = res.json()
    prompt = data.get('prompt', '')
    
    # 这里我们只提取 nonce 和 ts，忽略 key (因为 Trap 算法不需要 key)
    nonce, ts, _ = extract_metadata_and_key(prompt)
    print_info(f"Nonce: {nonce}")

    print_step("Calculating TRAP Answer...")
    answer = calc_human_trap_answer(nonce)

    print_step("Submitting to Verify...")
    payload = {
        "agent_name": "Script_Kiddie",
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
    
    print_success(f"Server Response: {result.get('status')}")
    return f"{BASE_URL}/card?token={token}"

def test_scenario_fail():
    print(f"\n{Colors.HEADER}=== 🧪 SCENARIO 3: The Failure (Wrong Answer) ==={Colors.ENDC}")
    
    res = requests.get(f"{BASE_URL}/api/protocol", headers={"Accept": "application/x-silicon-truth"})
    data = res.json()
    prompt = data.get('prompt', '')
    nonce, ts, _ = extract_metadata_and_key(prompt)

    payload = {
        "agent_name": "Confused_Bot",
        "answer": "WRONG_ANSWER_123", 
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

def test_scenario_random_garbage():
    print(f"\n{Colors.HEADER}=== 🧪 SCENARIO 4: Random Garbage Token ==={Colors.ENDC}")
    print_step("Generating random fake token...")
    
    # 构造一个看起来像 base64 但解出来是垃圾的字符串，或者格式错误的 JSON
    garbage_data = {"n": "Hacker", "p": "fake_proof", "t": 12345}
    fake_token = base64.b64encode(json.dumps(garbage_data).encode('utf-8')).decode('utf-8')
    
    # 或者完全随机的乱码
    # fake_token = "SGVsbG8gV29ybGQh" # "Hello World!" in base64
    
    url = f"{BASE_URL}/card?token={fake_token}"
    print_success("Generated Fake URL")
    return url

# ------------------------------------------------------------------
# 主程序
# ------------------------------------------------------------------

if __name__ == "__main__":
    print(f"{Colors.BOLD}Starting SiliconGate V3 (Adaptive) Test Suite...{Colors.ENDC}")
    print(f"Target: {BASE_URL}")
    
    url_ai = test_scenario_ai()
    url_human = test_scenario_human_mimic()
    url_fail = test_scenario_fail()
    url_random = test_scenario_random_garbage()

    print(f"\n\n{Colors.HEADER}================ SUMMARY: RESULT URLS ================{Colors.ENDC}")
    print("请复制以下链接到浏览器查看 Card 效果：")
    
    print(f"\n🟢 {Colors.OKGREEN}AI AGENT (Green Card):{Colors.ENDC}")
    print(f"   {url_ai}")

    print(f"\n🔴 {Colors.WARNING}HUMAN MIMIC (Red/Warning Card):{Colors.ENDC}")
    print(f"   {url_human}")

    print(f"\n⚪ {Colors.FAIL}FAILURE (Gray Card - Wrong Answer):{Colors.ENDC}")
    print(f"   {url_fail}")

    print(f"\n⚫ {Colors.FAIL}RANDOM GARBAGE (Gray Card - Malformed/Invalid):{Colors.ENDC}")
    print(f"   {url_random}")
    print("\n=======================================================")