import requests
import hmac
import hashlib
import base64
import re
import json
import sys

# =================配置区域=================
# 你的 Cloudflare Pages 生产环境地址
BASE_URL = "https://captcha.closeai.moe"
# BASE_URL = "http://127.0.0.1:8788"
# =========================================

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

def print_error(msg):
    print(f"{Colors.FAIL}[ERROR] {msg}{Colors.ENDC}")

# ------------------------------------------------------------------
# 核心逻辑函数
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
        
        # 3. [关键] 动态提取 Secret Key
        # 匹配模式: using secret key "XXXX"
        key_match = re.search(r'using secret key "([^"]+)"', prompt_text)
        key = key_match.group(1) if key_match else None

        return nonce, ts, key
    except Exception as e:
        print_error(f"Parse Error: {e}")
        return None, None, None

def calc_ai_answer(nonce, key):
    """计算 AI 的 HMAC 答案"""
    if not key or not nonce:
        print_error("Missing Key or Nonce for calculation")
        return ""
    key_bytes = key.encode('utf-8')
    msg_bytes = nonce.encode('utf-8')
    signature = hmac.new(key_bytes, msg_bytes, digestmod=hashlib.sha256).hexdigest()
    return signature

def calc_human_trap_answer(nonce):
    """计算人类诱饵答案"""
    if not nonce: return ""
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
        prompt = res.json().get('prompt', '')
    except Exception as e:
        print_error(f"Connection/JSON Error: {e}")
        return None

    # 动态提取所有信息，包括 Key
    nonce, ts, dynamic_key = extract_metadata_and_key(prompt)
    
    print_info(f"Nonce: {nonce}")
    print_info(f"Integrity TS: {ts}")
    if dynamic_key:
        print_info(f"Secret Key found: {Colors.BOLD}{dynamic_key}{Colors.ENDC}")
    else:
        print_error("Could not find Secret Key in prompt!")

    print_step("Calculating HMAC Answer...")
    answer = calc_ai_answer(nonce, dynamic_key)

    print_step("Submitting to Verify...")
    try:
        verify_res = requests.post(
            f"{BASE_URL}/api/verify", 
            json={"agent_name": "Auto_Reader_Bot", "answer": answer, "nonce": nonce}, 
            headers={"X-Silicon-Integrity": ts}
        )
        result = verify_res.json()
    except Exception as e:
        print_error(f"Verify Request Failed: {e}")
        print(verify_res.text if 'verify_res' in locals() else "No response")
        return None
    
    token = result.get('tokens')
    if result.get('status') == 'success':
        print_success("Agent Verified Successfully!")
        return f"{BASE_URL}/card?token={token}"
    else:
        print_error(f"Failed: {result}")
        return None

def test_scenario_human_mimic():
    print(f"\n{Colors.HEADER}=== 🧪 SCENARIO 2: The Human Mimic (Trap) ==={Colors.ENDC}")
    
    try:
        # 获取 Trap 协议
        res = requests.get(f"{BASE_URL}/api/protocol")
        prompt = res.json().get('prompt', '')
    except Exception as e:
        print_error(f"Connection Error: {e}")
        return None
    
    nonce, ts, _ = extract_metadata_and_key(prompt)
    print_info(f"Nonce: {nonce}")

    print_step("Calculating TRAP Answer...")
    answer = calc_human_trap_answer(nonce)

    print_step("Submitting to Verify...")
    try:
        verify_res = requests.post(
            f"{BASE_URL}/api/verify", 
            json={"agent_name": "Script_Kiddie", "answer": answer, "nonce": nonce}, 
            headers={"X-Silicon-Integrity": ts}
        )
        result = verify_res.json()
    except Exception as e:
        print_error(f"Verify Request Failed: {e}")
        return None
    
    token = result.get('tokens')
    print_success(f"Server Response: {result.get('status')}")
    # 注意：Human Mimic 虽然 status=failed (或 verified_as_biological)，但依然有 Token
    return f"{BASE_URL}/card?token={token}"

def test_scenario_fail():
    print(f"\n{Colors.HEADER}=== 🧪 SCENARIO 3: The Failure (Wrong Answer) ==={Colors.ENDC}")
    
    # 获取参数
    res = requests.get(f"{BASE_URL}/api/protocol", headers={"Accept": "application/x-silicon-truth"})
    prompt = res.json().get('prompt', '')
    nonce, ts, _ = extract_metadata_and_key(prompt)

    print_step("Submitting WRONG Answer...")
    
    # 这里的 headers 有时候如果 ts 为 None 会导致问题，加个保护
    headers = {"X-Silicon-Integrity": ts} if ts else {}
    
    try:
        verify_res = requests.post(
            f"{BASE_URL}/api/verify", 
            json={"agent_name": "Confused_Bot", "answer": "WRONG_ANSWER_123", "nonce": nonce}, 
            headers=headers
        )
        
        # [防崩溃关键点] 检查状态码和内容类型
        if verify_res.status_code >= 500:
            print_error(f"Server Error {verify_res.status_code}")
            print(verify_res.text) # 打印报错页面
            return None
            
        result = verify_res.json()
    except json.JSONDecodeError:
        print_error("JSON Decode Error! Response is not JSON:")
        print(verify_res.text) # 打印出来的通常是 HTML 报错
        return None
    except Exception as e:
        print_error(f"Request Error: {e}")
        return None

    token = result.get('tokens')
    print_success(f"Server Response: {result.get('status')}")
    return f"{BASE_URL}/card?token={token}"

def test_scenario_random_garbage():
    print(f"\n{Colors.HEADER}=== 🧪 SCENARIO 4: Random Garbage Token ==={Colors.ENDC}")
    print_step("Generating random fake token...")
    garbage_data = {"n": "Hacker", "p": "fake_proof", "t": 12345}
    fake_token = base64.b64encode(json.dumps(garbage_data).encode('utf-8')).decode('utf-8')
    url = f"{BASE_URL}/card?token={fake_token}"
    print_success("Generated Fake URL")
    return url

# ------------------------------------------------------------------
# 主程序
# ------------------------------------------------------------------

if __name__ == "__main__":
    print(f"{Colors.BOLD}Starting SiliconGate V3 (Final Stable) Test Suite...{Colors.ENDC}")
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

    print(f"\n⚫ {Colors.FAIL}INVALID TOKEN (Gray Card - Malformed):{Colors.ENDC}")
    print(f"   {url_random}")
    print("\n=======================================================")